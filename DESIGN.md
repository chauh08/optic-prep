# OpticPrep design system

## Direction

**Mode:** Operate. **Visual world:** a quiet optical workbench. The interface borrows
calibration marks, lens-center diagrams, ruled verification sheets, and precise instrument
labels without turning them into decoration. The first viewport pairs a concise practice
brief with a compact calibration sheet. It should feel measured, adult, and trustworthy—not
clinical theater or game UI.

## Principles

1. **Precision before pace.** Each screen has one dominant decision and explicit state.
2. **Evidence, not celebration.** Results expose topic performance and missed reasoning; no badges, streaks, confetti, or readiness claims.
3. **The bank survives.** Offline/no-token use remains first-class and AI fallback is named.
4. **Native familiarity.** Streamlit radio controls, buttons, progress, labels, status messages, and headings preserve expected keyboard and screen-reader behavior.
5. **Calculated means verifiable.** Numeric variants are deterministic, concise, and display
   the calculation used in their rationale.

## Tokens

- Paper `#F6F3EB`; panel `#FFFDF7`; ink `#172326`; muted `#5E6A6B`
- Calibration cyan `#007F82` (selection/progress); dark cyan `#005E60`
- Error `#A53C32`; success `#236D50`; focus `#005FCC`
- Rules are 1 px and square-edged. The setup sheet alone uses a restrained offset shadow.
- UI type is Inter when available, then Segoe UI/Arial/system sans. Monospace is limited to keys and measurements.
- Instrument readouts use tabular numerals; cyan wash is reserved for optical reference detail.

## Layout and components

Desktop setup uses an asymmetric two-column instrument/work-sheet composition; mobile collapses
to a single task stream. Quiz content stays focused on one question. Cards are not page
scaffolding: lists use rules and state fills. Primary controls are dark ink; cyan is reserved
for selection, instrument marks, and progress. Results pair a circular accuracy readout with
plain metrics, a topic verification table, and missed-item evidence. Focus rings are 3 px blue
with offset. Static CSS and fixed interface labels are the only unsafe-HTML use; generated
question and rationale text goes through Streamlit's safe renderers.

## Motion and access

Only Streamlit's native progress behavior may move, and custom transitions stop under
`prefers-reduced-motion`. Feedback uses explicit Correct/Not quite copy and native status
containers. Color never carries correctness alone. Primary actions are at least 44 px, and
layouts remain usable from 320 px.
