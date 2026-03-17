# Recommended Repo Structure

```text
sqlite-browser/
├─ .gitignore
├─ README.md
├─ pyproject.toml
├─ .python-version                  # optional
├─ .venv/                           # local only, ignored by git
├─ demo/
│  ├─ test.sqlite
│  └─ README.md
├─ docs/
│  ├─ 00-repo-structure.md
│  ├─ 01-product-requirements.md
│  ├─ 02-architecture.md
│  ├─ 03-ui-ux-spec.md
│  ├─ 04-api-spec.md
│  ├─ 05-testing-strategy.md
│  ├─ 06-delivery-plan.md
│  └─ 07-codex-build-brief.md
├─ src/
│  └─ sqlite_browser/
│     ├─ __init__.py
│     ├─ __main__.py
│     ├─ app.py
│     ├─ cli.py
│     ├─ config.py
│     ├─ db.py
│     ├─ models.py
│     ├─ session_store.py
│     ├─ routes/
│     │  ├─ pages.py
│     │  └─ api.py
│     ├─ templates/
│     │  └─ index.html
│     └─ static/
│        ├─ app.css
│        └─ app.js
└─ tests/
   ├─ test_db.py
   ├─ test_api.py
   ├─ test_upload.py
   ├─ test_smoke.py
   └─ e2e/
      └─ sqlite_browser.spec.ts
```

## Notes

- Keep the runtime app free of any Node/Vite/React build chain for v1.
- Use a local `.venv` in the repo root.
- Add a small demo SQLite database under `demo/test.sqlite` once the implementation exists.
- Include `data-testid` attributes from the start so Playwright MCP can drive the UI reliably.
