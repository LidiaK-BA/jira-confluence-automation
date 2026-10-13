# Module 10 Completion Report

## Instruction Files
```text
Directory: C:\Workspace\hello-genai\instructions


Mode                 LastWriteTime         Length Name                                                                 
----                 -------------         ------ ----                                                                 
-a----        13/10/2026     16:49            879 create-status-report.agent.md                                        
-a----        13/10/2026     17:00          16576 creating-instructions.agent.md                                       
-a----        13/10/2026     17:13           1238 main.agent.md
```

## main.agent.md Contents
```markdown
---
description: Index of instruction files in this project.
---

# Instructions Catalog

Each entry is an instruction file with a brief description. Use the keywords to route matching requests to the relevant instruction.

---

- [`./instructions/creating-instructions.agent.md`](./creating-instructions.agent.md) — create or update reusable project instructions and configure IDE-specific entry points.
  + Keywords: create instructions, update instructions, instruction catalog, Copilot prompt, instruction setup
- [`./instructions/create-status-report.agent.md`](./create-status-report.agent.md) — generate a concise weekly status report.
  + Keywords: weekly status report, accomplishments, blockers, next week
- [`../.github/instructions/list-filtering.instructions.md`](../.github/instructions/list-filtering.instructions.md) — implement consistent filtering of CR registry records.
  + Keywords: list filters, registry filtering, sub-project, status, priority, owner
- [`../.github/instructions/report-grouping.instructions.md`](../.github/instructions/report-grouping.instructions.md) — group CRs into the weekly report structure.
  + Keywords: report grouping, weekly report, sub-project, report group
```

## Sample Instruction
- File: report-grouping.instructions.md
- Contents:
```markdown
---
description: "Use when implementing or changing CR weekly report grouping by sub-project and status report group."
---

- **Input format:** Accept confirmed CR records, the configured sub-projects, the status-to-report-group mapping, and the configured Closed-section behavior (including the previous report date when needed).
- **Processing steps:**
  + Exclude drafts before grouping.
  + For each configured sub-project, group its CRs into `Open`, `In Progress`, `On Hold`, and `Closed` using the status mapping.
  + Apply the configured Closed-section behavior; do not assume whether it means all closed CRs or only those closed since the previous report.
- **Output format:** Produce a nested grouping of sub-project → report group → CR records, then render one Markdown section per sub-project and a section for each of the four report groups. Use the report columns from the specification; include `Status` only in the `In Progress` table.
- **Constraints:** Each confirmed CR must appear at most once, under its own sub-project and mapped group. Preserve the input order within groups, retain empty groups cleanly, and never include drafts or `cost` in report output.
```
