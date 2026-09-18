import { z } from "zod";
import { difficulties, topics } from "./types";

const questionSchema = z.object({
  id: z.string().min(1),
  prompt: z.string().min(1),
  options: z.tuple([z.string(), z.string(), z.string(), z.string()]),
  correctIndex: z.number().int().min(0).max(3),
  rationale: z.string().min(1),
  topic: z.enum(topics),
  difficulty: z.enum(difficulties),
  source: z.enum(["curated", "ai"])
}).strict();

const answerSchema = z.object({
  questionId: z.string().min(1),
  selectedIndex: z.number().int().min(0).max(3),
  correct: z.boolean()
}).strict();

export const settingsSchema = z.object({
  count: z.number().int().min(5).max(30),
  topics: z.array(z.enum(topics)).min(1),
  difficulties: z.array(z.enum(difficulties)).min(1),
  mode: z.enum(["curated", "ai"])
}).strict();

export const historySchema = z.array(z.object({
  id: z.string().min(1),
  completedAt: z.string().datetime(),
  score: z.number().int().nonnegative(),
  total: z.number().int().positive(),
  topics: z.array(z.enum(topics)).min(1)
}).strict()).max(8);

export const savedSessionSchema = z.object({
  phase: z.enum(["quiz", "results"]),
  settings: settingsSchema,
  questions: z.array(questionSchema).min(1).max(30),
  answers: z.array(answerSchema).max(30),
  index: z.number().int().nonnegative(),
  selected: z.number().int().min(0).max(3).nullable().optional(),
  locked: z.boolean().optional()
}).strict();
