export interface ModernizationState {
  vbCode: string;
  currentStep: number;
  businessLogic: string;
  useCases: string;
  domainModel: string;
  domainMapping: string;
  backendDesign: string;
  frontendDesign: string;
  cloudDesign: string;
  targetDomainModel: string;
  frontendZipUrl: string;
  backendZipUrl: string;
  history: ConversationMessage[];
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface StreamChunk {
  // Step outputs
  business_logic?: string;
  use_cases?: string;
  domain_model?: string;
  domain_mapping?: string;
  backend_design?: string;
  frontend_design?: string;
  cloud_design?: string;
  
  // Code generation status
  frontend_code_status?: string;
  backend_code_status?: string;
  status?: string;
  
  // Download URLs
  frontend_zip_path?: string;
  backend_zip_path?: string;
  frontend_zip_url?: string;
  backend_zip_url?: string;
  
  // Summary
  final_summary?: string;
  
  // Error handling
  error?: string;
}

export enum ModernizationStep {
  UPLOAD = 0,
  BUSINESS_LOGIC = 1,
  USE_CASES = 2,
  DOMAIN_MODEL = 3,
  BACKEND_DESIGN = 4,
  FRONTEND_DESIGN = 5,
  CLOUD_DESIGN = 6,
  CODE_GENERATION = 7,
  COMPLETE = 8
}

export interface StepInfo {
  step: ModernizationStep;
  title: string;
  description: string;
  icon: string;
}
