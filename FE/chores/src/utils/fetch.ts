const API_BASE = import.meta.env.VITE_API_BASE;

export const fetchURL = (url: string) =>
  `${API_BASE}/${url.startsWith("/") ? url.slice(1) : url}`;
