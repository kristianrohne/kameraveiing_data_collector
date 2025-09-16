import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { isPlatformBrowser } from '@angular/common';

export interface User {
  id: string;
  email: string;
  full_name: string;
  farmer_id: string;
  is_admin: boolean;
}

export interface OAuthLoginResponse {
  auth_url: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = '/api';
  private readonly TOKEN_KEY = 'auth_token';
  
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.loadUserFromToken();
  }

  private loadUserFromToken(): void {
    const token = this.getToken();
    if (token) {
      // Verify token with backend
      this.getCurrentUser().subscribe({
        next: (response) => this.currentUserSubject.next(response.user),
        error: () => {
          // Token is invalid, remove it and set user to null
          this.removeToken();
          this.currentUserSubject.next(null);
        }
      });
    } else {
      // No token, ensure user state is null
      this.currentUserSubject.next(null);
    }
  }

  getCurrentUser(): Observable<{user: User}> {
    return this.http.get<{user: User}>(`${this.API_URL}/auth/me`, {
      headers: this.getAuthHeaders(),
      withCredentials: true
    });
  }

  logout(): void {
    // Call backend logout endpoint
  this.http.post(`${this.API_URL}/auth/logout`, { sso_logout: true }, { withCredentials: true }).subscribe({
      next: (response: any) => {
        // Clear local token and user state
        this.removeToken();
        this.currentUserSubject.next(null);
        
        // If backend provides SSO logout URL, redirect to it
        if (response.sso_logout_url && typeof window !== 'undefined') {
          window.location.href = response.sso_logout_url;
        }
      },
      error: (error) => {
        console.error('Logout error:', error);
        // Still clear local state even if SSO logout fails
        this.removeToken();
        this.currentUserSubject.next(null);
      }
    });
  }

  isAuthenticated(): boolean {
    return !!this.getToken() && !!this.currentUserSubject.value;
  }

  isAdmin(): boolean {
    const user = this.currentUserSubject.value;
    return user?.is_admin || false;
  }

  getToken(): string | null {
    if (isPlatformBrowser(this.platformId)) {
      return localStorage.getItem(this.TOKEN_KEY);
    }
    return null;
  }

  private setToken(token: string): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem(this.TOKEN_KEY, token);
    }
  }

  private removeToken(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem(this.TOKEN_KEY);
    }
  }

  getAuthHeaders(): HttpHeaders {
    const token = this.getToken();
    return new HttpHeaders({
      'Authorization': token ? `Bearer ${token}` : ''
    });
  }

  // OAuth functions
  initiateOAuthLogin(): Observable<OAuthLoginResponse> {
    console.log('🔗 Calling backend OAuth endpoint:', `${this.API_URL}/auth/oauth/login`);
  return this.http.get<OAuthLoginResponse>(`${this.API_URL}/auth/oauth/login`, { withCredentials: true });
  }

  redirectToOAuth(): void {
    console.log('🔄 Starting OAuth redirect...');
    this.initiateOAuthLogin().subscribe({
      next: (response) => {
        console.log('✅ OAuth URL received:', response.auth_url);
        // Only redirect in browser, not during SSR
        if (typeof window !== 'undefined') {
          console.log('🎯 Redirecting to OAuth URL...');
          window.location.href = response.auth_url;
        } else {
          console.log('❌ Window is undefined, cannot redirect');
        }
      },
      error: (error) => {
        console.error('❌ OAuth login initiation failed:', error);
      }
    });
  }

  handleOAuthCallback(token: string): void {
    if (token) {
      this.setToken(token);
      this.getCurrentUser().subscribe({
        next: (response) => {
          this.currentUserSubject.next(response.user);
        },
        error: (error) => {
          console.error('Failed to get user info after OAuth:', error);
          this.logout();
        }
      });
    }
  }
}
