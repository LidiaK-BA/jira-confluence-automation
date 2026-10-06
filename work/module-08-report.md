# Module 08 Completion Report

## Tracked Files
```
.github/prompts/weekly-status-report.prompt.md
PROJECT_IDEAS.md
project_spec.md
work/module-03-report.md
work/module03-task
work/weekly-status-report.md
```

## Spec Commit History
```
3d62d9b (HEAD -> main) Module 8 Commit
```

## project_spec.md Contents
````markdown
# Change Request (CR) Registry – Technical Specification

## 1. Overview

A registry that tracks and summarizes change requests (CRs) across the CargoWise integration sub-projects of the TMS integration project. It is the single source of truth for CRs, which currently arrive by email, and produces a weekly status report for stakeholders.

| Item | Value |
|---|---|
| Owner | Business Analyst (BA) |
| Team size | 8 people |
| Scale | ~20 CRs currently; several integration sub-projects |
| Storage | Markdown/CSV files in the workspace, synced to a Jira/Confluence-permissioned location |
| Report format | Markdown table, weekly |

## 2. Goals and Non-Goals

### Goals
- Maintain one authoritative list of all CRs across sub-projects.
- Capture CRs from emails tagged `[CR]` as drafts for BA review.
- Track each CR through its lifecycle, including backward transitions.
- Generate a weekly Markdown report grouped by status group, per sub-project.
- Restrict access to people with access to the project's Jira.

### Non-Goals
- Cost is not shown in any report (see 5.2).
- The weekly report does not feed into `work/weekly-status-report.md`.
- No approval workflow or approver tracking in v1.
- No attachment storage; documents are referenced by link only.

## 3. Users and Roles

| Role | Capabilities |
|---|---|
| BA | Create, review, edit, change status of CRs; generate reports; run ingestion |
| Team members (up to 7) | View CRs; edit CRs they own (assumption, to be confirmed) |
| Stakeholders | Read the weekly report only; must have Jira project access |

## 4. Functional Requirements

### 4.1 CR intake
- FR-1: The system monitors a mailbox (Outlook/Microsoft Graph) for emails whose subject contains `[CR]`.
- FR-2: Each matching email creates a **draft** CR with fields pre-filled from the email (title from subject, description from body, requester from sender, received date).
- FR-3: Drafts are not part of the registry or reports until the BA reviews, completes, and confirms them.
- FR-4: Each email is processed once (deduplicate by message ID); the source email reference is stored on the CR.
- FR-5: The BA can also create a CR manually.

### 4.2 CR management
- FR-6: Create, view, update, and list CRs; filter by sub-project, status, priority, owner.
- FR-7: IDs are auto-generated per sub-project prefix, e.g. `CW-001` (see 8, open question 1).
- FR-8: Every status change is recorded in a history log (timestamp, old status, new status, changed by).
- FR-9: Statuses may move forward or backward (e.g. In Testing → Dev); any status may move to On Hold or Rejected.

### 4.3 Reporting
- FR-10: Generate a weekly Markdown report (see 6).
- FR-11: Reports exclude cost and drafts.

## 5. Data Model

### 5.1 Lifecycle statuses

`Open` → `Requirements and Discovery` → `Ready for Dev` → `Dev` → `Ready for Testing` → `In Testing` → `Closed`

Additional statuses: `On Hold`, `Rejected`.

| Report group | Statuses |
|---|---|
| Open | Open |
| In Progress | Requirements and Discovery, Ready for Dev, Dev, Ready for Testing, In Testing |
| On Hold | On Hold |
| Closed | Closed, Rejected |

