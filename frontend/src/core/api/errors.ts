import axios from 'axios';

export type ApiErrorCode = string;

export interface APIError {
  code: ApiErrorCode;
  message: string;
  status: number;
  detail?: unknown;
}

export function isAPIError(value: unknown): value is APIError {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.code === 'string' &&
    typeof candidate.message === 'string' &&
    typeof candidate.status === 'number'
  );
}

export function normalizeApiError(error: unknown): APIError {
  if (isAPIError(error)) return error;

  if (axios.isAxiosError(error)) {
    const status = error.response?.status ?? 0;
    const data = error.response?.data as
      | { detail?: unknown; code?: string; message?: string }
      | undefined;
    const detail = data?.detail;
    const messageFromDetail = Array.isArray(detail)
      ? detail
          .map((item) => (typeof item === 'object' ? JSON.stringify(item) : String(item)))
          .join('; ')
      : typeof detail === 'string'
        ? detail
        : undefined;
    const message =
      data?.message ?? messageFromDetail ?? error.message ?? 'Unexpected API error';

    return {
      code: data?.code ?? (status ? `http_${status}` : 'network_error'),
      message,
      status,
      detail,
    };
  }

  if (error instanceof Error) {
    return {
      code: 'client_error',
      message: error.message,
      status: 0,
    };
  }

  return {
    code: 'unknown_error',
    message: 'An unknown error occurred',
    status: 0,
    detail: error,
  };
}
