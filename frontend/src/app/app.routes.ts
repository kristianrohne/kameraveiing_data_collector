import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { UploadComponent } from './upload/upload.component';
import { OAuthCallbackComponent } from './oauth-callback/oauth-callback.component';
import { LogoutSuccessComponent } from './logout-success/logout-success.component';
import { IntroComponent } from './intro/intro.component';
import { authGuard, guestGuard } from './auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { 
    path: 'login', 
    component: LoginComponent,
    canActivate: [guestGuard]
  },
  { 
    path: 'auth/callback', 
    component: OAuthCallbackComponent
  },
  { 
    path: 'logout-success', 
    component: LogoutSuccessComponent
  },
  { 
    path: 'upload', 
    component: UploadComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'intro', 
    component: IntroComponent,
    canActivate: [authGuard]
  },
  { path: '**', redirectTo: '/login' }
];
