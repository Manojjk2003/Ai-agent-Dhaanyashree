import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  Grid,
  Paper,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";

import { useAuth } from "../../auth/AuthContext";
import {
  ProductInput,
  ProductResponse,
  createProduct,
  deleteProduct,
  listProducts,
  updateProduct,
} from "../../services/api";

const emptyProduct: ProductInput = {
  name: "",
  category: "",
  description: "",
  benefits: [],
  ingredients: [],
  price: null,
  target_audience: [],
  image_url: "",
  is_active: true,
};

function splitList(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function joinList(value: string[]) {
  return value.join(", ");
}

export function ProductsPage() {
  const { getIdToken } = useAuth();
  const [products, setProducts] = useState<ProductResponse[]>([]);
  const [form, setForm] = useState<ProductInput>(emptyProduct);
  const [benefits, setBenefits] = useState("");
  const [ingredients, setIngredients] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const activeCount = useMemo(
    () => products.filter((product) => product.is_active).length,
    [products],
  );

  async function loadProducts() {
    setError(null);
    setLoading(true);

    try {
      const token = await getIdToken();
      setProducts(await listProducts(token));
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not load products");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function resetForm() {
    setEditingId(null);
    setForm(emptyProduct);
    setBenefits("");
    setIngredients("");
    setTargetAudience("");
  }

  function editProduct(product: ProductResponse) {
    setEditingId(product.product_id);
    setForm(product);
    setBenefits(joinList(product.benefits));
    setIngredients(joinList(product.ingredients));
    setTargetAudience(joinList(product.target_audience));
    setSaved(false);
    setError(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSaved(false);
    setSaving(true);

    const payload: ProductInput = {
      ...form,
      benefits: splitList(benefits),
      ingredients: splitList(ingredients),
      target_audience: splitList(targetAudience),
    };

    try {
      const token = await getIdToken();
      if (editingId) {
        await updateProduct(token, editingId, payload);
      } else {
        await createProduct(token, payload);
      }

      resetForm();
      await loadProducts();
      setSaved(true);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not save product");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(productId: string) {
    setError(null);
    setSaved(false);

    try {
      const token = await getIdToken();
      await deleteProduct(token, productId);
      await loadProducts();
      if (editingId === productId) {
        resetForm();
      }
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not delete product");
    }
  }

  return (
    <Stack spacing={3} className="dashboard">
      <Box className="dashboard-header">
        <Stack spacing={1}>
          <Typography variant="overline" color="secondary">
            Product Memory
          </Typography>
          <Typography variant="h1">Products</Typography>
          <Typography color="text.secondary" className="dashboard-subtitle">
            Add the products the marketing agent can promote, compare, and use
            when creating captions, posters, SEO, and campaigns.
          </Typography>
        </Stack>
        <Stack direction="row" spacing={1}>
          <Chip label={`${products.length} total`} />
          <Chip color="success" label={`${activeCount} active`} />
        </Stack>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={5}>
          <Paper className="form-panel">
            <Stack component="form" spacing={2} onSubmit={handleSubmit}>
              <Typography variant="h2">
                {editingId ? "Edit product" : "Add product"}
              </Typography>
              {error ? <Alert severity="error">{error}</Alert> : null}
              {saved ? <Alert severity="success">Product saved.</Alert> : null}
              {loading ? <Alert severity="info">Loading products...</Alert> : null}

              <TextField
                disabled={saving}
                label="Product name"
                onChange={(event) => setForm({ ...form, name: event.target.value })}
                required
                value={form.name}
              />
              <TextField
                disabled={saving}
                label="Category"
                onChange={(event) =>
                  setForm({ ...form, category: event.target.value })
                }
                value={form.category}
              />
              <TextField
                disabled={saving}
                label="Description"
                minRows={3}
                multiline
                onChange={(event) =>
                  setForm({ ...form, description: event.target.value })
                }
                value={form.description}
              />
              <TextField
                disabled={saving}
                helperText="Separate benefits with commas"
                label="Benefits"
                onChange={(event) => setBenefits(event.target.value)}
                value={benefits}
              />
              <TextField
                disabled={saving}
                helperText="Separate ingredients with commas"
                label="Ingredients"
                onChange={(event) => setIngredients(event.target.value)}
                value={ingredients}
              />
              <TextField
                disabled={saving}
                label="Price"
                onChange={(event) =>
                  setForm({
                    ...form,
                    price: event.target.value ? Number(event.target.value) : null,
                  })
                }
                type="number"
                value={form.price ?? ""}
              />
              <TextField
                disabled={saving}
                helperText="Separate audiences with commas"
                label="Target audience"
                onChange={(event) => setTargetAudience(event.target.value)}
                value={targetAudience}
              />
              <TextField
                disabled={saving}
                label="Image URL"
                onChange={(event) =>
                  setForm({ ...form, image_url: event.target.value })
                }
                value={form.image_url}
              />
              <Stack alignItems="center" direction="row" spacing={1}>
                <Switch
                  checked={form.is_active}
                  onChange={(event) =>
                    setForm({ ...form, is_active: event.target.checked })
                  }
                />
                <Typography>Active product</Typography>
              </Stack>
              <Stack direction="row" spacing={1}>
                <Button disabled={saving || loading} type="submit" variant="contained">
                  {editingId ? "Update Product" : "Add Product"}
                </Button>
                {editingId ? (
                  <Button onClick={resetForm} variant="outlined">
                    Cancel
                  </Button>
                ) : null}
              </Stack>
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} md={7}>
          <Stack spacing={2}>
            {products.map((product) => (
              <Paper className="product-card" key={product.product_id}>
                <Stack spacing={1}>
                  <Stack
                    alignItems="flex-start"
                    direction="row"
                    justifyContent="space-between"
                    spacing={2}
                  >
                    <Stack spacing={0.5}>
                      <Typography variant="h2">{product.name}</Typography>
                      <Typography color="text.secondary">
                        {product.category || "No category"}
                        {product.price !== null ? ` | Rs. ${product.price}` : ""}
                      </Typography>
                    </Stack>
                    <Chip
                      color={product.is_active ? "success" : "default"}
                      label={product.is_active ? "Active" : "Inactive"}
                    />
                  </Stack>
                  {product.description ? (
                    <Typography>{product.description}</Typography>
                  ) : null}
                  {product.benefits.length ? (
                    <Typography color="text.secondary">
                      Benefits: {joinList(product.benefits)}
                    </Typography>
                  ) : null}
                  <Stack direction="row" spacing={1}>
                    <Button onClick={() => editProduct(product)} variant="outlined">
                      Edit
                    </Button>
                    <Button
                      color="error"
                      onClick={() => handleDelete(product.product_id)}
                      variant="text"
                    >
                      Delete
                    </Button>
                  </Stack>
                </Stack>
              </Paper>
            ))}

            {!loading && products.length === 0 ? (
              <Paper className="product-card">
                <Typography color="text.secondary">
                  No products yet. Add your first product to start building
                  marketing memory.
                </Typography>
              </Paper>
            ) : null}
          </Stack>
        </Grid>
      </Grid>
    </Stack>
  );
}
