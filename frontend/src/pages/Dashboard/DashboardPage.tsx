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
import {
  DailyPlanResponse,
  getHealth,
  listProducts,
  runDailyPlan,
} from "../../services/api";

type ApiStatus = "checking" | "online" | "offline";

const nextActions = [
  "Generate today's marketing plan from business profile and products",
  "Review caption, hashtags, and poster prompt",
  "Save generated content to a content calendar",
];

export function DashboardPage() {
  const { getIdToken } = useAuth();
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");
  const [productCount, setProductCount] = useState<number | null>(null);
  const [tokenCopied, setTokenCopied] = useState(false);
  const [dailyPlan, setDailyPlan] = useState<DailyPlanResponse | null>(null);
  const [planError, setPlanError] = useState<string | null>(null);
  const [generatingPlan, setGeneratingPlan] = useState(false);

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

  async function generateDailyPlan() {
    setPlanError(null);
    setGeneratingPlan(true);

    try {
      const token = await getIdToken();
      setDailyPlan(await runDailyPlan(token));
    } catch (exc) {
      setPlanError(exc instanceof Error ? exc.message : "Could not generate plan");
    } finally {
      setGeneratingPlan(false);
    }
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
            Your one business profile and its products are the active memory
            for the marketing agent.
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
              Use your one business profile and products to create today's
              caption, hashtags, and poster prompt.
            </Typography>
            <Button
              disabled={generatingPlan}
              onClick={generateDailyPlan}
              variant="contained"
            >
              {generatingPlan ? "Generating..." : "Generate Today"}
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper className="metric-card">
            <Sparkles size={24} />
            <Typography variant="h2">Products</Typography>
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

      {planError ? <Alert severity="error">{planError}</Alert> : null}

      {dailyPlan ? (
        <Paper className="next-panel">
          <Stack spacing={2}>
            <Stack spacing={0.5}>
              <Typography variant="overline" color="secondary">
                Today's Generated Plan
              </Typography>
              <Typography variant="h2">{dailyPlan.selected_product_name}</Typography>
              <Typography color="text.secondary">
                {dailyPlan.selection_reason}
              </Typography>
            </Stack>

            <Stack spacing={1}>
              <Typography>
                <strong>Content type:</strong> {dailyPlan.content_type}
              </Typography>
              <Typography>
                <strong>Idea:</strong> {dailyPlan.content_idea}
              </Typography>
              <Typography>
                <strong>Caption:</strong> {dailyPlan.caption}
              </Typography>
              <Typography>
                <strong>Hashtags:</strong> {dailyPlan.hashtags.join(" ")}
              </Typography>
              {dailyPlan.poster_prompt ? (
                <Typography>
                  <strong>Poster prompt:</strong> {dailyPlan.poster_prompt}
                </Typography>
              ) : null}
            </Stack>
          </Stack>
        </Paper>
      ) : null}

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
