import React from "react";
import ReactDOM from "react-dom/client";
import "@fontsource/fraunces/600.css";
import "@fontsource/fraunces/700.css";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "leaflet/dist/leaflet.css";
import "./index.css";
import App from "./App";
import { AuthProvider } from "./state/auth";
import { DestinationProvider } from "./state/destination";
import { ToastProvider } from "./state/toast";
import { LanguageProvider } from "./state/language";
import { BrowserRouter } from "react-router-dom";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ToastProvider>
        <DestinationProvider>
          <LanguageProvider>
            <AuthProvider>
              <App />
            </AuthProvider>
          </LanguageProvider>
        </DestinationProvider>
      </ToastProvider>
    </BrowserRouter>
  </React.StrictMode>,
);