import { NextResponse } from "next/server";
import { generatedQuestionsSchema, generateRequestSchema } from "@/lib/ai-schema";
import { normalizePrompt } from "@/lib/quiz";

export const runtime = "nodejs";

const requestLog = new Map<string, number[]>();
const RATE_WINDOW_MS = 60_000;
const RATE_LIMIT = 5;

export async function POST(request: Request) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    return NextResponse.json(
      { error: "AI enhancement is not configured. Using the curated question bank instead.", code: "NO_TOKEN" },
      { status: 503 }
    );
  }

  if (!isSameOrigin(request)) {
    return NextResponse.json({ error: "Cross-origin generation requests are not allowed.", code: "FORBIDDEN" }, { status: 403 });
  }

  const client = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "local";
  if (!consumeRateLimit(client)) {
    return NextResponse.json(
      { error: "AI enhancement is temporarily rate-limited. Curated questions are still available.", code: "RATE_LIMITED" },
      { status: 429 }
    );
  }

  const requestResult = generateRequestSchema.safeParse(await request.json().catch(() => null));
  if (!requestResult.success) {
    return NextResponse.json({ error: "The generation request was invalid.", code: "INVALID_REQUEST" }, { status: 400 });
  }

  const input = requestResult.data;
  const model = process.env.GITHUB_MODELS_MODEL || "openai/gpt-4.1-mini";
  const instruction = `Create ${input.count} original educational multiple-choice questions for opticianry fundamentals practice.
This is independent study material, not real or recalled certification exam content.
Use only these topics: ${input.topics.join(", ")}.
Use only these difficulty labels: ${input.difficulties.join(", ")}.
Each question must have exactly four distinct plausible options, one correctIndex from 0 to 3, and a concise factual rationale.
Avoid jurisdiction-specific legal claims; advise checking current local rules where relevant.
Do not repeat or closely paraphrase these prompts: ${input.existingPrompts.join(" | ")}.
Return JSON only, shaped as {"questions":[{"prompt":"","options":["","","",""],"correctIndex":0,"rationale":"","topic":"","difficulty":""}]}.`;

  try {
    const response = await fetch("https://models.github.ai/inference/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: "system", content: "You write original, cautious educational assessment items and return strict JSON." },
          { role: "user", content: instruction }
        ],
        temperature: 0.5,
        max_tokens: 3500,
        response_format: { type: "json_object" }
      }),
      signal: AbortSignal.timeout(20000)
    });
    if (!response.ok) throw new Error(`GitHub Models returned ${response.status}`);

    const payload: unknown = await response.json();
    const content = getModelContent(payload);
    const parsed = generatedQuestionsSchema.parse(JSON.parse(content.replace(/^```json\s*|\s*```$/g, "")));
    const existing = new Set(input.existingPrompts.map(normalizePrompt));
    const questions = parsed.questions
      .filter((question) =>
        input.topics.includes(question.topic) &&
        input.difficulties.includes(question.difficulty) &&
        !existing.has(normalizePrompt(question.prompt))
      )
      .slice(0, input.count)
      .map((question, index) => ({ ...question, id: `ai-${Date.now()}-${index}`, source: "ai" as const }));

    if (!questions.length) throw new Error("Generated questions did not satisfy the requested filters");
    return NextResponse.json({ questions, model });
  } catch (error) {
    console.error("AI question generation failed", error instanceof Error ? error.message : "Unknown error");
    return NextResponse.json(
      { error: "AI questions could not be safely validated. Using curated questions instead.", code: "AI_FALLBACK" },
      { status: 502 }
    );
  }
}

function isSameOrigin(request: Request) {
  const origin = request.headers.get("origin");
  if (!origin) return process.env.NODE_ENV !== "production";
  try {
    return new URL(origin).host === new URL(request.url).host;
  } catch {
    return false;
  }
}

function consumeRateLimit(client: string) {
  const now = Date.now();
  const recent = (requestLog.get(client) ?? []).filter((timestamp) => now - timestamp < RATE_WINDOW_MS);
  if (recent.length >= RATE_LIMIT) return false;
  recent.push(now);
  requestLog.set(client, recent);
  return true;
}

function getModelContent(payload: unknown): string {
  if (!payload || typeof payload !== "object" || !("choices" in payload)) {
    throw new Error("Missing model output");
  }
  const choices = (payload as { choices?: unknown }).choices;
  if (!Array.isArray(choices) || !choices[0] || typeof choices[0] !== "object") {
    throw new Error("Missing model output");
  }
  const message = (choices[0] as { message?: unknown }).message;
  if (!message || typeof message !== "object") throw new Error("Missing model output");
  const content = (message as { content?: unknown }).content;
  if (typeof content !== "string") throw new Error("Missing model output");
  return content;
}
