# Authentication configuration

Tender Radar reads its login credentials only on the Streamlit server from:

- `TENDER_RADAR_USERNAME`
- `TENDER_RADAR_PASSWORD`

Production values belong in the Render service environment. They must not be
placed in `render.yaml`, source files, logs, documentation, or browser code.
`render.yaml` declares both variables with `sync: false` so a Render Blueprint
requests secret values without storing them in Git.

For local development, copy `.env.example` only as a reference and set the two
variables in the local process environment. A local `.env` file is ignored by
Git, but the application intentionally does not parse it or send it to the
browser.

The login fails closed when either variable is missing. Password and username
comparison uses `hmac.compare_digest`, the form clears submitted values, and a
page reload starts a new unauthenticated Streamlit session.

Any credential that was previously embedded in a commit must be considered
retired and replaced in Render. Rewriting shared Git history is not necessary
after rotation and would add avoidable deployment risk to this private
repository.
