import { useState, useCallback, useEffect } from 'react';
import { ApiResponse, ErrorResponse, HttpMethod } from '../types/api';
import { handleApiError, displayErrorMessage, ErrorDisplayMode } from '../utils/errorHandler';
import api from '../services/api';

interface UseApiOptions {
  errorMode?: ErrorDisplayMode;
  autoExecute?: boolean;
  initialData?: any;
  dependencies?: any[];
}

export function useApi<T>(
  endpoint?: string, 
  method: HttpMethod = HttpMethod.GET,
  body?: any,
  options: UseApiOptions = {}
) {
  const [data, setData] = useState<T | null>(options.initialData || null);
  const [loading, setLoading] = useState(options.autoExecute && endpoint ? true : false);
  const [error, setError] = useState<ErrorResponse | null>(null);

  const execute = useCallback(async (
    customEndpoint?: string,
    customMethod?: HttpMethod,
    customBody?: any
  ): Promise<T | null> => {
    const url = customEndpoint || endpoint;
    const requestMethod = customMethod || method;
    const requestBody = customBody !== undefined ? customBody : body;
    
    if (!url) {
      const error: ErrorResponse = { 
        message: 'No endpoint specified for API call', 
        status: 400
      };
      setError(error);
      return null;
    }

    try {
      setLoading(true);
      setError(null);
      
      let response;
      
      switch (requestMethod) {
        case HttpMethod.GET:
          response = await api.get<ApiResponse<T>>(url);
          break;
        case HttpMethod.POST:
          response = await api.post<ApiResponse<T>>(url, requestBody);
          break;
        case HttpMethod.PUT:
          response = await api.put<ApiResponse<T>>(url, requestBody);
          break;
        case HttpMethod.DELETE:
          response = await api.delete<ApiResponse<T>>(url);
          break;
        case HttpMethod.PATCH:
          response = await api.patch<ApiResponse<T>>(url, requestBody);
          break;
      }
      
      const responseData = response.data.data;
      setData(responseData);
      return responseData;
    } catch (err) {
      const errorResponse = handleApiError(err);
      setError(errorResponse);
      
      if (options.errorMode) {
        displayErrorMessage(errorResponse, options.errorMode);
      }
      
      return null;
    } finally {
      setLoading(false);
    }
  }, [endpoint, method, body, options.errorMode]);

  // Auto-execute if configured
  useEffect(() => {
    if (options.autoExecute && endpoint) {
      execute();
    }
  }, [execute, endpoint, options.autoExecute, ...(options.dependencies || [])]);

  const refresh = useCallback(() => {
    if (endpoint) {
      return execute();
    }
    return Promise.resolve(null);
  }, [endpoint, execute]);

  return { data, execute, loading, error, refresh };
}
