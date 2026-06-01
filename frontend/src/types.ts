export interface Field<T = unknown> {
  value: T;
  locked: boolean;
  source?: string | null;
}

export interface CharacterSheet {
  name: Field<string>;
  race: Field<string>;
  char_class: Field<string>;
  background: Field<string>;
  alignment: Field<string>;
  level: Field<number>;
  stats: Field<Record<string, number>>;
  proficiencies: Field<string[]>;
  spells: Field<string[]>;
  equipment: Field<string[]>;
  backstory: Field<string>;
  personality: Field<string>;
}

export interface Character {
  id: string;
  name: string;
  sheet: CharacterSheet;
  created_at?: string;
  updated_at?: string;
}

export const SHEET_FIELDS: (keyof CharacterSheet)[] = [
  "name",
  "race",
  "char_class",
  "background",
  "alignment",
  "level",
  "stats",
  "proficiencies",
  "spells",
  "equipment",
  "backstory",
  "personality",
];

export const FIELD_LABELS: Record<keyof CharacterSheet, string> = {
  name: "Name",
  race: "Race",
  char_class: "Class",
  background: "Background",
  alignment: "Alignment",
  level: "Level",
  stats: "Ability Scores",
  proficiencies: "Proficiencies",
  spells: "Spells",
  equipment: "Equipment",
  backstory: "Backstory",
  personality: "Personality",
};
