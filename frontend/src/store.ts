import { create } from "zustand";
import type { Character, CharacterSheet } from "./types";

interface EditorState {
  character: Character | null;
  dirty: boolean;
  setCharacter: (c: Character | null) => void;
  setFieldValue: (field: keyof CharacterSheet, value: unknown) => void;
  toggleLock: (field: keyof CharacterSheet) => void;
  markClean: () => void;
}

export const useEditor = create<EditorState>((set) => ({
  character: null,
  dirty: false,
  setCharacter: (c) => set({ character: c, dirty: false }),
  setFieldValue: (field, value) =>
    set((s) => {
      if (!s.character) return s;
      const sheet = { ...s.character.sheet };
      sheet[field] = { ...sheet[field], value } as never;
      return { character: { ...s.character, sheet }, dirty: true };
    }),
  toggleLock: (field) =>
    set((s) => {
      if (!s.character) return s;
      const sheet = { ...s.character.sheet };
      sheet[field] = { ...sheet[field], locked: !sheet[field].locked } as never;
      return { character: { ...s.character, sheet }, dirty: true };
    }),
  markClean: () => set({ dirty: false }),
}));
