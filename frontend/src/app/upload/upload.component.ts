
import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';

interface PigUpload {
  weight: number | null;
  selectedFiles: File[];
}

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent {
  pigs: PigUpload[] = [{ weight: null, selectedFiles: [] }];
  uploading = false;
  uploadProgress = 0;
  uploadResults: string[] = [];

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  addPig() {
    this.pigs.push({ weight: null, selectedFiles: [] });
  }

  removePig(index: number) {
    if (this.pigs.length > 1) {
      this.pigs.splice(index, 1);
    }
  }

  onFileSelected(event: any, pigIndex: number) {
    const files = Array.from(event.target.files) as File[];
    this.pigs[pigIndex].selectedFiles = [];
    for (const file of files) {
      if (file.type.startsWith('image/')) {
        this.pigs[pigIndex].selectedFiles.push(file);
  }
    }
  }

  async uploadFiles() {
    const totalFiles = this.pigs.reduce((total, pig) => total + pig.selectedFiles.length, 0);
    if (totalFiles === 0) {
      this.uploadResults = ['❌ Ingen filer valgt'];
      return;
    }
    for (let i = 0; i < this.pigs.length; i++) {
      const pig = this.pigs[i];
      if (pig.selectedFiles.length > 0) {
        if (!pig.weight) {
          this.uploadResults = [`❌ Gris ${i + 1}: Vennligst fyll ut vekt`];
          return;
        }
        if (pig.weight < 1 || pig.weight > 400) {
          this.uploadResults = [`❌ Gris ${i + 1}: Vekt må være mellom 1 og 400 kg`];
          return;
        }
      }
    }
    this.uploading = true;
    this.uploadProgress = 0;
    this.uploadResults = [];
    let processedFiles = 0;
    for (let pigIndex = 0; pigIndex < this.pigs.length; pigIndex++) {
      const pig = this.pigs[pigIndex];
      if (pig.selectedFiles.length === 0) continue;
      for (let fileIndex = 0; fileIndex < pig.selectedFiles.length; fileIndex++) {
        const file = pig.selectedFiles[fileIndex];
        try {
          await this.uploadSingleFile(file, file.name, pig.weight!);
          this.uploadResults.push(`✅ Gris ${pigIndex + 1} - ${file.name} - Lastet opp`);
        } catch (error) {
          this.uploadResults.push(`❌ Gris ${pigIndex + 1} - ${file.name} - Feil ved opplasting`);
        }
        processedFiles++;
        this.uploadProgress = (processedFiles / totalFiles) * 100;
      }
    }
    setTimeout(() => {
        this.uploading = false;
      this.pigs = [{ weight: null, selectedFiles: [] }];
      this.cdr.markForCheck();
    }, 500);
  }

  private uploadSingleFile(file: File, originalName: string, weight: number): Promise<any> {
    return new Promise((resolve, reject) => {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('weight', weight.toString());
      const headers = this.authService.getAuthHeaders();
      this.http.post('/api/upload', formData, { headers }).subscribe({
        next: (event: any) => {
          resolve(event.body || event);
        },
        error: (error) => reject(error)
      });
    });
  }

  clearResults() {
    this.uploadResults = [];
    this.uploadProgress = 0;
    this.pigs = [{ weight: null, selectedFiles: [] }];
  }

  goToIntro() {
    this.router.navigate(['/intro']);
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
