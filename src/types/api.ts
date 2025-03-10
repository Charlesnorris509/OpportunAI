export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface ErrorResponse {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
  timestamp?: string;
  path?: string;
  requestId?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  DELETE = 'DELETE',
  PATCH = 'PATCH'
}

export interface ApiRequestConfig {
  method: HttpMethod;
  url: string;
  data?: any;
  params?: any;
  headers?: Record<string, string>;
}
