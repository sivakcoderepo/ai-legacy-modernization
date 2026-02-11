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
  
  // Track which steps have received content (for showing approve button early)
  private stepsWithContent: Set<ModernizationStep> = new Set();
  
  // Track if we're currently streaming content for the active step
  private isStreamingCurrentStep = false;
  
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
    this.isStreamingCurrentStep = true;
    this.state.currentStep = ModernizationStep.BUSINESS_LOGIC;
    this.state.history = [];
    this.stepsWithContent.clear();
    
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

    this.state.history.push({
      role: 'user',
      content: this.state.vbCode
    });

    console.log('🚀 Starting stream subscription...');
    let chunkCount = 0;
    let lastChunkTime = Date.now();

    this.modernizationService.analyzeCodeStream(this.state.vbCode, this.state.targetDomainModel)
      .subscribe({
        next: (chunk) => {
          chunkCount++;
          const now = Date.now();
          console.log(`[CHUNK ${chunkCount}] (${now - lastChunkTime}ms)`, Object.keys(chunk));
          lastChunkTime = now;
          
          // Business Logic
          if (chunk.business_logic) {
            this.state.businessLogic += chunk.business_logic;
            this.stepsWithContent.add(ModernizationStep.BUSINESS_LOGIC);
            
            // If we're on business logic step and receiving content, mark as streaming
            if (this.state.currentStep === ModernizationStep.BUSINESS_LOGIC) {
              this.isStreamingCurrentStep = true;
            }
          }
          
          // Use Cases
          if (chunk.use_cases) {
            this.state.useCases += chunk.use_cases;
            this.stepsWithContent.add(ModernizationStep.USE_CASES);
            
            if (this.state.currentStep === ModernizationStep.USE_CASES) {
              this.isStreamingCurrentStep = true;
            }
          }
          
          // Domain Model
          if (chunk.domain_model) {
            this.state.domainModel += chunk.domain_model;
            this.stepsWithContent.add(ModernizationStep.DOMAIN_MODEL);
            
            if (this.state.currentStep === ModernizationStep.DOMAIN_MODEL) {
              this.isStreamingCurrentStep = true;
            }
          }
          
          // Domain Mapping
          if (chunk.domain_mapping) {
            this.state.domainMapping += chunk.domain_mapping;
          }
          
          // Backend Design
          if (chunk.backend_design) {
            this.state.backendDesign += chunk.backend_design;
            this.stepsWithContent.add(ModernizationStep.BACKEND_DESIGN);
            
            if (this.state.currentStep === ModernizationStep.BACKEND_DESIGN) {
              this.isStreamingCurrentStep = true;
            }
          }
          
          // Frontend Design
          if (chunk.frontend_design) {
            this.state.frontendDesign += chunk.frontend_design;
            this.stepsWithContent.add(ModernizationStep.FRONTEND_DESIGN);
            
            if (this.state.currentStep === ModernizationStep.FRONTEND_DESIGN) {
              this.isStreamingCurrentStep = true;
            }
          }
          
          // Cloud Design
          if (chunk.cloud_design) {
            this.state.cloudDesign += chunk.cloud_design;
            this.stepsWithContent.add(ModernizationStep.CLOUD_DESIGN);
            
            if (this.state.currentStep === ModernizationStep.CLOUD_DESIGN) {
              this.isStreamingCurrentStep = true;
            }
          }
          
          // ZIPs
          if (chunk.frontend_zip_url) {
            this.state.frontendZipUrl = chunk.frontend_zip_url;
            this.stepsWithContent.add(ModernizationStep.CODE_GENERATION);
          }
          
          if (chunk.backend_zip_url) {
            this.state.backendZipUrl = chunk.backend_zip_url;
            this.stepsWithContent.add(ModernizationStep.CODE_GENERATION);
          }
          
          // After 2 seconds of no chunks for current step, consider it done
          setTimeout(() => {
            if (Date.now() - lastChunkTime > 2000) {
              this.isStreamingCurrentStep = false;
              console.log(`✅ Step ${this.state.currentStep} streaming appears complete`);
            }
          }, 2100);
        },
        error: (error) => {
          console.error('❌ Stream error:', error);
          this.isProcessing = false;
          this.isStreamingCurrentStep = false;
          alert('Error during analysis. Please check if the backend is running.');
        },
        complete: () => {
          console.log(`✅ Stream complete! Total chunks: ${chunkCount}`);
          this.isProcessing = false;
          this.isStreamingCurrentStep = false;
        }
      });
  }

  approveAndContinue(): void {
    if (this.state.currentStep < ModernizationStep.COMPLETE) {
      this.state.currentStep++;
      this.isStreamingCurrentStep = false; // Reset for new step
      console.log(`✅ User approved. Moving to step ${this.state.currentStep}`);
    }
  }

  goBack(): void {
    if (this.state.currentStep > ModernizationStep.UPLOAD) {
      this.state.currentStep--;
      console.log(`⬅️ Going back to step ${this.state.currentStep}`);
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
    this.isStreamingCurrentStep = false;
    this.stepsWithContent.clear();
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
    // FIXED: Show approve button as soon as we have content for current step
    // Don't wait for isProcessing to finish (that's for the whole stream)
    
    switch (this.state.currentStep) {
      case ModernizationStep.BUSINESS_LOGIC:
        // Show button if we have content AND not currently streaming THIS step
        return this.state.businessLogic.length > 50; // At least some content
        
      case ModernizationStep.USE_CASES:
        return this.state.useCases.length > 50;
        
      case ModernizationStep.DOMAIN_MODEL:
        return this.state.domainModel.length > 50;
        
      case ModernizationStep.BACKEND_DESIGN:
        return this.state.backendDesign.length > 50;
        
      case ModernizationStep.FRONTEND_DESIGN:
        return this.state.frontendDesign.length > 50;
        
      case ModernizationStep.CLOUD_DESIGN:
        return this.state.cloudDesign.length > 50;
        
      case ModernizationStep.CODE_GENERATION:
        return this.state.frontendZipUrl.length > 0 && this.state.backendZipUrl.length > 0;
        
      default:
        return false;
    }
  }

  canGoBack(): boolean {
    return this.state.currentStep > ModernizationStep.UPLOAD && 
           this.state.currentStep !== ModernizationStep.COMPLETE;
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

  isCurrentStepStreaming(): boolean {
    return this.isStreamingCurrentStep;
  }
}
