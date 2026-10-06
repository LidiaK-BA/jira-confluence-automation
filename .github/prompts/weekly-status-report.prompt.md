---
description: Draft the weekly status report email from my raw notes
agent: agent
---
Draft this week's status report from my notes: ${input:notes:Paste or attach your raw notes / meeting notes}

Rules:
- Follow the structure of [the template](../../work/weekly-status-report.md): Accomplishments, Blockers, Next Week's Plan.
- Fill the header: week of (Monday of the current week, YYYY-MM-DD), team, author.
- Audience: project manager and the tech team. Neutral, factual tone; no hype or filler.
- Use only information from my notes. If something is missing (owner, ETA, decision needed), write "TBD" and list it under "Open questions" at the end instead of guessing.
- Blockers must include owner, needed action/decision, and ETA.
- Save the draft to `work/status-reports/YYYY-MM-DD-weekly-status-report.md`.
- Format it as an email: a `Subject:` line ("Weekly Status Report – <team> – week of YYYY-MM-DD"), a short greeting, the report body, and a sign-off.
- Do not send anything. This is a draft for my review.
