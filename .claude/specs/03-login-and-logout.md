# Spec: Login and Logout

## Overview
This step implements session-based authentication for Spendly. When a registered user submits valid credentials via the login form, their password is verified with werkzeug, a Flask session is started storing `user_id` and `user_name`, and they are redirected to their profile page. When they log out, the session is cleared and they are redirected to the landing page. The navbar in `base.html` is updated to show context-aware links — authenticated users see their name and a logout link; guests see "Sign in" and "Get started".

## Depends on
- Step 01 — Database Setup (users table must exist)
- Step 02 — Registration (a user must be creatable to test login)

## Routes
- `GET  /login`  — render login form; redirect to profile if already logged in — public
- `POST /login`  — verify email/password, start session, redirect to `/profile` — public
- `GET  /logout` — clear session, redirect to `/` — logged-in (safe to call when logged out too)

## Database changes
- `database/db.py` — update `get_user_by_email` query from `SELECT id` to `SELECT *` so the login handler can access `password_hash` and `name` from the returned row. The existing truthy-check usage in the registration handler continues to work unchanged.

## Templates
- **Modify:** `templates/login.html` — add `value="{{ email }}"` to the email input so it re-populates on a validation failure re-render.
- **Modify:** `templates/base.html` — update the `<div class="nav-links">` block to conditionally show authenticated vs guest links based on `session.user_id`.

## Files to change
- `app.py` — set `app.secret_key`, convert `/login` from GET-only to GET+POST with full auth logic, implement `/logout` to clear session and redirect.
- `database/db.py` — update `get_user_by_email` to `SELECT *` instead of `SELECT id`.
- `templates/login.html` — add `value` attribute to the email field.
- `templates/base.html` — add conditional nav links based on session state.

## Files to create
No new files.

## New dependencies
No new dependencies. `werkzeug.security.check_password_hash` is already available via the existing `werkzeug` dependency.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw sqlite3 via `get_db()`
- Parameterised queries only — never string-format user input into SQL
- Passwords verified with `werkzeug.security.check_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- `app.secret_key` must be set; use `os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")` so it can be overridden in production
- Store only `user_id` (int) and `user_name` (str) in the session — never the password hash
- Login error message must be generic: "Invalid email or password." — never reveal which field was wrong
- After a failed login, re-render `login.html` with the submitted `email` value so the field is pre-populated
- `/logout` uses `session.clear()` then `redirect(url_for("landing"))`
- `GET /login` redirects to `/profile` if `session.get("user_id")` is already set

## Definition of done
- [ ] `GET /login` renders the form when not logged in
- [ ] `GET /login` redirects to `/profile` when already logged in
- [ ] Submitting valid credentials sets a session and redirects to `/profile`
- [ ] Submitting a non-existent email re-renders the form with "Invalid email or password."
- [ ] Submitting a wrong password re-renders the form with "Invalid email or password."
- [ ] After a failed login, the email field is pre-populated with the submitted value
- [ ] Visiting `/logout` clears the session and redirects to the landing page
- [ ] After logout, visiting `/login` no longer has a session
- [ ] When logged in, the navbar shows the user's name and a "Log out" link
- [ ] When logged out, the navbar shows "Sign in" and "Get started" as before
- [ ] `session` never contains the password or password hash
