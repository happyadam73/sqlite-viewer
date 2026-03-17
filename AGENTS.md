# Agent Guidelines

These guidelines describe how AI agents and coding tools should behave when working in this repository.

## 1. Source of Truth

- The planning and requirements documents under `docs/` are the current **source of truth** for requirements, architecture, and constraints.
- In particular, rely on `docs/01-product-requirements.md`, `docs/02-architecture.md`, `docs/03-ui-ux-spec.md`, `docs/04-api-spec.md`, `docs/05-testing-strategy.md`, and `docs/06-delivery-plan.md`.
- Before making any non-trivial change, re-read the relevant section in `docs/`.
- Do not contradict the docs. If something appears inconsistent, call it out in your notes instead of silently diverging.

## 2. Execution Plan

- The file `PLAN.md` at the repo root defines the current execution plan.
- Work **milestone by milestone**:
  - When asked to implement something, assume the intent is to implement a specific milestone from `PLAN.md` (for example, "Milestone 1").
  - Do not skip ahead to later milestones unless explicitly requested.
  - Do not modify milestones unless explicitly asked to refine the plan.
  - When a checklist task is completed and verified, update `PLAN.md` by changing `- [ ]` to `- [x]`.

## 3. Prompting Style

- Assume prompts from the user will be **minimal**, for example:
  - "Implement Milestone 1 from PLAN.md."
  - "Update the plan based on new requirements in docs/."
- Do **not** rely on the chat history as the canonical spec; always defer to:
  1. `docs/`
  2. `PLAN.md`
  3. The current codebase
- Avoid duplicating detailed requirements in the chat; keep them in the docs and `PLAN.md`.

## 4. Change Management

- Prefer **small, incremental changes** over large refactors.
- Keep the planning docs in `docs/` **read-only** unless explicitly instructed to revise them.
- When implementing a milestone:
  - Touch only the files needed for that milestone.
  - Avoid introducing new top-level directories or technologies not mentioned in the docs.
- Document any important decisions or deviations by updating `PLAN.md` under the relevant milestone when needed.

## 5. Plan Mode Behaviour

- When operating in a "plan" or "review" mode:
  - First update `PLAN.md` to reflect the intended changes.
  - Then propose file edits aligned with the updated plan.
- When in doubt, refine `PLAN.md` rather than inventing new requirements in the code.

## 6. Tests and Quality

- When milestones mention tests, treat them as first-class:
  - Add or update tests alongside implementation.
  - Use the project's existing testing tools and conventions.
- Favour clarity and maintainability over cleverness.

## 7. Project-Specific Notes

- The target runtime is Python 3.13 with FastAPI, Jinja2, vanilla JavaScript, plain CSS, and the standard-library `sqlite3` module.
- The product is intentionally local-only and read-only; do not add edit operations, arbitrary SQL execution, remote DB support, auth, or collaboration features unless the docs change.
- Keep the v1 frontend free of a Node, Vite, React, or other SPA build pipeline unless the requirements docs are explicitly revised.
- Preserve the required API surface from `docs/04-api-spec.md` and the required `data-testid` selectors from `docs/03-ui-ux-spec.md`.
- Treat Playwright-friendly behaviour, explicit loading and error states, and the happy-path `python -m sqlite_browser --db demo/test.sqlite` flow as core acceptance criteria.
