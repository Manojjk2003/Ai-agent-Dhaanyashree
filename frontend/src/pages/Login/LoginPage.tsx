import { FormEvent, useState } from "react";
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

type LoginMode = "sign-in" | "sign-up";

function getAuthErrorMessage(exc: unknown) {
  const message = exc instanceof Error ? exc.message : "Authentication failed";

  if (message.includes("auth/configuration-not-found")) {
    return (
      "Firebase Authentication is not enabled for this project. In Firebase Console, open Authentication, click Get started, and enable Email/Password sign-in."
    );
  }

  if (message.includes("auth/email-already-in-use")) {
    return "This email already has an account. Switch to sign in.";
  }

  if (message.includes("auth/invalid-credential")) {
    return "Email or password is incorrect.";
  }

  if (message.includes("auth/weak-password")) {
    return "Use a password with at least 6 characters.";
  }

  return message;
}

export function LoginPage() {
  const { signIn, signUp } = useAuth();
  const [mode, setMode] = useState<LoginMode>("sign-in");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      if (mode === "sign-in") {
        await signIn(email, password);
      } else {
        await signUp(email, password);
      }
    } catch (exc) {
      setError(getAuthErrorMessage(exc));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Box className="auth-page">
      <Paper className="auth-panel">
        <Stack spacing={3}>
          <Stack spacing={1}>
            <Typography variant="overline" color="secondary">
              AI Marketing Partner
            </Typography>
            <Typography variant="h1">
              {mode === "sign-in" ? "Sign in" : "Create account"}
            </Typography>
            <Typography color="text.secondary">
              Access your business memory, content plans, and marketing agent.
            </Typography>
          </Stack>

          {error ? <Alert severity="error">{error}</Alert> : null}

          <Stack component="form" spacing={2} onSubmit={handleSubmit}>
            <TextField
              autoComplete="email"
              label="Email"
              onChange={(event) => setEmail(event.target.value)}
              required
              type="email"
              value={email}
            />
            <TextField
              autoComplete={mode === "sign-in" ? "current-password" : "new-password"}
              label="Password"
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
            <Button disabled={submitting} type="submit" variant="contained">
              {mode === "sign-in" ? "Sign in" : "Create account"}
            </Button>
          </Stack>

          <Button
            onClick={() => setMode(mode === "sign-in" ? "sign-up" : "sign-in")}
            variant="text"
          >
            {mode === "sign-in"
              ? "Need an account? Create one"
              : "Already have an account? Sign in"}
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
