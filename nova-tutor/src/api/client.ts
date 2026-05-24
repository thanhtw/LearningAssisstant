/**
 * Fetch wrapper for backend API calls
 */

import { Mood } from '../components/Avatar/emotions';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const CHAT_REQUEST_TIMEOUT_MS = 30000;

export interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean>;
}

export interface StreamChatParams {
  sessionId: string;
  message: string;
  topic: string;
  level: string;
  characterName: string;
  onToken: (text: string) => void;
  onMood: (mood: Mood) => void;
  onDone: (fullText: string) => void;
  onError: (err: string) => void;
}

/**
 * Generic fetch wrapper with error handling
 */
export async function apiCall<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { params, ...fetchOptions } = options;

  // Build URL with query parameters
  let url = `${API_BASE_URL}${endpoint}`;
  if (params) {
    const queryString = new URLSearchParams(
      Object.entries(params).map(([key, value]) => [key, String(value)])
    ).toString();
    url += `?${queryString}`;
  }

  // Set default headers
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...fetchOptions.headers,
  };

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

/**
 * Stream chat with SSE (Server-Sent Events)
 * Returns cleanup function to abort the stream
 */
export function streamChat(params: StreamChatParams): () => void {
  const controller = new AbortController();
  let timedOut = false;
  const timeoutId = window.setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, CHAT_REQUEST_TIMEOUT_MS);
  
  const requestBody = {
    session_id: params.sessionId,
    message: params.message,
    topic: params.topic,
    level: params.level,
    character_name: params.characterName,
  };

  console.log('[chat] sending request', requestBody);

  fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
    signal: controller.signal,
  })
    .then(async (response) => {
      console.log('[chat] response status', response.status, response.statusText);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Response body is not readable');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          
          // Keep the last incomplete line in buffer
          buffer = lines[lines.length - 1];

          // Process complete lines
          for (let i = 0; i < lines.length - 1; i++) {
            const line = lines[i].trim();
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6); // Remove "data: "
              if (dataStr) {
                try {
                  const event = JSON.parse(dataStr);
                  
                  if (event.type === 'token') {
                    console.log('[chat] token', event.content);
                    params.onToken(event.content);
                  } else if (event.type === 'status') {
                    console.log('[chat] status', event.message);
                  } else if (event.type === 'mood') {
                    console.log('[chat] mood', event.mood);
                    params.onMood(event.mood);
                  } else if (event.type === 'done') {
                    console.log('[chat] done', event.full_text);
                    params.onDone(event.full_text);
                  } else if (event.type === 'error') {
                    console.error('[chat] error event', event.message);
                    params.onError(event.message);
                  }
                } catch (e) {
                  console.error('Failed to parse SSE event:', line, e);
                }
              }
            }
          }
        }
      } finally {
        window.clearTimeout(timeoutId);
        reader.releaseLock();
      }
    })
    .catch((error) => {
      window.clearTimeout(timeoutId);
      if (timedOut) {
        console.error('[chat] timed out waiting for backend response');
        params.onError('The tutor request timed out after 30 seconds.');
      } else if (error.name !== 'AbortError') {
        console.error('[chat] fetch failed', error);
        params.onError(error.message || 'Stream connection failed');
      }
    });

  // Return cleanup function
  return () => {
    window.clearTimeout(timeoutId);
    controller.abort();
  };
}

/**
 * Helper for GET requests
 */
export function get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
  return apiCall<T>(endpoint, { ...options, method: 'GET' });
}

/**
 * Helper for POST requests
 */
export function post<T>(
  endpoint: string,
  data?: unknown,
  options?: RequestOptions
): Promise<T> {
  return apiCall<T>(endpoint, {
    ...options,
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * Helper for PUT requests
 */
export function put<T>(
  endpoint: string,
  data?: unknown,
  options?: RequestOptions
): Promise<T> {
  return apiCall<T>(endpoint, {
    ...options,
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * Helper for DELETE requests
 */
export function del<T>(endpoint: string, options?: RequestOptions): Promise<T> {
  return apiCall<T>(endpoint, { ...options, method: 'DELETE' });
}
