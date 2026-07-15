import { FormEvent, useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  FormControlLabel,
  Grid,
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
  uploadAsset,
} from "../../services/api";

const emptyProfile: BusinessProfile = {
  business_name: "",
  industry: "",
  description: "",
  website_url: "",
  address: "",
  phone_number: "",
  email: "",
  license_number: "",
  target_audience: [],
  brand_tone: "",
  goals: [],
  brand_kit: {
    logo_url: "",
    avatar_url: "",
    primary_color: "#1b7b68",
    secondary_color: "#d9542b",
    accent_color: "#f2c94c",
    font_family: "Inter",
    heading_font_family: "Inter",
    visual_style: [],
    brand_keywords: [],
  },
};

function normalizeProfile(profile: BusinessProfile): BusinessProfile {
  return {
    ...emptyProfile,
    ...profile,
    target_audience: profile.target_audience ?? [],
    goals: profile.goals ?? [],
    brand_kit: {
      ...emptyProfile.brand_kit,
      ...(profile.brand_kit ?? {}),
      visual_style: profile.brand_kit?.visual_style ?? [],
      brand_keywords: profile.brand_kit?.brand_keywords ?? [],
    },
  };
}

const audienceOptions = [
  "Families",
  "Working professionals",
  "Busy parents",
  "Health-conscious customers",
  "Students",
  "Local community",
];

const goalOptions = [
  "Increase orders",
  "Grow Instagram reach",
  "Build trust",
  "Launch new product",
  "Educate customers",
  "Drive website visits",
];

const toneOptions = [
  "Warm",
  "Trustworthy",
  "Premium",
  "Friendly",
  "Traditional",
  "Modern",
];

const visualStyleOptions = [
  "Clean",
  "Premium",
  "Traditional Indian",
  "Natural light",
  "Minimal",
  "Bold colors",
];

const fontOptions = ["Inter", "Roboto", "Poppins", "Montserrat", "Lato", "Arial"];

