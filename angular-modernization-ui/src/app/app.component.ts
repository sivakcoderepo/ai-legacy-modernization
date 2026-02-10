import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ModernizationComponent } from './components/modernization/modernization.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ModernizationComponent],
  template: `
    <div class="app-container">
      <header class="app-header">
        <div class="container">
          <h1>🚀 Legacy Code Modernization Platform</h1>
          <p>Transform your VB applications into modern, cloud-ready solutions</p>
        </div>
      </header>
      <main class="app-main">
        <app-modernization></app-modernization>
      </main>
      <footer class="app-footer">
        <div class="container">
          <p>Powered by AI • Step-by-step modernization workflow</p>
        </div>
      </footer>
    </div>
  `,
  styles: [`
    .app-container {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    .app-header {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      padding: 30px 0;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    .app-header h1 {
      font-size: 36px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 8px;
    }

    .app-header p {
      color: #666;
      font-size: 16px;
    }

    .app-main {
      flex: 1;
      padding: 40px 0;
    }

    .app-footer {
      background: rgba(255, 255, 255, 0.9);
      padding: 20px 0;
      text-align: center;
      color: #666;
      font-size: 14px;
    }
  `]
})
export class AppComponent {
  title = 'legacy-modernization-ui';
}
