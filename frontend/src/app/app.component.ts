import { Component, OnInit } from '@angular/core';
import { Router, RouterOutlet, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from './auth.service';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  isAuthenticated = false;
  currentUser: any = null;
  currentRoute = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    // Subscribe to current user changes
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      this.isAuthenticated = !!user;
      console.log('🔄 App component - User changed:', { user, isAuthenticated: this.isAuthenticated });
    });

    // Subscribe to router events to track current route
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      this.currentRoute = event.url;
    });
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
