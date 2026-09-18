# OpticPrep design system

## Direction

**Mode:** Operate. **Visual world:** a quiet optical workbench. The interface borrows calibration marks, lens-center diagrams, ruled verification sheets, and precise instrument labels without turning them into decoration. It should feel measured, adult, and trustworthy—not clinical theater or game UI.

## Principles

1. **Precision before pace.** Each screen has one dominant decision and explicit state.
2. **Evidence, not celebration.** Results expose topic performance and missed reasoning; no badges, streaks, confetti, or readiness claims.
3. **The bank survives.** Offline/no-token use remains first-class and AI fallback is named.
4. **Native familiarity.** Semantic fieldsets, radio controls, buttons, progress, and headings preserve expected keyboard and screen-reader behavior.

## Tokens

- Paper `#F6F3EB`; panel `#FFFDF7`; ink `#172326`; muted `#5E6A6B`
- Calibration cyan `#007F82` (selection/progress); dark cyan `#005E60`
- Error `#A53C32`; success `#236D50`; focus `#005FCC`
- Rules are 1 px and square-edged. The setup sheet alone uses an offset hard shadow.
- UI type is Inter when available, then Segoe UI/Arial/system sans. Monospace is limited to keys and measurements.

## Layout and components

Desktop setup uses an asymmetric two-column instrument/work-sheet composition; mobile collapses to a single task stream. Quiz content is held to 880 px and one question. Cards are not page scaffolding: lists use rules and state fills. Primary controls are dark ink; cyan is reserved for selection and progress. Focus rings are 3 px blue with offset.

## Motion and access

Only progress width and loading skeleton opacity move, and both stop under `prefers-reduced-motion`. Feedback uses `aria-live`; errors use alerts. Color never carries correctness alone. Target sizes are at least 44 px for primary actions, and layouts remain usable from 320 px.
