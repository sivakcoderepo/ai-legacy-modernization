import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { StreamChunk } from '../models/modernization.model';

@Injectable({
  providedIn: 'root'
})
export class ModernizationService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor() { }

  analyzeCodeStream(vbCode: string): Observable<StreamChunk> {
    return new Observable((observer) => {
      fetch(`${this.apiUrl}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: vbCode })
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

                buffer += decoder.decode(value, { stream: true });
                const parts = buffer.split('\n\n');
                buffer = parts.pop() || '';

                for (const part of parts) {
                  if (!part.startsWith('data:')) continue;
                  
                  const jsonStr = part.replace(/^data:\s*/, '');
                  try {
                    const data = JSON.parse(jsonStr);
                    observer.next(data);
                  } catch (e) {
                    console.error('JSON parse error:', e, jsonStr);
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

  // Method to read VB file
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
