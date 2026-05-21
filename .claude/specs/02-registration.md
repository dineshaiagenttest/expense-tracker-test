# Spec: Registration

## Overview
This step wires up the registration form that already exists in `templates/register.html` to a working POST handler. When a visitor submits the form, their name, email, and password are validated, the password is hashed with werkzeug, and a new row is inserted into the `users` table. On success the user is redirected to the login page with a flash message; on failure the form is re-rendered with an inline error. A Flask session is not started here — that is deferred to Step 3 (Login).

## Depends on
- Step 01 — Database Setup (users table must exist)

## Routes
- `GET  /register` — render registration form — public
- `POST /register` — process form submission, create user, redirect to login — public

## Database changes
No database changes. The `users` table (id, name, email, password_hash, created_at) already exists from Step 01.

## Templates
- **Modify:** `templates/register.html` — already renders `{{ error }}`; no structural changes needed. Ensure `value="{{ name }}"` and `value="{{ email }}"` are added to inputs so the form re-populates on validation failure.

## Files to change
- `app.py` — convert `/register` from GET-only to accept POST; add validation logic, DB insert, and redirect.
- `database/db.py` — add `create_user(name, email, password)` and `get_user_by_email(email)` helper functions.
- `templates/register.html` — add `value` attributes to name and email inputs for re-population on error.

## Files to create
No new files.

## New dependencies
No new dependencies. `werkzeug.security` is already available via the existing `werkzeug==3.1.6` dependency.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw sqlite3 via `get_db()`
- Parameterised queries only — never string-format user input into SQL
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Server-side validation must cover:
  - Name: required, 1–100 characters
  - Email: required, must not already exist in `users`
  - Password: required, minimum 8 characters
- On duplicate email show the error: "An account with that email already exists."
- On success redirect to `/login` — do not auto-login the user (that is Step 3)
- Use `flask.redirect` and `flask.url_for` for redirects
- Import `request` from flask to access `form` data
- The `create_user` helper in `db.py` should catch `sqlite3.IntegrityError` for the UNIQUE constraint as a safety net and re-raise a descriptive exception

## Definition of done
- [ ] Visiting `GET /register` renders the form with no errors
- [ ] Submitting the form with all valid fields creates a row in `users` and redirects to `/login`
- [ ] Submitting with a name shorter than 1 character re-renders the form with an error message
- [ ] Submitting with a password shorter than 8 characters re-renders the form with an error message
- [ ] Submitting with an email that already exists re-renders the form with "An account with that email already exists."
- [ ] After a validation error, the name and email fields are pre-populated with the submitted values
- [ ] The stored password_hash in the database is not the plain-text password (verify with a direct DB query)
- [ ] No raw SQL strings contain user input directly (all queries use `?` placeholders)
