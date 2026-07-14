import { FormEvent, useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import { useAuth } from "../../auth/AuthContext";
import {
  BusinessProfile,
  getBusinessProfile,
  saveBusinessProfile,
} from "../../services/api";

const emptyProfile: BusinessProfile = {
  business_name: "",
  industry: "",
  description: "",
  target_audience: [],
  brand_tone: "",
  goals: [],
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

export function BusinessProfilePage() {
  const { getIdToken } = useAuth();
  const [profile, setProfile] = useState<BusinessProfile>(emptyProfile);
  const [targetAudience, setTargetAudience] = useState("");
  const [goals, setGoals] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function loadProfile() {
      setError(null);
      setLoading(true);

      try {
        const token = await getIdToken();
        const existing = await getBusinessProfile(token);

        if (!mounted) {
          return;
        }

        if (existing) {
          setProfile(existing);
          setTargetAudience(joinList(existing.target_audience));
          setGoals(joinList(existing.goals));
        }
      } catch (exc) {
        if (mounted) {
          setError(exc instanceof Error ? exc.message : "Could not load profile");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadProfile();

    return () => {
      mounted = false;
    };
  }, [getIdToken]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSaved(false);
    setSaving(true);

    try {
      const token = await getIdToken();
      const savedProfile = await saveBusinessProfile(token, {
        ...profile,
        target_audience: splitList(targetAudience),
        goals: splitList(goals),
      });

      setProfile(savedProfile);
      setTargetAudience(joinList(savedProfile.target_audience));
      setGoals(joinList(savedProfile.goals));
      setSaved(true);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not save profile");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Stack spacing={3} className="dashboard">
      <Box className="dashboard-header">
        <Stack spacing={1}>
          <Typography variant="overline" color="secondary">
            Business Memory
          </Typography>
          <Typography variant="h1">Business profile</Typography>
          <Typography color="text.secondary" className="dashboard-subtitle">
            This profile becomes the first memory layer for product selection,
            captions, posters, SEO, and recommendations.
          </Typography>
        </Stack>
      </Box>

      <Paper className="form-panel">
        <Stack component="form" spacing={2} onSubmit={handleSubmit}>
          {error ? <Alert severity="error">{error}</Alert> : null}
          {saved ? <Alert severity="success">Business profile saved.</Alert> : null}
          {loading ? <Alert severity="info">Loading business profile...</Alert> : null}

          <TextField
            disabled={saving}
            label="Business name"
            onChange={(event) =>
              setProfile({ ...profile, business_name: event.target.value })
            }
            required
            value={profile.business_name}
          />
          <TextField
            disabled={saving}
            label="Industry"
            onChange={(event) =>
              setProfile({ ...profile, industry: event.target.value })
            }
            required
            value={profile.industry}
          />
          <TextField
            disabled={saving}
            label="Description"
            minRows={3}
            multiline
            onChange={(event) =>
              setProfile({ ...profile, description: event.target.value })
            }
            value={profile.description}
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
            label="Brand tone"
            onChange={(event) =>
              setProfile({ ...profile, brand_tone: event.target.value })
            }
            value={profile.brand_tone}
          />
          <TextField
            disabled={saving}
            helperText="Separate goals with commas"
            label="Business goals"
            onChange={(event) => setGoals(event.target.value)}
            value={goals}
          />

          <Button disabled={saving || loading} type="submit" variant="contained">
            Save Business Memory
          </Button>
        </Stack>
      </Paper>
    </Stack>
  );
}
