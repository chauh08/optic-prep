# OpticPrep product truth

## Purpose

OpticPrep is a Streamlit study tool for people preparing for the ABO Basic Certification. It provides original practice material for learning and self-checking. It does **not** reproduce, predict, or claim access to an examination.

## Audience and job

Candidates use short, configurable sessions to expose knowledge gaps across optics fundamentals,
ophthalmic lenses, frame fitting and measurements, dispensing, ocular anatomy and refractive
conditions, instrumentation and verification, and safety or regulatory basics. The core loop
is: configure → answer → understand the rationale → inspect results → retry missed material.

## Shipped scope

- 97 original four-option questions, each with one answer, rationale, topic, and difficulty.
- Twelve deterministic numeric variants use locally evaluated original templates for focal
  power, induced prism, frame PD, and prescription transposition.
- Seven topics with foundation, applied, and challenge material available in every topic.
- Configurable question count, topic selection, difficulty mix, and curated or AI-enhanced source.
- One-question-at-a-time practice with keyboard-accessible native controls and immediate feedback.
- Results with overall score, topic breakdown, missed review, and retry.
- URL-backed setup settings, active Streamlit session state, and the latest eight in-session results.
- Optional server-side GitHub Models generation with strict validation and curated fallback.
- No accounts, database, analytics, spaced repetition, readiness prediction, or official exam simulation.

## Safety and claims

OpticPrep is independent and not affiliated with or endorsed by ABO-NCLE. Educational summaries are not legal, medical, or regulatory advice. Rules and standards can change and vary by jurisdiction; users should consult current primary authorities and qualified educators.

## Success standard

A candidate can complete a useful session without a token, account, or instruction manual. Once
the Streamlit app is loaded, AI failure must never block study. Normal Streamlit reruns preserve
the active session; a full browser refresh or server restart may clear answers because the product
has no database and Streamlit has no native durable browser storage.
