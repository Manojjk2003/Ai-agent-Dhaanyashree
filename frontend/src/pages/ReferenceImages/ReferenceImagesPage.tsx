import { FormEvent, useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  Grid,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import { useAuth } from "../../auth/AuthContext";
import {
  createReferenceImage,
  deleteReferenceImage,
  listReferenceImages,
  ReferenceImageInput,
  ReferenceImageResponse,
  ReferenceImageType,
  updateReferenceImage,
  uploadAsset,
} from "../../services/api";

const emptyReferenceImage: ReferenceImageInput = {
  name: "",
  image_url: "",
  reference_type: "ingredient",
  labels: [],
  notes: "",
};

const referenceTypes: ReferenceImageType[] = [
  "ingredient",
  "product",
  "packaging",
  "style",
  "other",
];

function splitList(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function joinList(value: string[]) {
  return value.join(", ");
}

export function ReferenceImagesPage() {
  const { getIdToken } = useAuth();
  const [referenceImages, setReferenceImages] = useState<ReferenceImageResponse[]>([]);
  const [form, setForm] = useState<ReferenceImageInput>(emptyReferenceImage);
  const [labels, setLabels] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  async function loadReferenceImages() {
    setError(null);
    setLoading(true);

    try {
      const token = await getIdToken();
      setReferenceImages(await listReferenceImages(token));
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not load reference images");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadReferenceImages();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function resetForm() {
    setEditingId(null);
    setForm(emptyReferenceImage);
    setLabels("");
  }

  function editReferenceImage(referenceImage: ReferenceImageResponse) {
    setEditingId(referenceImage.reference_image_id);
    setForm(referenceImage);
    setLabels(joinList(referenceImage.labels));
    setSaved(false);
    setError(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setSaved(false);
    setError(null);

    const payload: ReferenceImageInput = {
      ...form,
      labels: splitList(labels),
    };

    try {
      const token = await getIdToken();
      if (editingId) {
        await updateReferenceImage(token, editingId, payload);
      } else {
        await createReferenceImage(token, payload);
      }

      resetForm();
      await loadReferenceImages();
      setSaved(true);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not save reference image");
    } finally {
      setSaving(false);
    }
  }

  async function uploadReferenceImage(file: File | undefined) {
    if (!file) {
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const token = await getIdToken();
      const uploaded = await uploadAsset(
        token,
        "reference_image",
        file,
        editingId ?? "unassigned",
      );
      setForm({ ...form, image_url: uploaded.image_url });
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not upload reference image");
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(referenceImageId: string) {
    const shouldDelete = window.confirm("Delete this reference image?");
    if (!shouldDelete) {
      return;
    }

    setSaving(true);
    setError(null);
    setSaved(false);

    try {
      const token = await getIdToken();
      await deleteReferenceImage(token, referenceImageId);
      await loadReferenceImages();
      if (editingId === referenceImageId) {
        resetForm();
      }
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not delete reference image");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Stack spacing={3} className="dashboard">
      <Box className="dashboard-header">
        <Stack spacing={1}>
          <Typography variant="overline" color="secondary">
            Visual Memory
          </Typography>
          <Typography variant="h1">Reference images</Typography>
          <Typography color="text.secondary" className="dashboard-subtitle">
            Add labelled ingredient, packaging, product, and style references so
            the image agent can understand business-specific visuals.
          </Typography>
        </Stack>
        <Chip label={`${referenceImages.length} references`} />
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={5}>
          <Paper className="form-panel">
            <Stack component="form" spacing={2} onSubmit={handleSubmit}>
              <Typography variant="h2">
                {editingId ? "Edit reference" : "Add reference"}
              </Typography>
              {error ? <Alert severity="error">{error}</Alert> : null}
              {saved ? <Alert severity="success">Reference image saved.</Alert> : null}
              {loading ? <Alert severity="info">Loading reference images...</Alert> : null}

              <TextField
                disabled={saving}
                label="Reference name"
                onChange={(event) => setForm({ ...form, name: event.target.value })}
                required
                value={form.name}
              />
              <TextField
                disabled={saving}
                label="Reference type"
                onChange={(event) =>
                  setForm({
                    ...form,
                    reference_type: event.target.value as ReferenceImageType,
                  })
                }
                select
                SelectProps={{ native: true }}
                value={form.reference_type}
              >
                {referenceTypes.map((referenceType) => (
                  <option key={referenceType} value={referenceType}>
                    {referenceType}
                  </option>
                ))}
              </TextField>
              <TextField
                disabled={saving}
                label="Image URL"
                onChange={(event) =>
                  setForm({ ...form, image_url: event.target.value })
                }
                required
                value={form.image_url}
              />
              <Button component="label" disabled={saving || uploading} variant="outlined">
                {uploading ? "Uploading..." : "Upload Reference Image"}
                <input
                  accept="image/*"
                  hidden
                  onChange={(event) =>
                    uploadReferenceImage(event.target.files?.[0])
                  }
                  type="file"
                />
              </Button>
              <TextField
                disabled={saving}
                helperText="Separate labels with commas, for example: foxtail millet, raw grain, yellow millet"
                label="Labels"
                onChange={(event) => setLabels(event.target.value)}
                value={labels}
              />
              <TextField
                disabled={saving}
                label="Notes"
                minRows={3}
                multiline
                onChange={(event) => setForm({ ...form, notes: event.target.value })}
                value={form.notes}
              />
              <Stack direction="row" spacing={1}>
                <Button disabled={saving || loading} type="submit" variant="contained">
                  {editingId ? "Update Reference" : "Add Reference"}
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
            {referenceImages.map((referenceImage) => (
              <Paper className="product-card" key={referenceImage.reference_image_id}>
                <Stack spacing={1}>
                  <Stack direction="row" spacing={2}>
                    <Box
                      alt={referenceImage.name}
                      className="thumb-image"
                      component="img"
                      src={referenceImage.image_url}
                    />
                    <Stack spacing={0.5}>
                      <Typography variant="h2">{referenceImage.name}</Typography>
                      <Typography color="text.secondary">
                        {referenceImage.reference_type}
                      </Typography>
                    </Stack>
                  </Stack>
                  {referenceImage.labels.length ? (
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      {referenceImage.labels.map((label) => (
                        <Chip key={label} label={label} size="small" />
                      ))}
                    </Stack>
                  ) : null}
                  {referenceImage.notes ? (
                    <Typography color="text.secondary">{referenceImage.notes}</Typography>
                  ) : null}
                  <Stack direction="row" spacing={1}>
                    <Button
                      onClick={() => editReferenceImage(referenceImage)}
                      variant="outlined"
                    >
                      Edit
                    </Button>
                    <Button
                      color="error"
                      onClick={() =>
                        handleDelete(referenceImage.reference_image_id)
                      }
                      variant="text"
                    >
                      Delete
                    </Button>
                  </Stack>
                </Stack>
              </Paper>
            ))}

            {!loading && referenceImages.length === 0 ? (
              <Paper className="product-card">
                <Typography color="text.secondary">
                  No reference images yet. Add ingredient or packaging references
                  for the image agent.
                </Typography>
              </Paper>
            ) : null}
          </Stack>
        </Grid>
      </Grid>
    </Stack>
  );
}
