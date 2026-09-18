# OpticPrep

OpticPrep is an independent Streamlit study app for ABO Basic Certification candidates. It
ships with 33 original practice questions and works without an account, database, or AI token.

> **Educational disclaimer:** OpticPrep is not affiliated with or endorsed by ABO-NCLE. It
> does not contain, reproduce, or claim to predict real examination content. Regulatory and
> safety material is introductory; consult current primary authorities and local requirements.

## Run locally

Python 3.11 or newer is required.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
streamlit run app.py
```

Then open `http://localhost:8501`. Run the quality checks with:

```bash
pytest
ruff check .
python -m compileall app.py opticprep
```

## Optional GitHub Models enhancement

The curated experience requires no configuration. To add server-generated variety, set secrets
in `.streamlit/secrets.toml` (copy the committed example) or environment variables:

```toml
GITHUB_TOKEN = "your_token"
GITHUB_MODELS_MODEL = "openai/gpt-4.1-mini"
```

Use a fine-grained token with the minimum **Models: Read** permission. The token is accessed
only by Python on the Streamlit server and is never rendered into the page. Requests use a
20-second timeout. Responses receive strict Pydantic validation: exact fields, four distinct
options, one valid answer, allowed topic and difficulty, unique prompts, and rejection against
the curated bank. Missing credentials, request failures, malformed output, duplicates, or
filter mismatches show an explicit curated-fallback notice.

Streamlit executes interactions on the server, but a public deployment can still consume your
token through repeated UI use. For public or high-traffic use, restrict app viewers with
Streamlit platform access controls, apply organization/model spending limits, monitor usage,
and rotate the token when appropriate. Application memory is not an adequate global rate
limiter across replicas.

## Persistence

There is no database. Quiz state, answers, and up to eight recent results live in
`st.session_state`, so normal Streamlit reruns are safe. Setup choices are mirrored to query
parameters, making a configured URL bookmarkable. Streamlit does not provide native durable
browser `localStorage`; a hard refresh, disconnected session, server restart, or cleared URL
may lose active answers and history. The app states this limitation rather than adding an
opaque third-party component.

## Deploy

### Streamlit Community Cloud

1. Push the repository to GitHub and create an app at
   [share.streamlit.io](https://share.streamlit.io/).
2. Select `app.py` as the entrypoint.
3. Optionally add the two values above in **App settings → Secrets**.
4. Deploy. Dependencies are installed from `requirements.txt` and `pyproject.toml`.

Vercel is not used; this repository is a Python Streamlit application.

### Container

```bash
docker build -t opticprep .
docker run --rm -p 8501:8501 -e GITHUB_TOKEN opticprep
```

Omit the token for curated-only operation.

## Architecture

- `app.py` — setup, one-at-a-time quiz, feedback, results, review, and session flow.
- `opticprep/questions.json` — 33 original curated questions.
- `opticprep/models.py` — strict domain and AI response schemas.
- `opticprep/quiz.py` — selection, deduplication, and scoring.
- `opticprep/ai.py` — server-side GitHub Models REST boundary and validation.
- `tests/` — unit coverage and Streamlit `AppTest` smoke coverage.

Questions were authored for this project from general opticianry principles, not copied banks.
Terminology and current requirements can be checked against
[ABO-NCLE](https://www.abo-ncle.org/),
[OSHA 29 CFR 1910.133](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.133),
and [FDA 21 CFR 801.410](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-801/subpart-H/section-801.410).
