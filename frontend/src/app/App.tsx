import { useState } from "react";
import {
  AppBar,
  Box,
  Button,
  CircularProgress,
  Container,
  Stack,
  Toolbar,
  Typography,
} from "@mui/material";

import { useAuth } from "../auth/AuthContext";
import { BusinessProfilePage } from "../pages/BusinessProfile/BusinessProfilePage";
import { DashboardPage } from "../pages/Dashboard/DashboardPage";
import { LoginPage } from "../pages/Login/LoginPage";
import { ProductsPage } from "../pages/Products/ProductsPage";

type AppView = "dashboard" | "business" | "products";

export function App() {
  const { loading, logout, user } = useAuth();
  const [view, setView] = useState<AppView>("dashboard");

  if (loading) {
    return (
      <Box className="loading-screen">
        <CircularProgress />
      </Box>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <Box component="main" className="app-shell">
      <AppBar color="inherit" elevation={0} position="static" className="topbar">
        <Toolbar className="topbar-toolbar">
          <Typography variant="h2">AI Marketing Partner</Typography>
          <Stack direction="row" spacing={1}>
            <Button
              color={view === "dashboard" ? "primary" : "inherit"}
              onClick={() => setView("dashboard")}
              variant={view === "dashboard" ? "contained" : "text"}
            >
              Dashboard
            </Button>
            <Button
              color={view === "business" ? "primary" : "inherit"}
              onClick={() => setView("business")}
              variant={view === "business" ? "contained" : "text"}
            >
              Business
            </Button>
            <Button
              color={view === "products" ? "primary" : "inherit"}
              onClick={() => setView("products")}
              variant={view === "products" ? "contained" : "text"}
            >
              Products
            </Button>
            <Button onClick={logout} variant="outlined">
              Logout
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl">
        {view === "dashboard" ? <DashboardPage /> : null}
        {view === "business" ? <BusinessProfilePage /> : null}
        {view === "products" ? <ProductsPage /> : null}
      </Container>
    </Box>
  );
}
