export const topics = [
  "Optics fundamentals",
  "Ophthalmic lenses",
  "Frame fitting & measurements",
  "Dispensing",
  "Safety & regulatory basics"
] as const;

export const difficulties = ["foundation", "applied", "challenge"] as const;
export type Topic = (typeof topics)[number];
export type Difficulty = (typeof difficulties)[number];

export type Question = {
  id: string;
  prompt: string;
  options: [string, string, string, string];
  correctIndex: number;
  rationale: string;
  topic: Topic;
  difficulty: Difficulty;
  source: "curated" | "ai";
};

export type QuizSettings = {
  count: number;
  topics: Topic[];
  difficulties: Difficulty[];
  mode: "curated" | "ai";
};

export type QuizAnswer = { questionId: string; selectedIndex: number; correct: boolean };
export type HistoryEntry = {
  id: string;
  completedAt: string;
  score: number;
  total: number;
  topics: Topic[];
};
