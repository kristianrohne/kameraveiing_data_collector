import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-oauth-callback',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="callback-container">
      <div class="loading-message">
        <h2>Logger inn...</h2>
        <p>Vennligst vent mens vi fullfører innloggingen din.</p>
        <div class="spinner"></div>
      </div>
    </div>
  `,
  styles: [`
    .callback-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background-color: #f5f5f5;
    }

    .loading-message {
      text-align: center;
      background: white;
      padding: 2rem;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .loading-message h2 {
      color: #2c5530;
      margin-bottom: 1rem;
    }

    .loading-message p {
      color: #666;
      margin-bottom: 2rem;
    }

    .spinner {
      border: 4px solid #f3f3f3;
      border-top: 4px solid #2c5530;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 0 auto;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `]
})
export class OAuthCallbackComponent implements OnInit {

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    // Get token from query parameters
    this.route.queryParams.subscribe(params => {
      const token = params['token'];
      const error = params['error'];

      if (error) {
        console.error('OAuth error:', error);
        this.router.navigate(['/login'], { 
          queryParams: { error: 'OAuth innlogging mislyktes. Vennligst prøv igjen.' }
        });
        return;
      }

      if (token) {
        // Handle successful OAuth callback
        this.authService.handleOAuthCallback(token);
        
        // Wait a moment for user info to load, then redirect to upload
        setTimeout(() => {
          this.router.navigate(['/upload']);
        }, 1000);
      } else {
        console.error('No token received from OAuth callback');
        this.router.navigate(['/login'], { 
          queryParams: { error: 'Ingen token mottatt. Vennligst prøv igjen.' }
        });
      }
    });
  }
}
