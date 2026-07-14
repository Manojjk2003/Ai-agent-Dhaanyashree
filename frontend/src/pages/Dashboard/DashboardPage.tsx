import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  Grid,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { CalendarDays, Megaphone, RefreshCw, Sparkles } from "lucide-react";

import { useAuth } from "../../auth/AuthContext";
import { getHealth, listProducts } from "../../services/api";

type ApiStatus = "checking" | "online" | "offline";

const nextActions = [
  "Create product management",
  "Wire the daily LangGraph workflow to real business data",
  "Use the business profile in content generation",
];

export function DashboardPage() {
  const { getIdToken } = useAuth();
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");
  const [productCount, setProductCount] = useState<number | null>(null);
  const [tokenCopied, setTokenCopied] = useState(false);

  useEffect(() => {
    getHealth()
      .then(() => setApiStatus("online"))
      .catch(() => setApiStatus("offline"));
  }, []);

  useEffect(() => {
    getIdToken()
      .then((token) => listProducts(token))
      .then((products) => setProductCount(products.length))
      .catch(() => setProductCount(null));
  }, [getIdToken]);

  const statusColor =
    apiStatus === "online" ? "success" : apiStatus === "offline" ? "error" : "warning";

  async function copyFirebaseToken() {
    const token = await getIdToken();
    await navigator.clipboard.writeText(token);
    setTokenCopied(true);
    window.setTimeout(() => setTokenCopied(false), 3000);
  }

  return (
    <Stack spacing={3} className="dashboard">
      <Box className="dashboard-header">
        <Stack spacing={1}>
          <Typography variant="overline" color="secondary">
            AI Marketing Partner
          </Typography>
          <Typography variant="h1">Daily marketing command center</Typography>
          <Typography color="text.secondary" className="dashboard-subtitle">
            Auth and business memory are now the active foundation for the
            marketing agent.
          </Typography>
        </Stack>

        <Chip
          icon={<RefreshCw size={16} />}
          label={`API ${apiStatus}`}
          color={statusColor}
          variant="outlined"
        />
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Paper className="metric-card">
            <Sparkles size={24} />
            <Typography variant="h2">Daily Plan</Typography>
            <Typography color="text.secondary">
              Generate a product, trend, caption, hashtags, and poster draft.
            </Typography>
            <Button variant="contained" disabled>
              Generate Soon
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper className="metric-card">
            <Sparkles size={24} />
            <Typography variant="h2">Product Memory</Typography>
            <Typography color="text.secondary">
              {productCount === null
                ? "Connect Firebase Admin to read product memory."
                : `${productCount} products available for agent planning.`}
            </Typography>
            <Button variant="outlined" disabled>
              Manage Products
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper className="metric-card">
            <Megaphone size={24} />
            <Typography variant="h2">Content Review</Typography>
            <Typography color="text.secondary">
              Approve, edit, or reject posts before anything is published.
            </Typography>
            <Button variant="outlined" disabled>
              Review Drafts
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper className="metric-card">
            <CalendarDays size={24} />
            <Typography variant="h2">Calendar</Typography>
            <Typography color="text.secondary">
              Schedule 7-day and 30-day campaigns for each business.
            </Typography>
            <Button variant="outlined" disabled>
              Open Calendar
            </Button>
          </Paper>
        </Grid>
      </Grid>

      <Paper className="next-panel">
        <Typography variant="h2">Next build steps</Typography>
        <Stack component="ol" spacing={1} className="action-list">
          {nextActions.map((action) => (
            <Typography component="li" key={action}>
              {action}
            </Typography>
          ))}
        </Stack>
      </Paper>

      <Paper className="next-panel">
        <Typography variant="h2">API testing</Typography>
        <Typography color="text.secondary">
          Copy your Firebase ID token, open FastAPI Swagger at the backend
          `/docs` page, click Authorize, and paste the token.
        </Typography>
        {tokenCopied ? <Alert severity="success">Firebase ID token copied.</Alert> : null}
        <Button onClick={copyFirebaseToken} variant="outlined">
          Copy Firebase ID Token
        </Button>
      </Paper>
    </Stack>
  );
}
