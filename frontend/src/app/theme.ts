import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#176B5B",
    },
    secondary: {
      main: "#B85C38",
    },
    background: {
      default: "#F7F8F5",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#17211D",
      secondary: "#5D6861",
    },
  },
  shape: {
    borderRadius: 8,
  },
  typography: {
    fontFamily:
      'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    h1: {
      fontSize: "2.5rem",
      fontWeight: 700,
      letterSpacing: 0,
    },
    h2: {
      fontSize: "1.5rem",
      fontWeight: 700,
      letterSpacing: 0,
    },
  },
});
