import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ModernizationService } from '../../services/modernization.service';
import { ModernizationStep, ModernizationState } from '../../models/modernization.model';

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

  uploadedFileName: string = '';
  targetDomainFileName: string = '';
  isProcessing: boolean = false;
  isStreamingCurrentStep: boolean = false;
  stepsWithContent: Set<ModernizationStep> = new Set();
  currentStageComplete: boolean = false; // NEW: Track if current stage is complete

  steps = [
    { step: ModernizationStep.UPLOAD, title: 'Upload', description: 'VB File', icon: '📁' },
    { step: ModernizationStep.BUSINESS_LOGIC, title: 'Business Logic', description: 'Analysis', icon: '🔍' },
    { step: ModernizationStep.USE_CASES, title: 'Use Cases', description: 'Gherkin BDD', icon: '📋' },
    { step: ModernizationStep.DOMAIN_MODEL, title: 'Domain Model', description: 'Entities', icon: '🏗️' },
    { step: ModernizationStep.DOMAIN_MAPPING, title: 'Domain Compare', description: 'Mapping', icon: '🔄' },
    { step: ModernizationStep.BACKEND_DESIGN, title: 'Backend', description: 'API Design', icon: '⚙️' },
    { step: ModernizationStep.FRONTEND_DESIGN, title: 'Frontend', description: 'UI Design', icon: '🎨' },
    { step: ModernizationStep.CLOUD_DESIGN, title: 'Cloud', description: 'Architecture', icon: '☁️' },
    { step: ModernizationStep.COMPLETE, title: 'Complete', description: 'Download', icon: '✅' }
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
          console.log('✅ Target domain model loaded');
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
    this.currentStageComplete = false; // Reset stage completion
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

    console.log('🚀 Starting modernization workflow...');

    this.modernizationService.analyzeCodeStream(this.state.vbCode, this.state.targetDomainModel)
      .subscribe({
        next: (chunk) => {
          console.log('📦 Received chunk:', Object.keys(chunk));
          
          // Check if stage is complete
          if (chunk.stage_complete) {
            console.log(`✅ Stage complete: ${chunk.stage}`);
            this.currentStageComplete = true;
            this.isStreamingCurrentStep = false;
            return; // Don't process further, wait for user approval
          }
          
          // Business Logic
          if (chunk.business_logic) {
            this.state.businessLogic += chunk.business_logic;
            this.stepsWithContent.add(ModernizationStep.BUSINESS_LOGIC);
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
            this.stepsWithContent.add(ModernizationStep.DOMAIN_MAPPING);
            if (this.state.currentStep === ModernizationStep.DOMAIN_MAPPING) {
              this.isStreamingCurrentStep = true;
            }
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
          
          // ZIP URLs
          if (chunk.frontend_zip_url) {
            this.state.frontendZipUrl = chunk.frontend_zip_url;
          }
          if (chunk.backend_zip_url) {
            this.state.backendZipUrl = chunk.backend_zip_url;
          }
        },
        error: (error) => {
          console.error('❌ Stream error:', error);
          this.isProcessing = false;
          this.isStreamingCurrentStep = false;
          alert('Error during modernization. Check console for details.');
        },
        complete: () => {
          console.log('✅ Stream completed');
          this.isProcessing = false;
          this.isStreamingCurrentStep = false;
          this.state.currentStep = ModernizationStep.COMPLETE;
        }
      });
  }

  isCurrentStepStreaming(): boolean {
    return this.isStreamingCurrentStep && !this.currentStageComplete;
  }

  canGoBack(): boolean {
    return this.state.currentStep > ModernizationStep.BUSINESS_LOGIC && 
           !this.isProcessing;
  }

  approveAndContinue(): void {
    if (!this.currentStageComplete) {
      alert('Please wait for the current stage to complete.');
      return;
    }

    console.log(`✅ User approved stage: ${this.state.currentStep}`);
    this.currentStageComplete = false;
    
    // Move to next step
    if (this.state.currentStep < ModernizationStep.COMPLETE) {
      this.state.currentStep++;
      console.log(`➡️ Moving to step ${this.state.currentStep}`);
      
      // Continue processing (trigger next stage in backend)
      // Note: In a real implementation, you'd send a message to backend to continue
    }
  }

  goBack(): void {
    if (this.state.currentStep > ModernizationStep.UPLOAD) {
      this.state.currentStep--;
      console.log(`⬅️ Going back to step ${this.state.currentStep}`);
    }
  }

  rejectAndModify(): void {
    alert('Modification feature: You can edit the output manually and resubmit.');
  }

  reset(): void {
    if (confirm('Are you sure you want to start over? All progress will be lost.')) {
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
      this.currentStageComplete = false;
      this.stepsWithContent.clear();
    }
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

  // NEW: Download domain mapping as Excel
  async downloadDomainMappingExcel(): Promise<void> {
    if (!this.state.domainMapping) {
      alert('No domain mapping available to download.');
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/export/domain-mapping/excel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain_mapping: this.state.domainMapping })
      });

      if (!response.ok) {
        throw new Error('Failed to generate Excel file');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'domain_mapping_comparison.xlsx';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading Excel:', error);
      alert('Failed to download Excel file. See console for details.');
    }
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
    // Show approve button when stage is complete
    return this.currentStageComplete;
  }
}
