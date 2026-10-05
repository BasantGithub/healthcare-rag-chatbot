import { ApplicationInsights } from '@microsoft/applicationinsights-web';
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// Initialize Application Insights
if (process.env.REACT_APP_APPINSIGHTS_CONNECTION_STRING) {
  const appInsights = new ApplicationInsights({
    config: {
      connectionString: process.env.REACT_APP_APPINSIGHTS_CONNECTION_STRING
    }
  });
  appInsights.loadAppInsights();
  appInsights.trackPageView();
} else {
  console.warn("⚠️ App Insights connection string not provided");
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

reportWebVitals();
