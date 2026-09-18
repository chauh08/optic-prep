// @vitest-environment node
import { afterEach, describe, expect, it, vi } from "vitest";
import { POST } from "./route";

describe("generation endpoint fallback", () => {
  const priorToken = process.env.GITHUB_TOKEN;

  afterEach(() => {
    if (priorToken) process.env.GITHUB_TOKEN = priorToken;
    else delete process.env.GITHUB_TOKEN;
    vi.restoreAllMocks();
  });

  it("returns a clear no-token response without contacting a model", async () => {
    delete process.env.GITHUB_TOKEN;
    const response = await POST(new Request("http://localhost/api/generate", {
      method: "POST",
      body: JSON.stringify({ count: 1, topics: ["Dispensing"], difficulties: ["foundation"], existingPrompts: [] })
    }));
    expect(response.status).toBe(503);
    await expect(response.json()).resolves.toMatchObject({ code: "NO_TOKEN" });
  });

  it("returns validated, requested questions without exposing the token", async () => {
    process.env.GITHUB_TOKEN = "test-token";
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({
      choices: [{ message: { content: JSON.stringify({ questions: [{
        prompt: "Which instrument is used to verify spectacle lens power?",
        options: ["Lensometer", "Pupillometer", "Slit lamp", "Keratometer"],
        correctIndex: 0,
        rationale: "A lensometer is designed to measure and verify spectacle lens power.",
        topic: "Dispensing",
        difficulty: "foundation"
      }] }) } }]
    }), { status: 200 }));

    const response = await POST(new Request("http://localhost/api/generate", {
      method: "POST",
      headers: { origin: "http://localhost", "x-forwarded-for": "test-success" },
      body: JSON.stringify({ count: 1, topics: ["Dispensing"], difficulties: ["foundation"], existingPrompts: [] })
    }));

    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.questions).toHaveLength(1);
    expect(body.questions[0]).toMatchObject({ source: "ai", topic: "Dispensing", difficulty: "foundation" });
    expect(JSON.stringify(body)).not.toContain("test-token");
  });

  it("returns an explicit fallback when model output is malformed", async () => {
    process.env.GITHUB_TOKEN = "test-token";
    vi.spyOn(console, "error").mockImplementation(() => undefined);
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({
      choices: [{ message: { content: "{\"questions\":[{\"prompt\":\"too short\"}]}" } }]
    }), { status: 200 }));

    const response = await POST(new Request("http://localhost/api/generate", {
      method: "POST",
      headers: { origin: "http://localhost", "x-forwarded-for": "test-malformed" },
      body: JSON.stringify({ count: 1, topics: ["Dispensing"], difficulties: ["foundation"], existingPrompts: [] })
    }));

    expect(response.status).toBe(502);
    await expect(response.json()).resolves.toMatchObject({ code: "AI_FALLBACK" });
  });
});
