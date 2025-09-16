import { Component, OnInit } from '@angular/core';
import { AuthService } from '../auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div style="padding: 40px; text-align: center; max-width: 600px; margin: 0 auto;">
      <h2>🐷 Kameraveiing Data Collector</h2>
      <p style="margin: 20px 0;">Velkommen! Klikk for å logge inn med Animalia SSO.</p>
      
      <div style="margin: 30px 0;">
        <button 
          (click)="login()" 
          [disabled]="isLoading"
          style="background: #2196F3; color: white; border: none; padding: 15px 30px; border-radius: 5px; font-size: 16px; cursor: pointer;">
          {{ isLoading ? 'Kobler til...' : 'Logg inn med Animalia SSO' }}
        </button>
      </div>
      
      <div *ngIf="errorMessage" style="color: red; margin-top: 20px;">
        ❌ {{ errorMessage }}
      </div>
      
      <div *ngIf="debugInfo" style="margin-top: 30px; padding: 20px; background: #f5f5f5; border-radius: 5px; text-align: left;">
        <strong>Debug Info:</strong>
        <pre>{{ debugInfo }}</pre>
      </div>
    </div>
  `,
  styles: []
})
export class LoginComponent implements OnInit {
  isLoading = false;
  errorMessage = '';
  debugInfo = '';

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    console.log('Login component loaded');
    // Automatically start OAuth flow
    this.login();
  }

  login(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.debugInfo = 'Starting login process...';
    
    console.log('🔄 User clicked login button');
    this.authService.redirectToOAuth();
  }
}
