import { useEffect, useState } from "react";
import {
  Box,
  Button,
  Chip,
  Grid,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { CalendarDays, Megaphone, RefreshCw, Sparkles } from "lucide-react";

import { getHealth } from "../../services/api";

type ApiStatus = "checking" | "online" | "offline";

const nextActions = [
  "Add Firebase Auth and business profile storage",
  "Create product management",
  "Wire the daily LangGraph workflow to real business data",
];

export function DashboardPage() {
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");

  useEffect(() => {
    getHealth()
      .then(() => setApiStatus("online"))
      .catch(() => setApiStatus("offline"));
  }, []);

  const statusColor =
    apiStatus === "online" ? "success" : apiStatus === "offline" ? "error" : "warning";

  return (
    <Stack spacing={3} className="dashboard">
      <Box className="dashboard-header">
        <Stack spacing={1}>
          <Typography variant="overline" color="secondary">
            AI Marketing Partner
          </Typography>
          <Typography variant="h1">Daily marketing command center</Typography>
          <Typography color="text.secondary" className="dashboard-subtitle">
            The first foundation is ready: React frontend, FastAPI backend,
            and a placeholder LangGraph workflow.
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
    </Stack>
  );
}