function splitList(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function joinList(value: string[]) {
  return value.join(", ");
}

function toggleListValue(values: string[], value: string) {
  return values.includes(value)
    ? values.filter((item) => item !== value)
    : [...values, value];
}

function mergeOptionText(options: string[], otherValue: string) {
  return [...options, ...splitList(otherValue)];
}

export function BusinessProfilePage() {
  const { getIdToken } = useAuth();
  const [profile, setProfile] = useState<BusinessProfile>(emptyProfile);
  const [targetAudience, setTargetAudience] = useState("");
  const [goals, setGoals] = useState("");
  const [brandKeywords, setBrandKeywords] = useState("");
  const [visualStyleOther, setVisualStyleOther] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
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
          const normalized = normalizeProfile(existing);
          setProfile(normalized);
          setTargetAudience(
            joinList(
              normalized.target_audience.filter(
                (item) => !audienceOptions.includes(item),
              ),
            ),
          );
          setGoals(
            joinList(normalized.goals.filter((item) => !goalOptions.includes(item))),
          );
          setBrandKeywords(joinList(normalized.brand_kit.brand_keywords));
          setVisualStyleOther(
            joinList(
              normalized.brand_kit.visual_style.filter(
                (item) => !visualStyleOptions.includes(item),
              ),
            ),
          );
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
        target_audience: mergeOptionText(
          profile.target_audience.filter((item) => audienceOptions.includes(item)),
          targetAudience,
        ),
        goals: mergeOptionText(
          profile.goals.filter((item) => goalOptions.includes(item)),
          goals,
        ),
        brand_kit: {
          ...profile.brand_kit,
          visual_style: mergeOptionText(
            profile.brand_kit.visual_style.filter((item) =>
              visualStyleOptions.includes(item),
            ),
            visualStyleOther,
          ),
          brand_keywords: splitList(brandKeywords),
        },
      });

      const normalizedSavedProfile = normalizeProfile(savedProfile);
      setProfile(normalizedSavedProfile);
      setTargetAudience(
        joinList(
          normalizedSavedProfile.target_audience.filter(
            (item) => !audienceOptions.includes(item),
          ),
        ),
      );
      setGoals(
        joinList(
          normalizedSavedProfile.goals.filter(
            (item) => !goalOptions.includes(item),
          ),
        ),
      );
      setBrandKeywords(joinList(normalizedSavedProfile.brand_kit.brand_keywords));
      setVisualStyleOther(
        joinList(
          normalizedSavedProfile.brand_kit.visual_style.filter(
            (item) => !visualStyleOptions.includes(item),
          ),
        ),
      );
      setSaved(true);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not save profile");
    } finally {
      setSaving(false);
    }
  }

  async function uploadBrandAsset(
    file: File | undefined,
    assetType: "brand_logo" | "brand_avatar",
  ) {
    if (!file) {
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const token = await getIdToken();
      const uploaded = await uploadAsset(token, assetType, file);
      setProfile({
        ...profile,
        brand_kit: {
          ...profile.brand_kit,
          [assetType === "brand_logo" ? "logo_url" : "avatar_url"]:
            uploaded.image_url,
        },
      });
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not upload brand asset");
    } finally {
      setUploading(false);
    }
  }

  return (
    <Stack spacing={3} className="dashboard">
      <Box className="dashboard-header">
        <Stack spacing={1}>
          <Typography variant="overline" color="secondary">
            One Business Profile
          </Typography>
          <Typography variant="h1">Business profile</Typography>
          <Typography color="text.secondary" className="dashboard-subtitle">
            This single business profile is the parent memory for all products,
            captions, posters, SEO, and recommendations.
          </Typography>
        </Stack>
      </Box>

      <Paper className="form-panel business-profile-panel">
        <Stack component="form" spacing={2} onSubmit={handleSubmit}>
          {error ? <Alert severity="error">{error}</Alert> : null}
          {saved ? <Alert severity="success">Business profile saved.</Alert> : null}
          {loading ? <Alert severity="info">Loading business profile...</Alert> : null}

          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                disabled={saving}
                fullWidth
                label="Business name"
                onChange={(event) =>
                  setProfile({ ...profile, business_name: event.target.value })
                }
                required
                value={profile.business_name}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                disabled={saving}
                fullWidth
                label="Industry"
                onChange={(event) =>
                  setProfile({ ...profile, industry: event.target.value })
                }
                required
                value={profile.industry}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                disabled={saving}
                fullWidth
                label="Description"
                minRows={3}
                multiline
                onChange={(event) =>
                  setProfile({ ...profile, description: event.target.value })
                }
                value={profile.description}
              />
            </Grid>
          </Grid>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                disabled={saving}
                fullWidth
                label="Website URL"
                onChange={(event) =>
                  setProfile({ ...profile, website_url: event.target.value })
                }
                value={profile.website_url}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                disabled={saving}
                fullWidth
                label="Phone number"
                onChange={(event) =>
                  setProfile({ ...profile, phone_number: event.target.value })
                }
                value={profile.phone_number}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                disabled={saving}
                fullWidth
                label="Business email"
                onChange={(event) =>
                  setProfile({ ...profile, email: event.target.value })
                }
                value={profile.email}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                disabled={saving}
                fullWidth
                label="License number"
                onChange={(event) =>
                  setProfile({ ...profile, license_number: event.target.value })
                }
                value={profile.license_number}
              />
            </Grid>
          </Grid>
          <TextField
            disabled={saving}
            label="Address"
            minRows={2}
            multiline
            onChange={(event) =>
              setProfile({ ...profile, address: event.target.value })
            }
            value={profile.address}
          />

          <Typography variant="h2">Target audience</Typography>
          <Box className="option-grid">
            {audienceOptions.map((option) => (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={profile.target_audience.includes(option)}
                    onChange={() =>
                      setProfile({
                        ...profile,
                        target_audience: toggleListValue(
                          profile.target_audience,
                          option,
                        ),
                      })
                    }
                  />
                }
                disabled={saving}
                key={option}
                label={option}
              />
            ))}
          </Box>
          <TextField
            disabled={saving}
            helperText="Use this for audience groups not listed above"
            label="Other target audience"
            onChange={(event) => setTargetAudience(event.target.value)}
            value={targetAudience}
          />

          <Typography variant="h2">Brand tone</Typography>
          <Box className="option-grid">
            {toneOptions.map((option) => (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={profile.brand_tone
                      .split(",")
                      .map((item) => item.trim())
                      .includes(option)}
                    onChange={() => {
                      const next = toggleListValue(splitList(profile.brand_tone), option);
                      setProfile({ ...profile, brand_tone: joinList(next) });
                    }}
                  />
                }
                disabled={saving}
                key={option}
                label={option}
              />
            ))}
          </Box>
          <TextField
            disabled={saving}
            helperText="Add custom tone words if needed"
            label="Brand tone"
            onChange={(event) =>
              setProfile({ ...profile, brand_tone: event.target.value })
            }
            value={profile.brand_tone}
          />

          <Typography variant="h2">Business goals</Typography>
          <Box className="option-grid">
            {goalOptions.map((option) => (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={profile.goals.includes(option)}
                    onChange={() =>
                      setProfile({
                        ...profile,
                        goals: toggleListValue(profile.goals, option),
                      })
                    }
                  />
                }
                disabled={saving}
                key={option}
                label={option}
              />
            ))}
          </Box>
          <TextField
            disabled={saving}
            helperText="Use this for goals not listed above"
            label="Other business goals"
            onChange={(event) => setGoals(event.target.value)}
            value={goals}
          />

          <Typography variant="h2">Brand kit</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                disabled={saving}
                fullWidth
                label="Logo URL"
                onChange={(event) =>
                  setProfile({
                    ...profile,
                    brand_kit: {
                      ...profile.brand_kit,
                      logo_url: event.target.value,
                    },
                  })
                }
                value={profile.brand_kit.logo_url}
              />
              <Button component="label" disabled={uploading || saving} variant="outlined">
                {uploading ? "Uploading..." : "Upload Logo"}
                <input
                  accept="image/*"
                  hidden
                  onChange={(event) =>
                    uploadBrandAsset(event.target.files?.[0], "brand_logo")
                  }
                  type="file"
                />
              </Button>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                disabled={saving}
                fullWidth
                label="Avatar URL"
                onChange={(event) =>
                  setProfile({
                    ...profile,
                    brand_kit: {
                      ...profile.brand_kit,
                      avatar_url: event.target.value,
                    },
                  })
                }
                value={profile.brand_kit.avatar_url}
              />
              <Button component="label" disabled={uploading || saving} variant="outlined">
                {uploading ? "Uploading..." : "Upload Avatar"}
                <input
                  accept="image/*"
                  hidden
                  onChange={(event) =>
                    uploadBrandAsset(event.target.files?.[0], "brand_avatar")
                  }
                  type="file"
                />
              </Button>
            </Grid>
            {[
              ["Primary color", "primary_color"],
              ["Secondary color", "secondary_color"],
              ["Accent color", "accent_color"],
            ].map(([label, key]) => (
              <Grid item xs={12} md={4} key={key}>
                <TextField
                  disabled={saving}
                  fullWidth
                  label={label}
                  onChange={(event) =>
                    setProfile({
                      ...profile,
                      brand_kit: {
                        ...profile.brand_kit,
                        [key]: event.target.value,
                      },
                    })
                  }
                  type="color"
                  value={
                    profile.brand_kit[
                      key as "primary_color" | "secondary_color" | "accent_color"
                    ] || "#1b7b68"
                  }
                />
              </Grid>
            ))}
            <Grid item xs={12} md={6}>
              <TextField
                disabled={saving}
                fullWidth
                label="Body font"
                onChange={(event) =>
                  setProfile({
                    ...profile,
                    brand_kit: {
                      ...profile.brand_kit,
                      font_family: event.target.value,
                    },
                  })
                }
                select
                SelectProps={{ native: true }}
                value={profile.brand_kit.font_family}
              >
                {fontOptions.map((font) => (
                  <option key={font} value={font}>
                    {font}
                  </option>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                disabled={saving}
                fullWidth
                label="Heading font"
                onChange={(event) =>
                  setProfile({
                    ...profile,
                    brand_kit: {
                      ...profile.brand_kit,
                      heading_font_family: event.target.value,
                    },
                  })
                }
                select
                SelectProps={{ native: true }}
                value={profile.brand_kit.heading_font_family}
              >
                {fontOptions.map((font) => (
                  <option key={font} value={font}>
                    {font}
                  </option>
                ))}
              </TextField>
            </Grid>
          </Grid>
          <Box className="option-grid">
            {visualStyleOptions.map((option) => (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={profile.brand_kit.visual_style.includes(option)}
                    onChange={() =>
                      setProfile({
                        ...profile,
                        brand_kit: {
                          ...profile.brand_kit,
                          visual_style: toggleListValue(
                            profile.brand_kit.visual_style,
                            option,
                          ),
                        },
                      })
                    }
                  />
                }
                disabled={saving}
                key={option}
                label={option}
              />
            ))}
          </Box>
          <TextField
            disabled={saving}
            helperText="Use this for visual styles not listed above"
            label="Other visual styles"
            onChange={(event) => setVisualStyleOther(event.target.value)}
            value={visualStyleOther}
          />
          <TextField
            disabled={saving}
            helperText="Separate brand keywords with commas"
            label="Brand keywords"
            onChange={(event) => setBrandKeywords(event.target.value)}
            value={brandKeywords}
          />

          <Button disabled={saving || loading} type="submit" variant="contained">
            Save Business Profile
          </Button>
        </Stack>
      </Paper>
    </Stack>
  );
}
