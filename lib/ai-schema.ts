import { z } from "zod";
import { difficulties, topics } from "./types";
import { normalizePrompt } from "./quiz";

const generatedQuestionSchema = z.object({
  prompt: z.string().trim().min(12).max(500),
  options: z.tuple([
    z.string().trim().min(1).max(180),
    z.string().trim().min(1).max(180),
    z.string().trim().min(1).max(180),
    z.string().trim().min(1).max(180)
  ]),
  correctIndex: z.number().int().min(0).max(3),
  rationale: z.string().trim().min(12).max(600),
  topic: z.enum(topics),
  difficulty: z.enum(difficulties)
}).strict().superRefine((question, context) => {
  const uniqueOptions = new Set(question.options.map(normalizePrompt));
  if (uniqueOptions.size !== 4) {
    context.addIssue({ code: "custom", path: ["options"], message: "All four options must be distinct." });
  }
});

export const generatedQuestionsSchema = z.object({
  questions: z.array(generatedQuestionSchema).min(1).max(10)
}).strict().superRefine(({ questions }, context) => {
  const seen = new Set<string>();
  questions.forEach((question, index) => {
    const normalized = normalizePrompt(question.prompt);
    if (seen.has(normalized)) {
      context.addIssue({ code: "custom", path: ["questions", index, "prompt"], message: "Duplicate prompt." });
    }
    seen.add(normalized);
  });
});

export const generateRequestSchema = z.object({
  count: z.number().int().min(1).max(10),
  topics: z.array(z.enum(topics)).min(1).max(topics.length),
  difficulties: z.array(z.enum(difficulties)).min(1).max(difficulties.length),
  existingPrompts: z.array(z.string().max(500)).max(40)
}).strict();
