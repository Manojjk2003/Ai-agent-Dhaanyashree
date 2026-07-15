import { useEffect, useMemo, useState } from "react";
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
  createScheduledPost,
  deleteScheduledPost,
  GeneratedPostResponse,
  listGeneratedPosts,
  listScheduledPosts,
  publishScheduledPostNow,
  recommendScheduleTime,
  ScheduleRecommendationResponse,
  ScheduledPostResponse,
} from "../../services/api";

function defaultScheduleTime() {
  const date = new Date();
  date.setDate(date.getDate() + 1);
  date.setHours(10, 0, 0, 0);
  const pad = (value: number) => String(value).padStart(2, "0");
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
  ].join("-") + `T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function displayDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function toDateInputValue(value: string) {
  return value.slice(0, 10);
}

function toDatetimeInputValue(value: string) {
  const date = new Date(value);
  const pad = (part: number) => String(part).padStart(2, "0");
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
  ].join("-") + `T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function ContentCalendarPage() {
  const { getIdToken } = useAuth();
  const [generatedPosts, setGeneratedPosts] = useState<GeneratedPostResponse[]>([]);
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPostResponse[]>([]);
  const [selectedPostId, setSelectedPostId] = useState("");
  const [scheduledAt, setScheduledAt] = useState(defaultScheduleTime());
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [recommending, setRecommending] = useState(false);
  const [recommendation, setRecommendation] =
    useState<ScheduleRecommendationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [published, setPublished] = useState(false);

  const approvedPosts = useMemo(
    () => generatedPosts.filter((post) => post.status === "approved"),
    [generatedPosts],
  );

  function selectPost(postId: string) {
    setSelectedPostId(postId);
    setRecommendation(null);
    setSaved(false);
    setPublished(false);
    setError(null);
  }

  async function loadCalendar() {
    setError(null);
    setLoading(true);

    try {
      const token = await getIdToken();
      const [posts, scheduled] = await Promise.all([
        listGeneratedPosts(token),
        listScheduledPosts(token),
      ]);
      setGeneratedPosts(posts);
      setScheduledPosts(scheduled);
      const firstApproved = posts.find((post) => post.status === "approved");
      setSelectedPostId((current) => current || firstApproved?.post_id || "");
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not load calendar");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCalendar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function schedulePost() {
    if (!selectedPostId) {
      setError("Approve generated content before scheduling it.");
      return;
    }

    setSaving(true);
    setSaved(false);
    setError(null);

    try {
      const token = await getIdToken();
      await createScheduledPost(token, {
        post_id: selectedPostId,
        scheduled_at: new Date(scheduledAt).toISOString(),
        platforms: ["instagram"],
      });
      setSaved(true);
      setSelectedPostId("");
      await loadCalendar();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not schedule content");
    } finally {
      setSaving(false);
    }
  }

  async function publishNow(scheduledPostId: string) {
    const shouldPublish = window.confirm(
      "Publish this scheduled post now? This MVP records a mock publish only.",
    );
    if (!shouldPublish) {
      return;
    }

    setPublishing(true);
    setSaved(false);
    setPublished(false);
    setError(null);

    try {
      const token = await getIdToken();
      await publishScheduledPostNow(token, scheduledPostId);
      setPublished(true);
      await loadCalendar();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not publish post");
    } finally {
      setPublishing(false);
    }
  }

  async function recommendTime() {
    if (!selectedPostId) {
      setError("Choose approved content before asking for a recommended time.");
      return;
    }

    setRecommending(true);
    setSaved(false);
    setError(null);
    setRecommendation(null);

    try {
      const token = await getIdToken();
      const result = await recommendScheduleTime(token, {
        post_id: selectedPostId,
        target_date: toDateInputValue(scheduledAt),
        platforms: ["instagram"],
      });
      setRecommendation(result);
      setScheduledAt(toDatetimeInputValue(result.recommended_at));
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not recommend a time");
    } finally {
      setRecommending(false);
    }
  }

  async function cancelScheduledPost(scheduledPostId: string) {
    const shouldCancel = window.confirm("Cancel this scheduled post?");
    if (!shouldCancel) {
      return;
    }

    setSaving(true);
    setSaved(false);
    setError(null);

    try {
      const token = await getIdToken();
      await deleteScheduledPost(token, scheduledPostId);
      await loadCalendar();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not cancel scheduled post");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Stack spacing={3} className="dashboard">
      <Box className="dashboard-header">
        <Stack spacing={1}>
          <Typography variant="overline" color="secondary">
            Content Calendar
          </Typography>
          <Typography variant="h1">Schedule approved posts</Typography>
          <Typography color="text.secondary" className="dashboard-subtitle">
            Move approved generated content into the publishing calendar.
          </Typography>
        </Stack>
        <Chip label={`${scheduledPosts.length} scheduled`} />
      </Box>

      {error ? <Alert severity="error">{error}</Alert> : null}
      {saved ? <Alert severity="success">Content scheduled.</Alert> : null}
      {published ? <Alert severity="success">Mock publish recorded.</Alert> : null}
      {loading ? <Alert severity="info">Loading calendar...</Alert> : null}

      <Grid container spacing={2}>
        <Grid item xs={12} md={5}>
          <Paper className="form-panel review-panel">
            <Stack spacing={2}>
              <Stack spacing={0.5}>
                <Typography variant="h2">Ready to schedule</Typography>
                <Typography color="text.secondary">
                  Only approved generated content appears here.
                </Typography>
              </Stack>

              {approvedPosts.map((post) => (
                <Paper
                  className="product-card selectable-card"
                  key={post.post_id}
                  onClick={() => selectPost(post.post_id)}
                  variant={selectedPostId === post.post_id ? "outlined" : "elevation"}
                >
                  <Stack spacing={1}>
                    <Stack direction="row" justifyContent="space-between">
                      <Typography variant="h2">{post.product_name}</Typography>
                      <Chip label={post.generation_source} size="small" />
                    </Stack>
                    <Typography color="text.secondary">{post.content_type}</Typography>
                    <Typography>{post.caption}</Typography>
                  </Stack>
                </Paper>
              ))}

              {!loading && approvedPosts.length === 0 ? (
                <Typography color="text.secondary">
                  Approve content in the Content tab before scheduling.
                </Typography>
              ) : null}

              <TextField
                disabled={saving || recommending}
                label="Schedule time"
                onChange={(event) => setScheduledAt(event.target.value)}
                type="datetime-local"
                value={scheduledAt}
              />
              <Stack direction="row" spacing={1}>
                <Button
                  disabled={saving || recommending || !selectedPostId}
                  onClick={recommendTime}
                  variant="outlined"
                >
                  {recommending ? "Thinking..." : "Recommend Time"}
                </Button>
                <Button
                  disabled={saving || recommending || !selectedPostId}
                  onClick={schedulePost}
                  variant="contained"
                >
                  {saving ? "Scheduling..." : "Schedule Selected Post"}
                </Button>
              </Stack>
              {recommendation ? (
                <Paper className="product-card">
                  <Stack spacing={1}>
                    <Stack direction="row" spacing={1}>
                      <Chip
                        label={
                          recommendation.generation_source === "gemini"
                            ? "Gemini recommendation"
                            : "Fallback recommendation"
                        }
                        size="small"
                      />
                      <Chip
                        label={`${Math.round(recommendation.confidence * 100)}% confidence`}
                        size="small"
                      />
                    </Stack>
                    <Typography>
                      <strong>Recommended:</strong>{" "}
                      {displayDate(recommendation.recommended_at)}
                    </Typography>
                    <Typography color="text.secondary">
                      {recommendation.reason}
                    </Typography>
                    {recommendation.alternative_slots.length ? (
                      <Typography color="text.secondary">
                        <strong>Alternatives:</strong>{" "}
                        {recommendation.alternative_slots.map(displayDate).join(", ")}
                      </Typography>
                    ) : null}
                  </Stack>
                </Paper>
              ) : null}
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} md={7}>
          <Paper className="form-panel review-panel">
            <Stack spacing={2}>
              <Stack spacing={0.5}>
                <Typography variant="h2">Scheduled queue</Typography>
                <Typography color="text.secondary">
                  This is the manual schedule queue. Auto-publishing comes later.
                </Typography>
              </Stack>

              {scheduledPosts.map((post) => (
                <Paper className="product-card" key={post.scheduled_post_id}>
                  <Stack spacing={1}>
                    <Stack direction="row" justifyContent="space-between">
                      <Typography variant="h2">{post.product_name}</Typography>
                      <Chip label={post.status} size="small" />
                    </Stack>
                    <Typography color="text.secondary">
                      {displayDate(post.scheduled_at)} - {post.platforms.join(", ")}
                    </Typography>
                    {post.published_at ? (
                      <Typography color="text.secondary">
                        Published {displayDate(post.published_at)}
                        {post.platform_post_id
                          ? ` - ${post.platform_post_id}`
                          : ""}
                      </Typography>
                    ) : null}
                    {post.error_message ? (
                      <Alert severity="error">{post.error_message}</Alert>
                    ) : null}
                    <Typography>{post.caption}</Typography>
                    {post.status === "scheduled" ? (
                      <Stack direction="row" spacing={1}>
                        <Button
                          disabled={publishing || saving}
                          onClick={() => publishNow(post.scheduled_post_id)}
                          variant="contained"
                        >
                          {publishing ? "Publishing..." : "Publish Now"}
                        </Button>
                        <Button
                          color="error"
                          disabled={saving || publishing}
                          onClick={() => cancelScheduledPost(post.scheduled_post_id)}
                          variant="text"
                        >
                          Cancel Schedule
                        </Button>
                      </Stack>
                    ) : null}
                  </Stack>
                </Paper>
              ))}

              {!loading && scheduledPosts.length === 0 ? (
                <Typography color="text.secondary">
                  No scheduled posts yet.
                </Typography>
              ) : null}
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Stack>
  );
}
