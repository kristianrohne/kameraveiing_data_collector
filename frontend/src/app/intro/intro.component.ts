import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-intro',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './intro.component.html',
  styleUrls: ['./intro.component.css']
})
export class IntroComponent {
  currentSlide = 0;
  totalSlides = 3;

  constructor(private router: Router) {}

  nextSlide() {
    if (this.currentSlide < this.totalSlides - 1) {
      this.currentSlide++;
    }
  }

  prevSlide() {
    if (this.currentSlide > 0) {
      this.currentSlide--;
    }
  }

  finishIntro() {
    localStorage.setItem("seenIntro", "true");
    this.router.navigate(['/upload']);
  }

  goToUpload() {
    this.router.navigate(['/upload']);
  }
}
