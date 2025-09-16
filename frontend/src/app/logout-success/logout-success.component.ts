import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-logout-success',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="logout-success-container">
      <div class="logout-success-card">
        <h2>✅ Du er nå logget ut</h2>
        <p>Du har blitt logget ut av både applikasjonen og Animalia SSO.</p>
        <p class="success-message">SSO-utlogging vellykket</p>
        
        <button type="button" class="login-again-btn" (click)="goToLogin()">
          Logg inn igjen
        </button>
      </div>
    </div>
  `,
  styles: [`
    .logout-success-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 20px;
    }

    .logout-success-card {
      background: white;
      padding: 40px;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
      text-align: center;
      max-width: 400px;
      width: 100%;
    }

    h2 {
      color: #333;
      margin-bottom: 20px;
      font-size: 24px;
    }

    p {
      color: #666;
      margin-bottom: 20px;
      line-height: 1.5;
    }

    .success-message {
      background: #d4edda;
      color: #155724;
      padding: 10px;
      border-radius: 6px;
      border: 1px solid #c3e6cb;
      font-weight: bold;
      margin-bottom: 30px;
    }

    .login-again-btn {
      background: #667eea;
      color: white;
      border: none;
      padding: 12px 30px;
      border-radius: 6px;
      font-size: 16px;
      cursor: pointer;
      transition: background-color 0.3s;
    }

    .login-again-btn:hover {
      background: #5a6fd8;
    }
  `]
})
export class LogoutSuccessComponent {
  constructor(private router: Router) {}

  goToLogin() {
    this.router.navigate(['/login']);
  }
}
