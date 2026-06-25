import { Box, Container } from "@mui/material";

import { DashboardPage } from "../pages/Dashboard/DashboardPage";

export function App() {
  return (
    <Box component="main" className="app-shell">
      <Container maxWidth="xl">
        <DashboardPage />
      </Container>
    </Box>
  );
}
