/// <reference types="vite/client" />

interface ImportMeta {
  readonly env: {
    readonly VITE_API_BASE_URL: string;
    readonly VITE_VOICE_LANG: string;
    readonly VITE_VOICE_RATE: string;
    readonly VITE_VOICE_PITCH: string;
  };
}
