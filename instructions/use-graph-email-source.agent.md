---
description: "Use when retrieving [CR]-tagged mailbox messages with tools/graph_email_source.py."
---

- Use `tools/graph_email_source.py` to retrieve messages from Microsoft Graph when processing incoming `[CR]` emails.
- Set `GRAPH_ACCESS_TOKEN` to a valid access token with `Mail.Read` permission and `GRAPH_USER_ID` to the mailbox user's ID or UPN; never put tokens in command arguments, source files, or logs.
- Run `python tools/graph_email_source.py` from the repository root. Set `GRAPH_MAIL_FOLDER_ID` or pass `--folder-id <folder-id>` to limit retrieval to a specific mail folder; without it, the source requests messages from the mailbox.
- The script follows Graph pagination and prints matching messages as a JSON array with `id`, `subject`, `body`, `sender`, and `received_date`. It keeps messages whose subject contains `[CR]`.
- Treat the output as retrieved email data only; this script does not create drafts, deduplicate messages, or write registry files.
- If the script reports missing environment variables, set them before retrying. For Graph authentication or permission errors, refresh the token or verify `Mail.Read` access; surface other errors rather than treating them as an empty result.