### 5.2 CR fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | `<PREFIX>-<NNN>`, unique, auto-generated |
| `title` | string | yes | |
| `description` | text | yes | |
| `sub_project` | enum | yes | Integration sub-project; determines ID prefix |
| `requester` | string | yes | |
| `owner` | string | yes | Team member responsible |
| `priority` | enum | yes | High / Med / Low |
| `status` | enum | yes | See 5.1 |
| `scope_impact` | text | no | |
| `effort_hours` | number | no | Estimated effort in hours |
| `schedule_impact` | text | no | |
| `cost` | number | no | Stored internally; never shown in reports |
| `affected_systems` | list | no | Systems/interfaces (e.g. CargoWise, TMS) |
| `jira_url` | URL | no | Link only; no other Jira data is stored |
| `document_links` | list of URLs | no | |
| `source_email_id` | string | no | Message ID of originating email |
| `created_date` | date | yes | |
| `updated_date` | date | yes | |
| `is_draft` | boolean | yes | True until BA confirms |

### 5.3 Storage layout (proposed)

```
cr-registry/
  registry.csv          # one row per confirmed CR
  drafts.csv            # CRs awaiting BA review
  history.csv           # status change log
  reports/
    cr-report-YYYY-MM-DD.md
```

## 6. Weekly Report

- Frequency: once a week.
- Format: Markdown table(s), one section per sub-project.
- Grouped by: Open, In Progress, On Hold, Closed.
- Columns (proposed): ID, Title, Status, Priority, Owner, Effort (h), Jira link.
- Excluded: cost, drafts.
- "Closed" shows CRs closed or rejected since the previous report (see open question 3).

Example:

```markdown
## CargoWise – Sub-project A

### Open
| ID | Title | Priority | Owner | Effort (h) | Jira |
|---|---|---|---|---|---|
| CW-001 | Example CR | High | Name | 16 | link |

### In Progress
| ID | Title | Status | Priority | Owner | Effort (h) | Jira |
|---|---|---|---|---|---|---|

### On Hold
...

### Closed
...
```

## 7. Non-Functional Requirements

- NFR-1 **Access control:** The registry and reports are stored only in a Jira/Confluence-permissioned location so that access is limited to people with access to the project's Jira. Local copies must not be shared outside that group.
- NFR-2 **Confidentiality:** Cost data is stored but never appears in reports or exports.
- NFR-3 **Auditability:** All status changes are logged in `history.csv`.
- NFR-4 **Mailbox access:** Ingestion uses read-only access to the designated mailbox; credentials are not stored in the repository.
- NFR-5 **Scale:** Designed for tens of CRs; no database is required.
- NFR-6 **Portability:** Plain-text files (CSV/Markdown) that are diff-friendly and readable without tooling.

## 8. Open Questions

1. Names and ID prefixes of the sub-projects (not provided; `CW-` is the example prefix).
2. Whether team members may edit CRs or only the BA.
3. Whether the "Closed" report section lists all closed CRs or only those closed since the last report.
4. Sync mechanism to the Jira/Confluence-permissioned location (Confluence page, Jira attachment, or other) and who runs it.
5. Which mailbox or folder is monitored, and the approach to Microsoft Graph authentication (organizational approval may be needed).
6. How the report is distributed to stakeholders (manual publish vs. automatic).

## 9. Assumptions

- All CRs originate from emails tagged `[CR]` or are created by the BA.
- Cost is entered manually and is optional.
- The Jira ticket is linked by URL only; no two-way sync with Jira.
- No approval workflow is required in v1.

## 10. Proposed Implementation Phases

1. **Core registry:** CSV storage, CR create/update/list, ID generation, status history.
2. **Reporting:** Weekly Markdown report grouped by sub-project and status group.
3. **Email intake:** Mailbox ingestion for `[CR]` emails producing drafts, and BA review step.
4. **Sync and access:** Publish registry/reports to the Jira/Confluence-permissioned location.

## 11. Acceptance Criteria

- A CR can be created, edited, and moved between any statuses, with history recorded.
- A `[CR]` email produces exactly one draft, which does not appear in reports until confirmed.
- The weekly report shows CRs per sub-project in the four groups and never shows cost.
- IDs are unique and follow the sub-project prefix format.
- Registry and reports are accessible only through the Jira-permissioned location.
````
