import { describe, expect, it } from "vitest";
import { curatedQuestions } from "./questions";
import { mergeUniqueQuestions, scoreAnswers, selectCurated } from "./quiz";
import type { QuizSettings } from "./types";

describe("quiz selection and scoring", () => {
  it("filters curated questions and respects the requested count", () => {
    const settings: QuizSettings = {
      count: 5,
      topics: ["Optics fundamentals"],
      difficulties: ["foundation"],
      mode: "curated"
    };
    const selected = selectCurated(settings, () => 0.5);
    expect(selected).toHaveLength(5);
    expect(selected.every((question) => question.topic === "Optics fundamentals")).toBe(true);
    expect(selected.every((question) => question.difficulty === "foundation")).toBe(true);
  });

  it("scores overall and by topic and identifies missed questions", () => {
    const questions = curatedQuestions.slice(0, 2);
    const answers = [
      { questionId: questions[0].id, selectedIndex: questions[0].correctIndex, correct: true },
      { questionId: questions[1].id, selectedIndex: (questions[1].correctIndex + 1) % 4, correct: false }
    ];
    const result = scoreAnswers(questions, answers);
    expect(result.correct).toBe(1);
    expect(result.total).toBe(2);
    expect(result.byTopic).toEqual([{ topic: "Optics fundamentals", correct: 1, total: 2 }]);
    expect(result.missed).toEqual([questions[1]]);
  });

  it("does not count duplicate answer records more than once", () => {
    const question = curatedQuestions[0];
    const duplicate = { questionId: question.id, selectedIndex: question.correctIndex, correct: true };
    expect(scoreAnswers([question], [duplicate, duplicate]).correct).toBe(1);
  });

  it("prevents normalized duplicate prompts while preserving the curated question", () => {
    const curated = curatedQuestions.slice(0, 2);
    const generated = [{ ...curated[0], id: "ai-1", prompt: curated[0].prompt.toUpperCase(), source: "ai" as const }];
    const result = mergeUniqueQuestions(curated, generated, 3);
    expect(result).toHaveLength(2);
    expect(result[0].id).toBe(curated[0].id);
  });
});
