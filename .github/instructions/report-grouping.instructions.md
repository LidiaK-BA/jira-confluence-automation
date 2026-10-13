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
