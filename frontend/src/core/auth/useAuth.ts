export interface AuthUser {
  id: string;
  email: string;
  name?: string;
}

export interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

/**
 * Auth stub — ready for Clerk / Auth0 / custom JWT.
 * Always returns unauthenticated until a real provider is wired.
 */
export function useAuth(): AuthState {
  return {
    user: null,
    isAuthenticated: false,
    isLoading: false,
  };
}
