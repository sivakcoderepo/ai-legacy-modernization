export interface ModernizationState {
  vbCode: string;
  currentStep: number;
  businessLogic: string;
  domainModel: string;
  backendDesign: string;
  frontendDesign: string;
  cloudDesign: string;
  history: ConversationMessage[];
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface StreamChunk {
  agent?: string;
  output?: string;
  business_logic?: string;
  domain_model?: string;
  backend_design?: string;
  frontend_design?: string;
  cloud_design?: string;
}

export enum ModernizationStep {
  UPLOAD = 0,
  BUSINESS_LOGIC = 1,
  DOMAIN_MODEL = 2,
  BACKEND_DESIGN = 3,
  FRONTEND_DESIGN = 4,
  CLOUD_DESIGN = 5,
  COMPLETE = 6
}

export interface StepInfo {
  step: ModernizationStep;
  title: string;
  description: string;
  icon: string;
}
