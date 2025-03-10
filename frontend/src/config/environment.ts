/**
 * Environment configuration with type safety
 */

export interface EnvironmentConfig {
  apiUrl: string;
  apiTimeout: number;
  enableDebug: boolean;
  sentryDsn?: string;
  appVersion: string;
  googleAnalyticsId?: string;
}

// Default development environment configuration
const devConfig: EnvironmentConfig = {
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  apiTimeout: 30000,
  enableDebug: true,
  appVersion: process.env.REACT_APP_VERSION || '0.1.0-dev',
};

// Production environment configuration
const prodConfig: EnvironmentConfig = {
  apiUrl: process.env.REACT_APP_API_URL || '/api',
  apiTimeout: 60000,
  enableDebug: false,
  sentryDsn: process.env.REACT_APP_SENTRY_DSN,
  appVersion: process.env.REACT_APP_VERSION || '0.1.0',
  googleAnalyticsId: process.env.REACT_APP_GA_ID,
};

// Test environment configuration
const testConfig: EnvironmentConfig = {
  apiUrl: 'http://localhost:8000/api',
  apiTimeout: 5000,
  enableDebug: true,
  appVersion: '0.1.0-test',
};

// Determine which config to use based on environment
const getEnvironmentConfig = (): EnvironmentConfig => {
  switch (process.env.NODE_ENV) {
    case 'production':
      return prodConfig;
    case 'test':
      return testConfig;
    case 'development':
    default:
      return devConfig;
  }
};

const config = getEnvironmentConfig();
export default config;
