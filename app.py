from __future__ import annotations

from urllib.parse import quote, unquote

import streamlit as st

from opticprep.ai import AIUnavailable, generate_questions
from opticprep.models import DIFFICULTIES, TOPICS, Question
from opticprep.questions import CURATED_QUESTIONS
from opticprep.quiz import merge_unique, score_questions, select_questions

st.set_page_config(
    page_title="OpticPrep · Opticianry practice",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_css() -> None:
    st.markdown(
        """
        <style>
        :root {
          --paper:#f6f3eb; --panel:#fffdf7; --ink:#172326; --muted:#536061;
          --cyan:#007f82; --cyan-dark:#005e60; --success:#236d50; --error:#a53c32;
          --rule:#8a9694; --soft-rule:#ced4cf; --cyan-wash:#dcebe8;
        }
        .stApp { background:var(--paper); color:var(--ink); }
        .block-container { max-width:1160px; padding-top:1.25rem; padding-bottom:4rem; }
        header[data-testid="stHeader"] { background:transparent; }
        h1,h2,h3,p,label { color:var(--ink); }
        h1 { font-size:3.65rem; letter-spacing:-.038em; line-height:1.02; max-width:15ch;
          text-wrap:balance; margin-bottom:1rem; }
        h2 { letter-spacing:-.025em; margin-top:2.25rem; }
        h3 { letter-spacing:-.012em; }
        p, label, .stMarkdown { line-height:1.58; }
        [data-testid="stForm"] { background:var(--panel); border:1px solid var(--ink);
          border-radius:0; padding:clamp(1rem,3vw,1.65rem); box-shadow:8px 9px 18px rgba(23,35,38,.10); }
        [data-testid="stMetric"] { background:transparent; border-top:1px solid var(--rule); padding-top:.75rem; }
        [data-testid="stMetricValue"] { color:var(--ink); letter-spacing:-.04em; }
        .stButton > button, [data-testid="stFormSubmitButton"] button {
          min-height:46px; border-radius:0; border:1px solid var(--ink); font-weight:700;
        }
        .stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button {
          background:var(--ink); color:var(--panel);
        }
        .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
          border-color:var(--cyan); color:var(--cyan-dark);
        }
        .stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] button:hover {
          background:var(--cyan-dark); color:#fff; border-color:var(--cyan-dark);
        }
        .stButton > button:disabled { opacity:.55; cursor:not-allowed; }
        button:focus-visible, input:focus-visible, [role="radiogroup"]:focus-visible {
          outline:3px solid #005fcc !important; outline-offset:3px;
        }
        [data-testid="stProgress"] > div > div { background:var(--cyan); }
        [data-testid="stAlert"] { border-radius:0; border:1px solid currentColor; }
        hr { border-color:var(--rule); }
        .brand { display:flex; align-items:center; gap:.7rem; font-size:1.25rem; font-weight:800;
          letter-spacing:-.02em; }
        .lens { width:2rem; height:2rem; display:grid; place-items:center; border:2px solid var(--cyan);
          border-radius:50%; color:var(--cyan-dark); font-size:.75rem; }
        .masthead { padding-bottom:.85rem; border-bottom:1px solid var(--rule); margin-bottom:2.1rem; }
        .calibration { color:var(--cyan-dark); letter-spacing:.24rem; font-size:.72rem;
          text-align:right; font-variant-numeric:tabular-nums; }
        .intro { max-width:58ch; font-size:1.08rem; color:var(--muted); margin-bottom:1.5rem; }
        .bench-rule { height:28px; margin:1.7rem 0 1rem; border-top:1px solid var(--cyan-dark);
          background:repeating-linear-gradient(90deg, var(--cyan-dark) 0 1px, transparent 1px 24px);
          background-size:auto 9px; background-repeat:repeat-x; }
        .instrument { display:grid; grid-template-columns:auto 1fr; gap:.85rem 1.1rem;
          align-items:center; border-top:1px solid var(--rule); border-bottom:1px solid var(--rule);
          padding:.85rem 0; max-width:32rem; }
        .instrument strong { font-size:2.65rem; letter-spacing:-.05em; line-height:1; }
        .instrument span { color:var(--muted); font-size:.9rem; }
        .instrument b { color:var(--cyan-dark); font-size:.72rem; letter-spacing:.08em;
          text-transform:uppercase; }
        .setup-note { max-width:64ch; color:var(--muted); font-size:.86rem; margin-top:1rem; }
        .sheet-head { display:flex; align-items:baseline; justify-content:space-between;
          gap:1rem; border-bottom:1px solid var(--soft-rule); margin-bottom:1rem; }
        .sheet-head strong { font-size:1.32rem; letter-spacing:-.02em; }
        .sheet-head span { color:var(--cyan-dark); font-size:.72rem; letter-spacing:.08em; }
        .status-strip { display:flex; flex-wrap:wrap; gap:.45rem 1.25rem; margin:.6rem 0 1.35rem;
          padding:.65rem 0; border-top:1px solid var(--soft-rule); border-bottom:1px solid var(--soft-rule);
          color:var(--muted); font-size:.82rem; }
        .status-strip b { color:var(--ink); font-weight:700; }
        .meta { text-transform:uppercase; font-size:.76rem; letter-spacing:.08em; color:var(--cyan-dark);
          word-spacing:.4rem; margin-bottom:.75rem; }
        .question-station { border-top:1px solid var(--ink); padding-top:1rem; margin-top:.6rem; }
        .question-station .counter { display:flex; justify-content:space-between; gap:1rem;
          color:var(--muted); font-size:.83rem; }
        .results-head { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:2rem;
          align-items:end; border-bottom:1px solid var(--ink); padding-bottom:1.4rem; margin-bottom:.6rem; }
        .score-dial { width:7.5rem; height:7.5rem; border:2px solid var(--cyan-dark);
          border-radius:50%; display:grid; place-content:center; text-align:center; }
        .score-dial strong { display:block; font-size:2.25rem; line-height:1; letter-spacing:-.05em; }
        .score-dial span { color:var(--muted); font-size:.74rem; margin-top:.35rem; }
        .section-rule { margin-top:2.4rem; padding-top:.7rem; border-top:1px solid var(--rule); }
        .footer { border-top:1px solid var(--rule); margin-top:4rem; padding-top:1rem;
          color:var(--muted); font-size:.82rem; max-width:78ch; }
        @media (max-width:760px) {
          .block-container { padding:1rem 1rem 3rem; }
          .masthead { margin-bottom:1.35rem; }
          h1 { font-size:2.55rem; }
          .calibration { display:none; }
          .results-head { grid-template-columns:1fr; }
          .score-dial { width:6.5rem; height:6.5rem; }
        }
        @media (prefers-reduced-motion:reduce) {
          *,*::before,*::after { scroll-behavior:auto !important; transition:none !important; animation:none !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def defaults() -> dict:
    params = st.query_params
    count = int(params.get("count", "10")) if str(params.get("count", "10")).isdigit() else 10
    topics = [unquote(item) for item in str(params.get("topics", "")).split("|") if item]
    difficulties = [item for item in str(params.get("difficulty", "")).split("|") if item]
    mode = str(params.get("source", "curated"))
    return {
        "count": count if count in range(5, 31, 5) else 10,
        "topics": [item for item in topics if item in TOPICS] or list(TOPICS),
        "difficulties": [item for item in difficulties if item in DIFFICULTIES] or list(DIFFICULTIES),
        "mode": mode if mode in {"curated", "ai"} else "curated",
    }


def initialize() -> None:
    if "phase" not in st.session_state:
        st.session_state.update(
            phase="setup",
            settings=defaults(),
            questions=[],
            answers={},
            question_index=0,
            locked=False,
            notice="",
            history=[],
        )


def save_settings(settings: dict) -> None:
    st.query_params.update(
        count=str(settings["count"]),
        topics="|".join(quote(item, safe="") for item in settings["topics"]),
        difficulty="|".join(settings["difficulties"]),
        source=settings["mode"],
    )


def go_home() -> None:
    st.session_state.update(
        phase="setup", questions=[], answers={}, question_index=0, locked=False, notice=""
    )


def start_quiz(settings: dict) -> None:
    save_settings(settings)
    curated = select_questions(
        CURATED_QUESTIONS,
        settings["count"],
        settings["topics"],
        settings["difficulties"],
    )
    assembled = curated
    notice = (
        f"{len(curated)} curated questions match this setup; the requested set size was "
        f"{settings['count']}."
        if len(curated) < settings["count"]
        else ""
    )
    if settings["mode"] == "ai":
        try:
            generated = generate_questions(
                min(10, max(1, (settings["count"] + 1) // 2)),
                settings["topics"],
                settings["difficulties"],
                [question.prompt for question in CURATED_QUESTIONS],
            )
            assembled = merge_unique(curated, generated, settings["count"])
            if len(assembled) < settings["count"]:
                notice = (
                    f"AI enhancement supplied fewer validated items than requested. "
                    f"This set contains {len(assembled)} safe questions."
                )
            else:
                notice = "This set combines validated AI-generated items with the curated bank."
        except AIUnavailable:
            notice = (
                "AI enhancement was unavailable or did not pass validation. "
                "Your set uses the curated question bank instead."
            )
    if not assembled:
        st.session_state.notice = (
            "No curated questions match that topic and difficulty combination. "
            "Choose another difficulty or add another topic."
        )
        return
    st.session_state.update(
        settings=settings,
        questions=assembled,
        answers={},
        question_index=0,
        locked=False,
        notice=notice,
        phase="quiz",
    )


def render_header() -> None:
    left, right = st.columns([4, 1], vertical_alignment="center")
    with left:
        st.markdown(
            '<div class="brand"><span class="lens">OC</span><span>OpticPrep</span></div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown('<div class="calibration">0 · 5 · 10 · 15 mm</div>', unsafe_allow_html=True)
    st.divider()


def render_setup() -> None:
    settings = st.session_state.settings
    intro, sheet = st.columns([0.9, 1.1], gap="large", vertical_alignment="top")
    with intro:
        st.title("Practice with precision.")
        st.markdown(
            '<p class="intro">Build a focused opticianry session, verify each answer, and leave '
            "with a clear review list. Every curated item was written for OpticPrep—not copied, "
            "recalled, or presented as examination content.</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="bench-rule" aria-hidden="true"></div>'
            f'<div class="instrument"><strong>{len(CURATED_QUESTIONS)}</strong>'
            '<span><b>Curated bank</b><br>Original questions · available without AI</span>'
            f'<strong>{len(TOPICS)}</strong><span><b>Coverage</b><br>Topics · three difficulty levels each</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="setup-note">Your setup choices are mirrored in the page URL. Answers and '
            "recent results stay only in this Streamlit session; a refresh, disconnect, or server "
            "restart may clear them.</p>",
            unsafe_allow_html=True,
        )
    with sheet:
        with st.form("setup_form"):
            st.markdown(
                '<div class="sheet-head"><strong>Configure the set</strong>'
                '<span>CALIBRATION SHEET</span></div>',
                unsafe_allow_html=True,
            )
            count = st.select_slider(
                "Question count", options=[5, 10, 15, 20, 25, 30], value=settings["count"]
            )
            topics = st.multiselect("Topics", TOPICS, default=settings["topics"])
            difficulties = st.multiselect(
                "Difficulty mix", DIFFICULTIES, default=settings["difficulties"]
            )
            mode_label = st.radio(
                "Question source",
                ("Curated only", "AI-enhanced"),
                index=1 if settings["mode"] == "ai" else 0,
                help="AI-enhanced mode always falls back visibly to curated questions.",
            )
            submitted = st.form_submit_button(
                "Start practice", type="primary", use_container_width=True
            )
        if submitted:
            if not topics or not difficulties:
                st.error("Select at least one topic and one difficulty.")
            else:
                next_settings = {
                    "count": count,
                    "topics": topics,
                    "difficulties": difficulties,
                    "mode": "ai" if mode_label == "AI-enhanced" else "curated",
                }
                start_quiz(next_settings)
                if st.session_state.phase == "quiz":
                    st.rerun()
        if st.session_state.notice and st.session_state.phase == "setup":
            st.error(st.session_state.notice)
    if st.session_state.history:
        st.divider()
        st.subheader("Recent sessions")
        for entry in st.session_state.history[:8]:
            st.write(f"**{entry['correct']}/{entry['total']}** · {entry['label']}")


def render_quiz() -> None:
    questions: list[Question] = st.session_state.questions
    index = st.session_state.question_index
    question = questions[index]
    source_label = "AI-generated" if question.source == "ai" else "Curated bank"
    st.markdown('<div class="question-station"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="meta">{question.topic} · {question.difficulty}</div>'
        f'<div class="status-strip"><span>Source <b>{source_label}</b></span>'
        f'<span>Set <b>{len(questions)} questions</b></span>'
        '<span>Feedback <b>after submission</b></span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="counter"><strong>Question {index + 1} of {len(questions)}</strong>'
        f"<span>{round(100 * (index + 1) / len(questions))}% through set</span></div>",
        unsafe_allow_html=True,
    )
    st.progress((index + 1) / len(questions), text="Practice set progress")
    if st.session_state.notice and index == 0:
        st.info(st.session_state.notice)
    st.subheader(question.prompt)
    selected = st.radio(
        "Choose one answer",
        range(4),
        format_func=lambda option: f"{option + 1}.  {question.options[option]}",
        index=None if question.id not in st.session_state.answers else st.session_state.answers[question.id],
        disabled=st.session_state.locked,
        key=f"answer_{question.id}",
    )
    if not st.session_state.locked:
        if st.button(
            "Submit answer",
            type="primary",
            disabled=selected is None,
            use_container_width=True,
        ):
            st.session_state.answers[question.id] = selected
            st.session_state.locked = True
            st.rerun()
    else:
        chosen = st.session_state.answers[question.id]
        correct = chosen == question.correctIndex
        label = "Correct." if correct else "Not quite."
        feedback = (
            f"**{label}** {question.rationale}\n\n"
            f"Correct answer: {question.options[question.correctIndex]}"
        )
        (st.success if correct else st.error)(feedback)
        button_label = "See results" if index == len(questions) - 1 else "Next question"
        if st.button(button_label, type="primary", use_container_width=True):
            if index == len(questions) - 1:
                result = score_questions(questions, st.session_state.answers)
                st.session_state.history.insert(
                    0,
                    {
                        "correct": result["correct"],
                        "total": result["total"],
                        "label": "completed this session",
                    },
                )
                st.session_state.history = st.session_state.history[:8]
                st.session_state.phase = "results"
            else:
                st.session_state.question_index += 1
                st.session_state.locked = False
            st.rerun()
    st.caption("Use Tab and Space/Enter with the standard Streamlit controls.")
    if st.button("Leave this set", type="secondary"):
        go_home()
        st.rerun()


def render_results() -> None:
    questions = st.session_state.questions
    result = score_questions(questions, st.session_state.answers)
    percent = round(100 * result["correct"] / result["total"]) if result["total"] else 0
    st.markdown(
        '<div class="results-head"><div><h1>Session complete.</h1>'
        '<p class="intro">Use the breakdown as a study map, not a readiness prediction. '
        "Review missed reasoning, then build a new set when you are ready.</p></div>"
        f'<div class="score-dial"><strong>{percent}%</strong><span>SESSION ACCURACY</span></div></div>',
        unsafe_allow_html=True,
    )
    score, rate, missed = st.columns(3)
    score.metric("Correct", f"{result['correct']} / {result['total']}")
    rate.metric("Accuracy", f"{percent}%")
    missed.metric("To review", len(result["missed"]))
    st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
    st.subheader("Topic breakdown")
    for row in result["by_topic"]:
        left, middle, right = st.columns([3, 5, 1], vertical_alignment="center")
        left.write(row["topic"])
        middle.progress(row["correct"] / row["total"])
        right.write(f"**{row['correct']}/{row['total']}**")
    st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
    st.subheader("Missed review")
    if not result["missed"]:
        st.success("Clear verification: no missed questions in this set.")
    for question in result["missed"]:
        chosen = st.session_state.answers.get(question.id)
        st.divider()
        st.markdown(f"**{question.prompt}**")
        st.write(f"Your answer: {question.options[chosen] if chosen is not None else 'No answer'}")
        st.write(f"Correct answer: **{question.options[question.correctIndex]}**")
        st.caption(question.rationale)
    retry, another = st.columns(2)
    with retry:
        if result["missed"] and st.button("Retry missed", type="primary", use_container_width=True):
            st.session_state.update(
                questions=result["missed"], answers={}, question_index=0, locked=False,
                notice="Retrying only the questions you missed.", phase="quiz"
            )
            st.rerun()
    with another:
        if st.button("Build another test", use_container_width=True):
            go_home()
            st.rerun()


load_css()
initialize()
render_header()
if st.session_state.phase == "setup":
    render_setup()
elif st.session_state.phase == "quiz":
    render_quiz()
else:
    render_results()
st.markdown(
    '<div class="footer"><strong>Educational practice only.</strong> OpticPrep is independent '
    "and is not affiliated with or endorsed by ABO-NCLE. It does not reproduce or predict "
    "certification examinations. Content is not medical, legal, or regulatory advice; verify "
    "current standards, manufacturer guidance, and local requirements with qualified sources.</div>",
    unsafe_allow_html=True,
)
