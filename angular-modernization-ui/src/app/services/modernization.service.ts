import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { StreamChunk } from '../models/modernization.model';

@Injectable({
  providedIn: 'root'
})
export class ModernizationService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor() { }

  /**
   * Analyze VB code with real-time streaming
   * @param vbCode - VB code content
   * @param targetDomain - Optional target domain model for comparison
   * @returns Observable that emits chunks in real-time
   */
  analyzeCodeStream(vbCode: string, targetDomain?: string): Observable<StreamChunk> {
    return new Observable((observer) => {
      fetch(`${this.apiUrl}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: vbCode,
          targetDomainModel: targetDomain || ''
        })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.body;
        })
        .then(body => {
          if (!body) {
            throw new Error('Response body is null');
          }

          const reader = body.getReader();
          const decoder = new TextDecoder();
          let buffer = '';

          const processStream = async () => {
            try {
              while (true) {
                const { done, value } = await reader.read();
                
                if (done) {
                  observer.complete();
                  break;
                }

                // Decode the chunk immediately
                buffer += decoder.decode(value, { stream: true });
                
                // Process all complete SSE messages in the buffer
                const lines = buffer.split('\n');
                buffer = lines.pop() || ''; // Keep incomplete line in buffer

                for (const line of lines) {
                  if (line.trim() === '') continue;
                  if (!line.startsWith('data:')) continue;
                  
                  const jsonStr = line.replace(/^data:\s*/, '').trim();
                  if (!jsonStr) continue;
                  
                  try {
                    const data = JSON.parse(jsonStr);
                    // Emit each chunk immediately to the observer
                    // This ensures real-time UI updates
                    observer.next(data);
                  } catch (e) {
                    console.error('JSON parse error:', e, 'String:', jsonStr);
                  }
                }
              }
            } catch (error) {
              observer.error(error);
            }
          };

          processStream();
        })
        .catch(error => {
          observer.error(error);
        });
    });
  }

  /**
   * Read VB file content
   * @param file - File object
   * @returns Promise with file content
   */
  readVBFile(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        resolve(content);
      };
      reader.onerror = (e) => {
        reject(e);
      };
      reader.readAsText(file);
    });
  }
}
