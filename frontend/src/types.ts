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

export interface ValidationError {
  field: string;
  rule: string;
  detail: string;
}

export interface GenerateResult {
  character: Character;
  validation_errors: ValidationError[];
  run_id: string | null;
  version_id: string | null;
  version_number: number | null;
}

export interface CharacterVersion {
  id: string;
  character_id: string;
  version_number: number;
  sheet: CharacterSheet;
  created_at?: string;
}

export interface RunSummary {
  id: string;
  character_id: string;
  version_id: string | null;
  model: string;
  locked_fields: string[];
  validation_errors?: ValidationError[] | null;
  latency_ms?: number | null;
  cost_usd?: number | null;
  created_at?: string;
}

export interface RetrievedChunk {
  section?: string;
  text?: string;
  content?: string;
  score?: number;
}

export interface PipelineStep {
  name: string;
  detail: Record<string, unknown>;
  duration_ms: number;
}

export interface TraceRun extends RunSummary {
  input_snapshot: Record<string, unknown>;
  retrieved_chunks?: RetrievedChunk[] | null;
  prompt?: string | null;
  raw_output?: Record<string, unknown> | null;
  input_tokens?: number | null;
  output_tokens?: number | null;
  steps?: PipelineStep[] | null;
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
