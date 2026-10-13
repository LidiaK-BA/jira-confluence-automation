# Backlog instructions
description: "Use when implementing or changing CR registry list filters for sub-project, status, priority, or owner."
---

- **Input format:** Accept the registry's CR records and optional filters for `sub_project`, `status`, `priority`, and `owner`. Treat omitted filters as unset.
- **Processing steps:**
  + Validate supplied filter values against the configured sub-projects and CR model enums where applicable.
  + Return a CR only when it matches every supplied filter.
  + Exclude drafts by default; include them only if an explicit, existing option requests them.
- **Output format:** Return matching CR records as a sequence in registry order; let the existing CLI presentation render that sequence without changing its established format.
- **Constraints:** Do not mutate records or the registry. Do not silently ignore invalid filters or add unrequested filters.
