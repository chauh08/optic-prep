# OpticPrep

OpticPrep is an independent browser study app for ABO Basic Certification candidates. It ships with 33 original practice questions and remains fully usable without an account, database, network connection, or AI token.

> **Educational disclaimer:** This project is not affiliated with or endorsed by ABO-NCLE. It does not contain, reproduce, or claim to predict real examination content. Regulatory and safety material is introductory; consult current primary authorities and local requirements.

## Run locally

Requires a current Node.js LTS release (Node 20.9 or newer is supported by Next.js 16).

```bash
npm install
npm run dev
```

Open `http://localhost:3000`. Useful checks:

```bash
npm test
npm run lint
npm run typecheck
npm run build
```

## Optional GitHub Models enhancement

Copy `.env.example` to `.env.local`, then set:

```text
GITHUB_TOKEN=your_token
GITHUB_MODELS_MODEL=openai/gpt-4.1-mini
```

Use a fine-grained personal access token with the minimum **Models: Read** permission. Model availability and names depend on your GitHub account and organization policy. See [GitHub Models quickstart](https://docs.github.com/en/github-models/quickstart) and [API reference](https://docs.github.com/en/rest/models/inference).

The token is read only in `app/api/generate/route.ts`; it has no `NEXT_PUBLIC_` prefix and is never returned to the browser. The server caps request/output counts, applies a lightweight per-client rate limit, rejects cross-origin browser requests, asks for JSON, validates every field and option with Zod, rejects response duplicates, and filters against curated prompts. Missing credentials, network errors, invalid output, and duplicate-only output produce an explicit curated fallback notice. For public high-traffic deployments, also enable Vercel Firewall rate limiting because in-memory limits are instance-local.

## Architecture

- `app/page.tsx` — client-side setup, quiz, results, keyboard flow, and local recovery.
- `app/api/generate/route.ts` — server-only GitHub Models boundary.
- `lib/questions.ts` — original curated bank; no third-party question content.
- `lib/ai-schema.ts` — request and generated-response validation.
- `lib/quiz.ts` — deterministic selection, scoring, history, and deduplication logic.
- `localStorage` — settings, active session, and latest eight result summaries. No personal data is sent to a database.

AI-enhanced mode places validated generated items before curated fallback items. Refreshing restores an active quiz. Browser storage can be cleared by the user at any time.

## Deploy to Vercel

Import the repository in Vercel and use the detected Next.js defaults. The curated experience needs no environment variables. To enable AI-enhanced mode, add `GITHUB_TOKEN` and optionally `GITHUB_MODELS_MODEL` as encrypted project environment variables, then redeploy. Never expose the token through a `NEXT_PUBLIC_` variable.

## Content references

Questions were authored for this project from general opticianry principles rather than copied question banks. Useful primary/reference material for checking terminology and current requirements:

- [ABO-NCLE — Basic examination information and content outlines](https://www.abo-ncle.org/)
- [OSHA — Eye and Face Protection, 29 CFR 1910.133](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.133)
- [FDA — Impact-resistant lenses and 21 CFR 801.410](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-801/subpart-H/section-801.410)

These links are references, not claims of endorsement. Verify current editions and local applicability.
