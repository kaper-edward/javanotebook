# Repository Guidelines

## Project Structure & Module Organization
`src/javanotebook` contains the FastAPI app, routers, and static assets (`static/`, `templates/`). Examples that back the development server live under `examples/`. Tests are split into `tests/unit` for isolated components and `tests/integration` for API-level flows. Reusable testing fixtures are defined in `tests/conftest.py`.

## Build, Test, and Development Commands
Use `make install-dev` for a full editable install with tooling; run `make setup` if you also want pre-commit hooks configured. Start the sample server against `examples/basic_java.md` with `make dev` (append `PORT=8080` or use `make dev-port` for alternates). Execute all checks via `make check`, or target a specific step: `make test`, `make test-unit`, `make test-integration`, `make lint`, `make format`, `make typecheck`, and `make coverage`.

## Coding Style & Naming Conventions
Write Python 3.8+ code with 4-space indentation. Follow the Black 88-character line length and the isort Black profile; run `make format` before committing. Maintain descriptive snake_case for Python identifiers and kebab-case for Make targets. Keep FastAPI routers organized by feature within `src/javanotebook/routers/`, naming modules after the exposed route group.

## Testing Guidelines
Prefer pytest fixtures for server setup and mark slow scenarios with `@pytest.mark.slow`. Name new test modules `test_*.py` and group integration cases under `tests/integration`. Run `make coverage` to ensure meaningful paths stay covered; highlight gaps or intentionally skipped sections in the PR description.

## Commit & Pull Request Guidelines
Commits follow Conventional Commit prefixes (`feat:`, `fix:`, etc.) as seen in the history (`feat: add comprehensive Jupyter notebook support...`). Keep commits focused and include the why in the body when behavior changes. For pull requests, provide a concise summary, link related issues, note required manual checks (e.g., Java version, browser testing), and attach screenshots or terminal logs when UI responses or CLI output change.

## Java & Environment Setup
Verify Java tooling before server work with `make check-java`; the project expects Java 8+ available via `java` and `javac` on PATH. When troubleshooting compilation errors, confirm the active JDK matches the target notebooks and document any local overrides in the PR.
