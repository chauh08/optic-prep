import { curatedQuestions } from "./questions";
import type { HistoryEntry, Question, QuizAnswer, QuizSettings, Topic } from "./types";

export const defaultSettings: QuizSettings = {
  count: 10,
  topics: ["Optics fundamentals", "Ophthalmic lenses", "Frame fitting & measurements", "Dispensing", "Safety & regulatory basics"],
  difficulties: ["foundation", "applied", "challenge"],
  mode: "curated"
};

export function shuffle<T>(items: T[], random = Math.random): T[] {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

export function selectCurated(settings: QuizSettings, random = Math.random): Question[] {
  const eligible = curatedQuestions.filter(
    (q) => settings.topics.includes(q.topic) && settings.difficulties.includes(q.difficulty)
  );
  return shuffle(eligible, random).slice(0, Math.min(settings.count, eligible.length));
}

export function scoreAnswers(questions: Question[], answers: QuizAnswer[]) {
  const byId = new Map(answers.map((a) => [a.questionId, a]));
  const topicRows = new Map<Topic, { correct: number; total: number }>();
  for (const question of questions) {
    const row = topicRows.get(question.topic) ?? { correct: 0, total: 0 };
    row.total++;
    if (byId.get(question.id)?.correct) row.correct++;
    topicRows.set(question.topic, row);
  }
  return {
    correct: questions.filter((question) => byId.get(question.id)?.correct).length,
    total: questions.length,
    byTopic: [...topicRows.entries()].map(([topic, values]) => ({ topic, ...values })),
    missed: questions.filter((q) => !byId.get(q.id)?.correct)
  };
}

export function makeHistoryEntry(questions: Question[], answers: QuizAnswer[]): HistoryEntry {
  const result = scoreAnswers(questions, answers);
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    completedAt: new Date().toISOString(),
    score: result.correct,
    total: result.total,
    topics: [...new Set(questions.map((q) => q.topic))]
  };
}

export function normalizePrompt(value: string) {
  return value.toLocaleLowerCase().replace(/[^\p{L}\p{N}]+/gu, " ").trim();
}

export function mergeUniqueQuestions(curated: Question[], generated: Question[], limit: number) {
  const seen = new Set<string>();
  const interleaved: Question[] = [];
  const maxLength = Math.max(curated.length, generated.length);
  for (let index = 0; index < maxLength; index++) {
    if (curated[index]) interleaved.push(curated[index]);
    if (generated[index]) interleaved.push(generated[index]);
  }
  return interleaved.filter((q) => {
    const key = normalizePrompt(q.prompt);
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  }).slice(0, limit);
}
