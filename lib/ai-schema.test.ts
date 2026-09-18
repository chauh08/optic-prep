import { describe, expect, it } from "vitest";
import { generatedQuestionsSchema } from "./ai-schema";

const valid = {
  prompt: "Which measurement locates one pupil relative to the facial midline?",
  options: ["Monocular PD", "Temple length", "B dimension", "Effective diameter"],
  correctIndex: 0,
  rationale: "Monocular PD records each eye's centration distance independently.",
  topic: "Frame fitting & measurements",
  difficulty: "applied"
};

describe("AI response validation", () => {
  it("accepts a well-formed original question", () => {
    expect(generatedQuestionsSchema.parse({ questions: [valid] }).questions).toHaveLength(1);
  });

  it("rejects duplicate options", () => {
    const result = generatedQuestionsSchema.safeParse({
      questions: [{ ...valid, options: ["Monocular PD", "Monocular PD", "B dimension", "Effective diameter"] }]
    });
    expect(result.success).toBe(false);
  });

  it("rejects duplicate prompts within one response", () => {
    const result = generatedQuestionsSchema.safeParse({ questions: [valid, { ...valid }] });
    expect(result.success).toBe(false);
  });
});
