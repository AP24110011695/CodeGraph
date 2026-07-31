import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { normalizeApiError } from './errors';
import { useRepositoryStore } from '@/core/store/repository.store';

const baseURL = import.meta.env.VITE_API_URL ?? '/api';

export const apiClient = axios.create({
  baseURL,
  timeout: 30_000,
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = typeof window !== 'undefined' ? window.localStorage.getItem('cg_auth_token') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  const repositoryId = useRepositoryStore.getState().activeRepositoryId;
  if (repositoryId) {
    config.headers['X-Repository-Id'] = repositoryId;
  }

  if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
    // Axios may default JSON content-type; multipart must set its own boundary.
    config.headers.delete('Content-Type');
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => Promise.reject(normalizeApiError(error))
);
