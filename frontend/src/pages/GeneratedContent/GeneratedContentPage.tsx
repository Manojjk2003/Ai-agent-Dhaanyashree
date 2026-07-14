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
  deleteGeneratedPost,
  generatePoster,
  GeneratedPostResponse,
  GeneratedPosterResponse,
  GeneratedPostStatus,
  listGeneratedPosters,
  listGeneratedPosts,
  updateGeneratedPost,
} from "../../services/api";

function splitList(value: string) {
  return value
    .split(/\s|,/)
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => (item.startsWith("#") ? item : `#${item}`));
}

export function GeneratedContentPage() {
  const { getIdToken } = useAuth();
  const [posts, setPosts] = useState<GeneratedPostResponse[]>([]);
  const [posters, setPosters] = useState<GeneratedPosterResponse[]>([]);
  const [selected, setSelected] = useState<GeneratedPostResponse | null>(null);
  const [caption, setCaption] = useState("");
  const [hashtags, setHashtags] = useState("");
  const [posterPrompt, setPosterPrompt] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [generatingPoster, setGeneratingPoster] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [deleted, setDeleted] = useState(false);
  const [posterGenerated, setPosterGenerated] = useState(false);

  async function loadPosts() {
    setError(null);
    setLoading(true);

    try {
      const token = await getIdToken();
      const [loadedPosts, loadedPosters] = await Promise.all([
        listGeneratedPosts(token),
        listGeneratedPosters(token),
      ]);
      setPosts(loadedPosts);
      setPosters(loadedPosters);

      if (!selected && loadedPosts.length) {
        selectPost(loadedPosts[0]);
      }
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not load generated posts");
    } finally {
      setLoading(false);
    }
  }

  function selectPost(post: GeneratedPostResponse) {
    setSelected(post);
    setCaption(post.caption);
    setHashtags(post.hashtags.join(" "));
    setPosterPrompt(post.poster_prompt ?? "");
    setSaved(false);
    setDeleted(false);
    setPosterGenerated(false);
    setError(null);
  }

  useEffect(() => {
    loadPosts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function savePost(status?: GeneratedPostStatus) {
    if (!selected) {
      return;
    }

    setSaving(true);
    setSaved(false);
    setError(null);

    try {
      const token = await getIdToken();
      const updated = await updateGeneratedPost(token, selected.post_id, {
        caption,
        hashtags: splitList(hashtags),
        poster_prompt: posterPrompt,
        status: status ?? selected.status,
      });

      setPosts((current) =>
        current.map((post) => (post.post_id === updated.post_id ? updated : post)),
      );
      selectPost(updated);
      setSaved(true);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not save generated post");
    } finally {
      setSaving(false);
    }
  }

  async function deletePost() {
    if (!selected) {
      return;
    }

    const shouldDelete = window.confirm(
      "Reject and permanently delete this generated draft?",
    );
    if (!shouldDelete) {
      return;
    }

    setDeleting(true);
    setSaved(false);
    setDeleted(false);
    setError(null);

    try {
      const token = await getIdToken();
      await deleteGeneratedPost(token, selected.post_id);

      const remainingPosts = posts.filter(
        (post) => post.post_id !== selected.post_id,
      );
      setPosts(remainingPosts);

      if (remainingPosts.length) {
        selectPost(remainingPosts[0]);
      } else {
        setSelected(null);
        setCaption("");
        setHashtags("");
        setPosterPrompt("");
      }
      setDeleted(true);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not delete generated post");
    } finally {
      setDeleting(false);
    }
  }

  async function generateSelectedPoster() {
    if (!selected) {
      return;
    }

    setGeneratingPoster(true);
    setPosterGenerated(false);
    setSaved(false);
    setError(null);

    try {
      const token = await getIdToken();
      const updated = await updateGeneratedPost(token, selected.post_id, {
        caption,
        hashtags: splitList(hashtags),
        poster_prompt: posterPrompt,
        status: selected.status,
      });
      const poster = await generatePoster(token, updated.post_id);

      setPosts((current) =>
        current.map((post) => (post.post_id === updated.post_id ? updated : post)),
      );
      setPosters((current) => [
        poster,
        ...current.filter((item) => item.poster_id !== poster.poster_id),
      ]);
      selectPost(updated);
      setPosterGenerated(true);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not generate poster");
    } finally {
      setGeneratingPoster(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await savePost();
  }

  const selectedPoster = selected
    ? posters.find((poster) => poster.post_id === selected.post_id)
    : null;

  return (
    <Stack spacing={3} className="dashboard">
      <Box className="dashboard-header">
        <Stack spacing={1}>
          <Typography variant="overline" color="secondary">
            Content Review
          </Typography>
          <Typography variant="h1">Generated content</Typography>
          <Typography color="text.secondary" className="dashboard-subtitle">
            Review generated captions, hashtags, and poster prompts before they
            move into scheduling.
          </Typography>
        </Stack>
        <Chip label={`${posts.length} generated`} />
      </Box>

      {error ? <Alert severity="error">{error}</Alert> : null}
      {saved ? <Alert severity="success">Generated content saved.</Alert> : null}
      {deleted ? <Alert severity="success">Generated content deleted.</Alert> : null}
      {posterGenerated ? <Alert severity="success">Poster generated.</Alert> : null}
      {loading ? <Alert severity="info">Loading generated content...</Alert> : null}

      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Stack spacing={2}>
            {posts.map((post) => (
              <Paper
                className="product-card selectable-card"
                key={post.post_id}
                onClick={() => selectPost(post)}
              >
                <Stack spacing={1}>
                  <Stack direction="row" justifyContent="space-between">
                    <Typography variant="h2">{post.product_name}</Typography>
                    <Chip label={post.status.replaceAll("_", " ")} size="small" />
                  </Stack>
                  <Chip
                    label={post.generation_source === "gemini" ? "Gemini" : "Fallback"}
                    size="small"
                    sx={{ alignSelf: "flex-start" }}
                  />
                  <Typography color="text.secondary">{post.content_type}</Typography>
                  <Typography>{post.content_idea}</Typography>
                </Stack>
              </Paper>
            ))}

            {!loading && posts.length === 0 ? (
              <Paper className="product-card">
                <Typography color="text.secondary">
                  No generated content yet. Use Generate Today on the dashboard.
                </Typography>
              </Paper>
            ) : null}
          </Stack>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper className="form-panel review-panel">
            {selected ? (
              <Stack component="form" spacing={2} onSubmit={handleSubmit}>
                <Stack spacing={0.5}>
                  <Typography variant="h2">{selected.product_name}</Typography>
                  <Typography color="text.secondary">
                    {selected.selection_reason}
                  </Typography>
                  <Chip
                    label={
                      selected.generation_source === "gemini"
                        ? "Generated with Gemini"
                        : "Generated with fallback rules"
                    }
                    size="small"
                    sx={{ alignSelf: "flex-start" }}
                  />
                </Stack>

                <TextField
                  disabled={saving || deleting}
                  label="Caption"
                  minRows={5}
                  multiline
                  onChange={(event) => setCaption(event.target.value)}
                  value={caption}
                />
                <TextField
                  disabled={saving || deleting}
                  helperText="Separate hashtags with spaces or commas"
                  label="Hashtags"
                  onChange={(event) => setHashtags(event.target.value)}
                  value={hashtags}
                />
                <TextField
                  disabled={saving || deleting}
                  label="Poster prompt"
                  minRows={4}
                  multiline
                  onChange={(event) => setPosterPrompt(event.target.value)}
                  value={posterPrompt}
                />
                <Stack direction="row" spacing={1}>
                  <Button disabled={saving || deleting} type="submit" variant="contained">
                    Save Changes
                  </Button>
                  <Button
                    color="success"
                    disabled={saving || deleting}
                    onClick={() => savePost("approved")}
                    variant="outlined"
                  >
                    Approve
                  </Button>
                  <Button
                    color="error"
                    disabled={saving || deleting}
                    onClick={deletePost}
                    variant="text"
                  >
                    {deleting ? "Deleting..." : "Reject and Delete"}
                  </Button>
                </Stack>
                <Stack spacing={2}>
                  <Button
                    disabled={saving || deleting || generatingPoster}
                    onClick={generateSelectedPoster}
                    variant="outlined"
                  >
                    {generatingPoster ? "Generating Poster..." : "Generate Poster"}
                  </Button>
                  {selectedPoster ? (
                    <Paper className="poster-preview">
                      <Stack spacing={1}>
                        <img
                          alt={`${selectedPoster.product_name} generated poster`}
                          className="poster-preview-image"
                          src={selectedPoster.image_url}
                        />
                        <Chip
                          label={
                            selectedPoster.provider === "huggingface"
                              ? "Generated with Hugging Face FLUX"
                              : selectedPoster.provider === "gemini"
                                ? "Generated with Gemini image"
                                : "Generated with fallback poster"
                          }
                          size="small"
                          sx={{ alignSelf: "flex-start" }}
                        />
                        {selectedPoster.provider === "fallback" &&
                        selectedPoster.error_message ? (
                          <Alert severity="warning">
                            Image API fallback: {selectedPoster.error_message}
                          </Alert>
                        ) : null}
                      </Stack>
                    </Paper>
                  ) : null}
                </Stack>
              </Stack>
            ) : (
              <Typography color="text.secondary">
                Select generated content to review.
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Stack>
  );
}
