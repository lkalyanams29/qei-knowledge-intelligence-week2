# Deploying the Python/Streamlit version

## Current state

The active codebase is now Python/Streamlit. The existing chatgpt.site URL still serves the earlier React/Worker release. Its runtime requires Cloudflare-compatible JavaScript/WebAssembly and cannot directly execute a long-running Streamlit Python server. It has **not** been republished with a fake representation of the new Python app.

Run `python -m streamlit run ui.py` for the actual application. For local-only use, bind to `127.0.0.1`. The demo requires no application login and contains only the approved public sample, public/design notes and clearly labeled synthetic exports.

## Streamlit Community Cloud

Following [Streamlit's deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app):

1. Sign in to your own Streamlit Community Cloud account and connect the Week 2 GitHub repository.
2. Select `lkalyanams29/qei-knowledge-intelligence-week2`, branch `main`, entry point `ui.py`.
3. Select Python 3.12. The root `requirements.txt` pins the tested packages.
4. Deploy the public demo. The first launch generates the local index from the included file corpus; it does not call enterprise sources.
5. Leave model configuration unset for no-key excerpt mode. If using an approved model endpoint, configure its values in the hosting secret store, never in GitHub. A laptop localhost endpoint will not work from a remote host.
6. Verify citations, scope filters, unknown-ID refusal, conflict disclosure and comparison results on the resulting host.

Creating an account, granting a hosting service access to GitHub, or choosing a public hosted URL requires the owner's action. This migration did not create a Streamlit account or claim a new public deployment URL.

## Internal Python host

Use an isolated Python 3.12 environment and the same install/ingest/test/run commands in the README. Terminate HTTPS at a managed reverse proxy and keep Streamlit's CORS/XSRF protections enabled. The shipped UI intentionally grants **no private scopes**. Before real enterprise deployment, add verified server-side identity mapping and source-level access inheritance; do not turn the project selector into authorization.

For private data, use ignored `sources/private/` exports and a private local index path. Never publish private indexes, embeddings, logs, prompts or derived summaries into the public GitHub repo. Monitor process health, memory and request latency, and arrange an approved refresh job and backups separately.

## Legacy source preservation

`legacy/sites/` retains the earlier React/Worker sources and `.openai/hosting.json`. The legacy README/report and previous evaluation files describe that historical version. The existing hosted release continues to run independently. The root Python app does not need legacy Node dependencies.
