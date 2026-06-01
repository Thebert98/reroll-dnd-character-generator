import { supabase } from "./supabase";
import type { Character, CharacterSheet } from "../types";

const BASE = import.meta.env.VITE_API_BASE_URL as string;

async function authHeader(): Promise<Record<string, string>> {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  const token = session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(await authHeader()),
      ...(init.headers || {}),
    },
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status}: ${detail}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  listCharacters: () => request<Character[]>("/characters"),
  createCharacter: (name: string) =>
    request<Character>("/characters", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  getCharacter: (id: string) => request<Character>(`/characters/${id}`),
  updateCharacter: (id: string, patch: { name?: string; sheet?: CharacterSheet }) =>
    request<Character>(`/characters/${id}`, {
      method: "PUT",
      body: JSON.stringify(patch),
    }),
  deleteCharacter: (id: string) =>
    request<void>(`/characters/${id}`, { method: "DELETE" }),
};
