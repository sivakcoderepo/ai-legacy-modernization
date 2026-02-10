import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ModernizationService } from '../../services/modernization.service';
import { ModernizationState, ModernizationStep, StepInfo } from '../../models/modernization.model';

@Component({
  selector: 'app-modernization',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './modernization.component.html',
  styleUrls: ['./modernization.component.css']
})
export class ModernizationComponent {
  state: ModernizationState = {
    vbCode: '',
    currentStep: ModernizationStep.UPLOAD,
    businessLogic: '',
    domainModel: '',
    backendDesign: '',
    frontendDesign: '',
    cloudDesign: '',
    history: []
  };

  isProcessing = false;
  uploadedFileName = '';
  
  steps: StepInfo[] = [
    { step: ModernizationStep.UPLOAD, title: 'Upload VB Code', description: 'Upload your legacy VB application', icon: '📁' },
    { step: ModernizationStep.BUSINESS_LOGIC, title: 'Business Logic Analysis', description: 'AI extracts and explains business rules', icon: '🔍' },
    { step: ModernizationStep.DOMAIN_MODEL, title: 'Domain Model', description: 'Generate domain entities and bounded contexts', icon: '🏗️' },
    { step: ModernizationStep.BACKEND_DESIGN, title: 'Backend Design', description: 'Design Spring Boot REST API architecture', icon: '⚙️' },
    { step: ModernizationStep.FRONTEND_DESIGN, title: 'Frontend Design', description: 'Create Angular UI components', icon: '🎨' },
    { step: ModernizationStep.CLOUD_DESIGN, title: 'Cloud Architecture', description: 'AWS deployment and containerization', icon: '☁️' },
    { step: ModernizationStep.COMPLETE, title: 'Complete', description: 'Modernization complete!', icon: '✅' }
  ];

  // Expose enum to template
  ModernizationStep = ModernizationStep;

  constructor(private modernizationService: ModernizationService) {}

  onFileSelected(event: any): void {
    const file: File = event.target.files[0];
    if (file) {
      this.uploadedFileName = file.name;
      this.modernizationService.readVBFile(file)
        .then(content => {
          this.state.vbCode = content;
        })
        .catch(error => {
          console.error('Error reading file:', error);
          alert('Error reading file. Please try again.');
        });
    }
  }

  startAnalysis(): void {
    if (!this.state.vbCode.trim()) {
      alert('Please upload a VB file first.');
      return;
    }

    this.isProcessing = true;
    this.state.currentStep = ModernizationStep.BUSINESS_LOGIC;
    this.state.history = [];
    
    // Reset all outputs
    this.state.businessLogic = '';
    this.state.domainModel = '';
    this.state.backendDesign = '';
    this.state.frontendDesign = '';
    this.state.cloudDesign = '';

    // Add user message to history
    this.state.history.push({
      role: 'user',
      content: this.state.vbCode
    });

    this.modernizationService.analyzeCodeStream(this.state.vbCode)
      .subscribe({
        next: (chunk) => {
          // Handle different types of chunks
          if (chunk.business_logic) {
            this.state.businessLogic += chunk.business_logic;
          }
          if (chunk.domain_model) {
            this.state.domainModel += chunk.domain_model;
          }
          if (chunk.backend_design) {
            this.state.backendDesign += chunk.backend_design;
          }
          if (chunk.frontend_design) {
            this.state.frontendDesign += chunk.frontend_design;
          }
          if (chunk.cloud_design) {
            this.state.cloudDesign += chunk.cloud_design;
          }
        },
        error: (error) => {
          console.error('Stream error:', error);
          this.isProcessing = false;
          alert('Error during analysis. Please check if the backend is running at http://127.0.0.1:8000');
        },
        complete: () => {
          this.isProcessing = false;
        }
      });
  }

  approveAndContinue(): void {
    // Move to next step
    if (this.state.currentStep < ModernizationStep.COMPLETE) {
      this.state.currentStep++;
    }
  }

  rejectAndModify(): void {
    // Allow user to modify the current step's output
    alert('Modification feature coming soon! You can edit the output manually for now.');
  }

  reset(): void {
    this.state = {
      vbCode: '',
      currentStep: ModernizationStep.UPLOAD,
      businessLogic: '',
      domainModel: '',
      backendDesign: '',
      frontendDesign: '',
      cloudDesign: '',
      history: []
    };
    this.uploadedFileName = '';
    this.isProcessing = false;
  }

  downloadOutput(stepName: string, content: string): void {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${stepName}-output.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
  }

  getStepStatus(step: ModernizationStep): 'completed' | 'current' | 'pending' {
    if (step < this.state.currentStep) return 'completed';
    if (step === this.state.currentStep) return 'current';
    return 'pending';
  }

  canProceedToNextStep(): boolean {
    switch (this.state.currentStep) {
      case ModernizationStep.BUSINESS_LOGIC:
        return this.state.businessLogic.length > 0 && !this.isProcessing;
      case ModernizationStep.DOMAIN_MODEL:
        return this.state.domainModel.length > 0 && !this.isProcessing;
      case ModernizationStep.BACKEND_DESIGN:
        return this.state.backendDesign.length > 0 && !this.isProcessing;
      case ModernizationStep.FRONTEND_DESIGN:
        return this.state.frontendDesign.length > 0 && !this.isProcessing;
      case ModernizationStep.CLOUD_DESIGN:
        return this.state.cloudDesign.length > 0 && !this.isProcessing;
      default:
        return false;
    }
  }

  getCurrentStepContent(): string {
    switch (this.state.currentStep) {
      case ModernizationStep.BUSINESS_LOGIC:
        return this.state.businessLogic;
      case ModernizationStep.DOMAIN_MODEL:
        return this.state.domainModel;
      case ModernizationStep.BACKEND_DESIGN:
        return this.state.backendDesign;
      case ModernizationStep.FRONTEND_DESIGN:
        return this.state.frontendDesign;
      case ModernizationStep.CLOUD_DESIGN:
        return this.state.cloudDesign;
      default:
        return '';
    }
  }
}
