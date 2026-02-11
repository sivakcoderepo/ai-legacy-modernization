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
    useCases: '',
    domainModel: '',
    domainMapping: '',
    backendDesign: '',
    frontendDesign: '',
    cloudDesign: '',
    targetDomainModel: '',
    frontendZipUrl: '',
    backendZipUrl: '',
    history: []
  };

  isProcessing = false;
  uploadedFileName = '';
  targetDomainFileName = '';
  
  // Track which content has been received (for background streaming)
  private receivedContent = {
    businessLogic: false,
    useCases: false,
    domainModel: false,
    domainMapping: false,
    backendDesign: false,
    frontendDesign: false,
    cloudDesign: false,
    frontendZip: false,
    backendZip: false
  };
  
  steps: StepInfo[] = [
    { step: ModernizationStep.UPLOAD, title: 'Upload VB Code', description: 'Upload your legacy VB application', icon: '📁' },
    { step: ModernizationStep.BUSINESS_LOGIC, title: 'Business Logic', description: 'AI extracts and explains business rules', icon: '🔍' },
    { step: ModernizationStep.USE_CASES, title: 'Use Cases (Gherkin)', description: 'Generate BDD scenarios', icon: '📋' },
    { step: ModernizationStep.DOMAIN_MODEL, title: 'Domain Model', description: 'Extract domain entities and contexts', icon: '🏗️' },
    { step: ModernizationStep.BACKEND_DESIGN, title: 'Backend Design', description: 'Design Spring Boot REST API', icon: '⚙️' },
    { step: ModernizationStep.FRONTEND_DESIGN, title: 'Frontend Design', description: 'Create Angular components', icon: '🎨' },
    { step: ModernizationStep.CLOUD_DESIGN, title: 'Cloud Architecture', description: 'AWS deployment strategy', icon: '☁️' },
    { step: ModernizationStep.CODE_GENERATION, title: 'Code Generation', description: 'Generate deployable apps', icon: '💻' },
    { step: ModernizationStep.COMPLETE, title: 'Complete', description: 'Modernization complete!', icon: '✅' }
  ];

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

  onTargetDomainSelected(event: any): void {
    const file: File = event.target.files[0];
    if (file) {
      this.targetDomainFileName = file.name;
      this.modernizationService.readVBFile(file)
        .then(content => {
          this.state.targetDomainModel = content;
          console.log('Target domain model loaded');
        })
        .catch(error => {
          console.error('Error reading target domain file:', error);
          alert('Error reading target domain file. Please try again.');
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
    this.state.useCases = '';
    this.state.domainModel = '';
    this.state.domainMapping = '';
    this.state.backendDesign = '';
    this.state.frontendDesign = '';
    this.state.cloudDesign = '';
    this.state.frontendZipUrl = '';
    this.state.backendZipUrl = '';
    
    // Reset received content tracking
    this.receivedContent = {
      businessLogic: false,
      useCases: false,
      domainModel: false,
      domainMapping: false,
      backendDesign: false,
      frontendDesign: false,
      cloudDesign: false,
      frontendZip: false,
      backendZip: false
    };

    this.state.history.push({
      role: 'user',
      content: this.state.vbCode
    });

    console.log('🚀 Starting stream subscription...');
    let chunkCount = 0;

    this.modernizationService.analyzeCodeStream(this.state.vbCode, this.state.targetDomainModel)
      .subscribe({
        next: (chunk) => {
          chunkCount++;
          console.log(`[CHUNK ${chunkCount}]`, Object.keys(chunk));
          
          // Stream content into state variables
          // Content accumulates in background while user is on current step
          
          if (chunk.business_logic) {
            this.state.businessLogic += chunk.business_logic;
            if (!this.receivedContent.businessLogic) {
              console.log('✅ Business Logic: Started receiving');
              this.receivedContent.businessLogic = true;
            }
          }
          
          if (chunk.use_cases) {
            this.state.useCases += chunk.use_cases;
            if (!this.receivedContent.useCases) {
              console.log('✅ Use Cases: Started receiving');
              this.receivedContent.useCases = true;
            }
          }
          
          if (chunk.domain_model) {
            this.state.domainModel += chunk.domain_model;
            if (!this.receivedContent.domainModel) {
              console.log('✅ Domain Model: Started receiving');
              this.receivedContent.domainModel = true;
            }
          }
          
          if (chunk.domain_mapping) {
            this.state.domainMapping += chunk.domain_mapping;
            if (!this.receivedContent.domainMapping) {
              console.log('✅ Domain Mapping: Started receiving');
              this.receivedContent.domainMapping = true;
            }
          }
          
          if (chunk.backend_design) {
            this.state.backendDesign += chunk.backend_design;
            if (!this.receivedContent.backendDesign) {
              console.log('✅ Backend Design: Started receiving');
              this.receivedContent.backendDesign = true;
            }
          }
          
          if (chunk.frontend_design) {
            this.state.frontendDesign += chunk.frontend_design;
            if (!this.receivedContent.frontendDesign) {
              console.log('✅ Frontend Design: Started receiving');
              this.receivedContent.frontendDesign = true;
            }
          }
          
          if (chunk.cloud_design) {
            this.state.cloudDesign += chunk.cloud_design;
            if (!this.receivedContent.cloudDesign) {
              console.log('✅ Cloud Design: Started receiving');
              this.receivedContent.cloudDesign = true;
            }
          }
          
          if (chunk.frontend_zip_url) {
            this.state.frontendZipUrl = chunk.frontend_zip_url;
            if (!this.receivedContent.frontendZip) {
              console.log('✅ Frontend ZIP: Ready');
              this.receivedContent.frontendZip = true;
            }
          }
          
          if (chunk.backend_zip_url) {
            this.state.backendZipUrl = chunk.backend_zip_url;
            if (!this.receivedContent.backendZip) {
              console.log('✅ Backend ZIP: Ready');
              this.receivedContent.backendZip = true;
            }
          }
          
          if (chunk.status) {
            console.log('📢 Status:', chunk.status);
          }
        },
        error: (error) => {
          console.error('❌ Stream error:', error);
          this.isProcessing = false;
          alert('Error during analysis. Please check if the backend is running.');
        },
        complete: () => {
          console.log(`✅ Stream complete! Total chunks: ${chunkCount}`);
          this.isProcessing = false;
          
          // Show summary of what was received
          console.log('📊 Content received:', this.receivedContent);
        }
      });
  }

  approveAndContinue(): void {
    // User manually advances to next step
    // Content for future steps is already streaming in background
    if (this.state.currentStep < ModernizationStep.COMPLETE) {
      this.state.currentStep++;
      console.log(`✅ User approved. Moving to step ${this.state.currentStep}`);
    }
  }

  rejectAndModify(): void {
    alert('Modification feature coming soon! You can edit the output manually for now.');
  }

  reset(): void {
    this.state = {
      vbCode: '',
      currentStep: ModernizationStep.UPLOAD,
      businessLogic: '',
      useCases: '',
      domainModel: '',
      domainMapping: '',
      backendDesign: '',
      frontendDesign: '',
      cloudDesign: '',
      targetDomainModel: '',
      frontendZipUrl: '',
      backendZipUrl: '',
      history: []
    };
    this.uploadedFileName = '';
    this.targetDomainFileName = '';
    this.isProcessing = false;
    
    this.receivedContent = {
      businessLogic: false,
      useCases: false,
      domainModel: false,
      domainMapping: false,
      backendDesign: false,
      frontendDesign: false,
      cloudDesign: false,
      frontendZip: false,
      backendZip: false
    };
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

  downloadZip(url: string, filename: string): void {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
  }

  getStepStatus(step: ModernizationStep): 'completed' | 'current' | 'pending' {
    if (step < this.state.currentStep) return 'completed';
    if (step === this.state.currentStep) return 'current';
    return 'pending';
  }

  canProceedToNextStep(): boolean {
    // Check if current step has content AND streaming is complete for that step
    switch (this.state.currentStep) {
      case ModernizationStep.BUSINESS_LOGIC:
        return this.state.businessLogic.length > 0 && !this.isProcessing;
      case ModernizationStep.USE_CASES:
        return this.state.useCases.length > 0;
      case ModernizationStep.DOMAIN_MODEL:
        return this.state.domainModel.length > 0;
      case ModernizationStep.BACKEND_DESIGN:
        return this.state.backendDesign.length > 0;
      case ModernizationStep.FRONTEND_DESIGN:
        return this.state.frontendDesign.length > 0;
      case ModernizationStep.CLOUD_DESIGN:
        return this.state.cloudDesign.length > 0;
      case ModernizationStep.CODE_GENERATION:
        return this.state.frontendZipUrl.length > 0 && this.state.backendZipUrl.length > 0;
      default:
        return false;
    }
  }

  getCurrentStepContent(): string {
    switch (this.state.currentStep) {
      case ModernizationStep.BUSINESS_LOGIC:
        return this.state.businessLogic;
      case ModernizationStep.USE_CASES:
        return this.state.useCases;
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
