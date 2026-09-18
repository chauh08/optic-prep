"use client";

import { useEffect, useMemo, useState } from "react";
import { curatedQuestions } from "@/lib/questions";
import { historySchema, savedSessionSchema, settingsSchema } from "@/lib/persistence";
import { defaultSettings, makeHistoryEntry, mergeUniqueQuestions, scoreAnswers, selectCurated } from "@/lib/quiz";
import { difficulties, topics, type Difficulty, type HistoryEntry, type Question, type QuizAnswer, type QuizSettings, type Topic } from "@/lib/types";

type Phase = "setup" | "loading" | "quiz" | "results";
type SavedSession = {
  phase: Phase;
  settings: QuizSettings;
  questions: Question[];
  answers: QuizAnswer[];
  index: number;
  selected?: number | null;
  locked?: boolean;
};

const STORAGE = {
  settings: "opticprep.settings.v1",
  history: "opticprep.history.v1",
  session: "opticprep.session.v1"
};

function readStorage(key: string): unknown {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch {
    return null;
  }
}

function writeStorage(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Persistence is optional; the active in-memory session remains usable.
  }
}

function removeStorage(key: string) {
  try {
    localStorage.removeItem(key);
  } catch {
    // Persistence is optional; the active in-memory session remains usable.
  }
}

function LensMark() {
  return (
    <svg className="lens-mark" viewBox="0 0 48 48" aria-hidden="true">
      <circle cx="24" cy="24" r="15.5" />
      <path d="M2 24h44M24 2v44M7 15h5M36 15h5M7 33h5M36 33h5" />
      <circle cx="24" cy="24" r="2.5" />
    </svg>
  );
}

function Header({ onHome }: { onHome: () => void }) {
  return (
    <header className="site-header">
      <button className="brand" onClick={onHome} aria-label="OpticPrep home">
        <LensMark /><span>OpticPrep</span>
      </button>
      <div className="calibration" aria-hidden="true"><i /><i /><i /><i /><i /></div>
      <span className="edition">BASIC / PRACTICE</span>
    </header>
  );
}

function Notice({ children, tone = "info" }: { children: React.ReactNode; tone?: "info" | "error" }) {
  return <div className={`notice ${tone}`} role={tone === "error" ? "alert" : "status"}>{children}</div>;
}

