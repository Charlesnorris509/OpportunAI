import { ErrorResponse } from '../types/api';

export const handleApiError = (error: any): ErrorResponse => {
  if (error.response) {
    // Handle API error responses
    return {
      message: error.response.data.message || 'An error occurred',
      status: error.response.status,
      errors: error.response.data.errors,
      timestamp: new Date().toISOString(),
      path: error.response.config?.url,
    };
  } else if (error.request) {
    // Handle network errors (request made, no response)
    return {
      message: 'No response from server. Please check your connection.',
      status: 0,
      timestamp: new Date().toISOString(),
    };
  }
  
  // Handle other types of errors
  return {
    message: error.message || 'Network error occurred',
    status: 500,
    timestamp: new Date().toISOString(),
  };
};

export enum ErrorDisplayMode {
  CONSOLE = 'console',
  TOAST = 'toast',
  ALERT = 'alert',
  INLINE = 'inline',
}

export const displayErrorMessage = (
  error: ErrorResponse, 
  mode: ErrorDisplayMode = ErrorDisplayMode.CONSOLE,
  duration?: number
) => {
  // Log all errors to console for debugging
  console.error('Error:', error);
  
  switch (mode) {
    case ErrorDisplayMode.TOAST:
      // Implementation will depend on your toast library (e.g., react-toastify)
      // Example: toast.error(error.message, { autoClose: duration });
      break;
    case ErrorDisplayMode.ALERT:
      alert(error.message);
      break;
    case ErrorDisplayMode.INLINE:
      // This mode is meant to be used by components to display the error themselves
      return error;
    case ErrorDisplayMode.CONSOLE:
    default:
      // Already logged to console above
      break;
  }
};

export const formatValidationErrors = (errors?: Record<string, string[]>) => {
  if (!errors) return '';
  
  return Object.entries(errors)
    .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
    .join('\n');
};