export default function Home() {
  const [hydrated, setHydrated] = useState(false);
  const [phase, setPhase] = useState<Phase>("setup");
  const [settings, setSettings] = useState<QuizSettings>(defaultSettings);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<QuizAnswer[]>([]);
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [locked, setLocked] = useState(false);
  const [notice, setNotice] = useState("");
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  /* Client storage is intentionally applied after hydration to keep server markup deterministic. */
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    const storedSettings = settingsSchema.safeParse(readStorage(STORAGE.settings));
    const storedHistory = historySchema.safeParse(readStorage(STORAGE.history));
    const storedSession = savedSessionSchema.safeParse(readStorage(STORAGE.session));
    setSettings(storedSettings.success ? storedSettings.data : defaultSettings);
    setHistory(storedHistory.success ? storedHistory.data : []);
    const saved: SavedSession | null = storedSession.success ? storedSession.data : null;
    if (saved) {
      setPhase(saved.phase);
      setSettings(saved.settings);
      setQuestions(saved.questions);
      setAnswers(saved.answers);
      setIndex(Math.min(saved.index, saved.questions.length - 1));
      setSelected(saved.selected ?? null);
      setLocked(saved.locked ?? false);
      setNotice(saved.phase === "quiz" ? "Your in-progress session was restored." : "");
    }
    setHydrated(true);
  }, []);
  /* eslint-enable react-hooks/set-state-in-effect */

  useEffect(() => {
    if (!hydrated) return;
    writeStorage(STORAGE.settings, settings);
    if (phase === "quiz" || phase === "results") {
      writeStorage(STORAGE.session, { phase, settings, questions, answers, index, selected, locked });
    } else if (phase === "setup") {
      removeStorage(STORAGE.session);
    }
  }, [hydrated, phase, settings, questions, answers, index, selected, locked]);

  const eligibleCount = useMemo(() => curatedQuestions.filter(
    (q) => settings.topics.includes(q.topic) && settings.difficulties.includes(q.difficulty)
  ).length, [settings]);

  async function startQuiz() {
    if (!settings.topics.length || !settings.difficulties.length || eligibleCount === 0) return;
    setNotice("");
    setPhase("loading");
    const curated = selectCurated(settings);
    let assembled = curated;
    if (settings.mode === "ai") {
      if (!navigator.onLine) {
        setNotice("You appear to be offline. Curated questions are ready, so your session will continue without AI enhancement.");
      } else {
        try {
          const response = await fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              count: Math.min(Math.ceil(settings.count / 2), 10),
              topics: settings.topics,
              difficulties: settings.difficulties,
              existingPrompts: curatedQuestions.map((q) => q.prompt)
            })
          });
          const data = await response.json();
          if (!response.ok) throw new Error(data.error || "AI enhancement is unavailable.");
          assembled = mergeUniqueQuestions(curated, data.questions, settings.count);
          if (assembled.length < settings.count) {
            setNotice(`AI enhancement returned fewer validated items than requested. ${assembled.length} safe questions were selected.`);
          }
        } catch (error) {
          const reason = error instanceof Error && error.message.includes("not configured")
            ? error.message
            : "AI enhancement was unavailable or returned unsafe data. Curated questions were used instead.";
          setNotice(reason);
        }
      }
    }
    setQuestions(assembled);
    setAnswers([]);
    setIndex(0);
    setSelected(null);
    setLocked(false);
    setPhase("quiz");
  }

  function submitAnswer() {
    if (selected === null || locked) return;
    const question = questions[index];
    setAnswers((current) => [
      ...current.filter((answer) => answer.questionId !== question.id),
      { questionId: question.id, selectedIndex: selected, correct: selected === question.correctIndex }
    ]);
    setLocked(true);
  }

  function nextQuestion() {
    if (!locked) return;
    if (index === questions.length - 1) {
      const entry = makeHistoryEntry(questions, answers);
      const nextHistory = [entry, ...history].slice(0, 8);
      setHistory(nextHistory);
      writeStorage(STORAGE.history, nextHistory);
      setPhase("results");
      return;
    }
    setIndex((value) => value + 1);
    setSelected(null);
    setLocked(false);
  }

  useEffect(() => {
    if (phase !== "quiz") return;
    const onKey = (event: KeyboardEvent) => {
      if (event.repeat || event.target instanceof HTMLButtonElement || event.target instanceof HTMLInputElement) return;
      if (!locked && ["1", "2", "3", "4"].includes(event.key)) {
        setSelected(Number(event.key) - 1);
      } else if (event.key === "Enter") {
        if (locked) nextQuestion();
        else submitAnswer();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  function reset() {
    if (phase === "quiz" && answers.length > 0 && !window.confirm("Leave this practice set? Your current session will be cleared.")) {
      return;
    }
    setPhase("setup");
    setQuestions([]);
    setAnswers([]);
    setIndex(0);
    setSelected(null);
    setLocked(false);
    setNotice("");
  }

  function retryMissed() {
    const missed = scoreAnswers(questions, answers).missed;
    setQuestions(missed);
    setAnswers([]);
    setIndex(0);
    setSelected(null);
    setLocked(false);
    setNotice("Retrying only the questions you missed.");
    setPhase("quiz");
  }

  if (!hydrated) {
    return <main className="loading-shell" aria-busy="true"><div className="skeleton wide" /><div className="skeleton" /><span className="sr-only">Loading your study workspace</span></main>;
  }

  return (
    <>
      <Header onHome={reset} />
      <main>
        {phase === "setup" && <Setup settings={settings} setSettings={setSettings} eligibleCount={eligibleCount} onStart={startQuiz} history={history} />}
        {phase === "loading" && <Loading />}
        {phase === "quiz" && questions[index] && (
          <Quiz
            question={questions[index]} index={index} total={questions.length}
            selected={selected} locked={locked} onSelect={setSelected}
            onSubmit={submitAnswer} onNext={nextQuestion} notice={notice}
          />
        )}
        {phase === "results" && <Results questions={questions} answers={answers} onRetry={retryMissed} onReset={reset} />}
      </main>
      <footer>
        <p>Independent educational practice. Not affiliated with or endorsed by ABO-NCLE. Not real exam content.</p>
      </footer>
    </>
  );
}

function Setup({ settings, setSettings, eligibleCount, onStart, history }: {
  settings: QuizSettings; setSettings: React.Dispatch<React.SetStateAction<QuizSettings>>;
  eligibleCount: number; onStart: () => void; history: HistoryEntry[];
}) {
  const toggle = <T,>(values: T[], value: T) => values.includes(value) ? values.filter((item) => item !== value) : [...values, value];
  return (
    <div className="setup-layout">
      <section className="setup-intro">
        <div className="lens-figure" aria-hidden="true"><LensMark /><span>OC</span><b>0</b><b>5</b><b>10</b></div>
        <h1>Set the focus.<br />Test the fundamentals.</h1>
        <p>Original practice questions for ABO Basic candidates, built for deliberate review—not prediction or recall of any real exam.</p>
        <div className="bank-readout"><strong>{curatedQuestions.length}</strong><span>curated questions<br />available offline</span></div>
      </section>

      <form className="setup-form" onSubmit={(event) => { event.preventDefault(); onStart(); }}>
        <h2>Build a practice set</h2>
        <label className="control-label" htmlFor="count">Question count <output>{settings.count}</output></label>
        <input id="count" type="range" min="5" max="30" step="5" value={settings.count}
          onChange={(e) => setSettings((s) => ({ ...s, count: Number(e.target.value) }))} />
        <div className="range-labels" aria-hidden="true"><span>5</span><span>10</span><span>15</span><span>20</span><span>25</span><span>30</span></div>

        <fieldset>
          <legend>Topics <span>Choose one or more</span></legend>
          <div className="check-list">
            {topics.map((topic) => <label key={topic}><input type="checkbox" checked={settings.topics.includes(topic)}
              onChange={() => setSettings((s) => ({ ...s, topics: toggle<Topic>(s.topics, topic) }))} /><span>{topic}</span></label>)}
          </div>
        </fieldset>

        <fieldset>
          <legend>Difficulty mix</legend>
          <div className="segment">
            {difficulties.map((difficulty) => <label key={difficulty}><input type="checkbox" checked={settings.difficulties.includes(difficulty)}
              onChange={() => setSettings((s) => ({ ...s, difficulties: toggle<Difficulty>(s.difficulties, difficulty) }))} /><span>{difficulty}</span></label>)}
          </div>
        </fieldset>

        <fieldset>
          <legend>Question source</legend>
          <div className="source-options">
            <label><input type="radio" name="mode" checked={settings.mode === "curated"} onChange={() => setSettings((s) => ({ ...s, mode: "curated" }))} />
              <span><strong>Curated only</strong><small>Reliable, reviewed bank. Works offline.</small></span></label>
            <label><input type="radio" name="mode" checked={settings.mode === "ai"} onChange={() => setSettings((s) => ({ ...s, mode: "ai" }))} />
              <span><strong>AI-enhanced</strong><small>Server-generated variety with validated fallback.</small></span></label>
          </div>
        </fieldset>

        {(!settings.topics.length || !settings.difficulties.length) && <Notice tone="error">Select at least one topic and one difficulty.</Notice>}
        {eligibleCount > 0 && eligibleCount < settings.count && settings.mode === "curated" && <Notice>Only {eligibleCount} matching curated questions are available; the set will use all of them.</Notice>}
        <button className="primary" type="submit" disabled={!settings.topics.length || !settings.difficulties.length || eligibleCount === 0}>
          Start practice <span aria-hidden="true">→</span>
        </button>
        <p className="key-hint">During practice: keys <kbd>1</kbd>–<kbd>4</kbd> select · <kbd>Enter</kbd> advances</p>
      </form>

      <aside className="history-strip">
        <h2>Recent sessions</h2>
        {history.length === 0 ? <p>No completed sessions yet. Your latest eight results will appear here on this device.</p> :
          <ol>{history.slice(0, 4).map((item) => <li key={item.id}><time dateTime={item.completedAt}>{new Date(item.completedAt).toLocaleDateString()}</time><strong>{item.score}/{item.total}</strong></li>)}</ol>}
      </aside>
    </div>
  );
}

function Loading() {
  return (
    <section className="question-shell" aria-busy="true" aria-live="polite">
      <div className="progress-line"><span style={{ width: "12%" }} /></div>
      <p className="loading-copy">Calibrating your question set…</p>
      <div className="skeleton wide" /><div className="skeleton" /><div className="skeleton" /><div className="skeleton" />
    </section>
  );
}

function Quiz({ question, index, total, selected, locked, onSelect, onSubmit, onNext, notice }: {
  question: Question; index: number; total: number; selected: number | null; locked: boolean;
  onSelect: (index: number) => void; onSubmit: () => void; onNext: () => void; notice: string;
}) {
  return (
    <section className="question-shell">
      <div className="quiz-meta">
        <span>{question.topic}</span><span>{question.difficulty}</span><span>{question.source === "ai" ? "AI-generated" : "Curated"}</span>
      </div>
      <div className="progress-copy"><strong>Question {index + 1}</strong><span>of {total}</span></div>
      <div className="progress-line" role="progressbar" aria-label="Quiz progress" aria-valuemin={1} aria-valuemax={total} aria-valuenow={index + 1}>
        <span style={{ width: `${((index + 1) / total) * 100}%` }} />
      </div>
      {notice && index === 0 && <Notice>{notice}</Notice>}
      <h1>{question.prompt}</h1>
      <fieldset className="answers">
        <legend className="sr-only">Choose one answer</legend>
        {question.options.map((option, optionIndex) => {
          const isCorrect = locked && optionIndex === question.correctIndex;
          const isWrong = locked && selected === optionIndex && optionIndex !== question.correctIndex;
          return (
            <label key={option} className={`${selected === optionIndex ? "selected" : ""} ${isCorrect ? "correct" : ""} ${isWrong ? "wrong" : ""}`}>
              <input type="radio" name="answer" checked={selected === optionIndex} disabled={locked} onChange={() => onSelect(optionIndex)} />
              <kbd>{optionIndex + 1}</kbd><span>{option}</span>
              {isCorrect && <b>Correct</b>}{isWrong && <b>Selected</b>}
            </label>
          );
        })}
      </fieldset>
      <div aria-live="polite">
        {locked && <div className="rationale"><strong>{selected === question.correctIndex ? "Correct." : "Not quite."}</strong><p>{question.rationale}</p></div>}
      </div>
      <div className="quiz-actions">
        {!locked ? <button className="primary" disabled={selected === null} onClick={onSubmit}>Submit answer</button> :
          <button className="primary" onClick={onNext}>{index === total - 1 ? "See results" : "Next question"} <span aria-hidden="true">→</span></button>}
      </div>
    </section>
  );
}

function Results({ questions, answers, onRetry, onReset }: { questions: Question[]; answers: QuizAnswer[]; onRetry: () => void; onReset: () => void }) {
  const result = scoreAnswers(questions, answers);
  const percent = result.total ? Math.round((result.correct / result.total) * 100) : 0;
  return (
    <section className="results-shell">
      <header className="score-head">
        <div><span>SESSION COMPLETE</span><h1>{result.correct}<small> / {result.total}</small></h1><p>{percent}% correct</p></div>
        <svg viewBox="0 0 160 80" aria-label={`${percent} percent correct`} role="img"><path d="M10 70A70 70 0 01150 70" /><path className="score-arc" style={{ strokeDasharray: `${percent} 100` }} pathLength="100" d="M10 70A70 70 0 01150 70" /></svg>
      </header>
      <div className="result-columns">
        <section><h2>Topic breakdown</h2><ul className="topic-results">{result.byTopic.map((row) =>
          <li key={row.topic}><span>{row.topic}</span><div><i style={{ width: `${(row.correct / row.total) * 100}%` }} /></div><strong>{row.correct}/{row.total}</strong></li>)}</ul></section>
        <section><h2>Missed review</h2>{result.missed.length === 0 ? <Notice>Clear verification: no missed questions in this set.</Notice> :
          <ol className="missed-list">{result.missed.map((question) => {
            const answer = answers.find((item) => item.questionId === question.id);
            return <li key={question.id}><h3>{question.prompt}</h3><p><b>Your answer:</b> {answer ? question.options[answer.selectedIndex] : "No answer"}</p><p><b>Correct:</b> {question.options[question.correctIndex]}</p><small>{question.rationale}</small></li>;
          })}</ol>}</section>
      </div>
      <div className="result-actions">{result.missed.length > 0 && <button className="primary" onClick={onRetry}>Retry missed</button>}<button className="secondary" onClick={onReset}>Build another test</button></div>
    </section>
  );
}
