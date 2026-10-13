# CR Registry – Implementation Backlog

Source: [project_spec.md](project_spec.md). Language: Python (CLI scripts). v1 MVP: registry CRUD + status history, weekly report. Email intake and Jira/Confluence sync are post-MVP, built in spec order. Decisions are tracked as blocking tasks in the relevant phase.

## Phase 1: Setup

### Decisions (blocking)
- [ ] D-1: Confirm sub-project names and ID prefixes (spec Q1); until then use `CW-` as the placeholder. *(FR-7)*
- [ ] D-2: Confirm whether team members can edit CRs or only the BA (spec Q2). *(Section 3)*
- [ ] D-3: Confirm "Closed" section semantics: all closed vs. closed since last report (spec Q3). *(FR-10)*

### Project scaffolding
- [ ] Create `cr-registry/` layout: `registry.csv`, `drafts.csv`, `history.csv`, `reports/`. *(5.3)*
- [ ] Create Python package structure (`cr_registry/`, `tests/`) and `requirements.txt` (stdlib-first; avoid a database). *(NFR-5, NFR-6)*
- [ ] Add `.gitignore` for local copies of data, secrets, and `.env` files. *(NFR-1, NFR-4)*
- [ ] Add config file for sub-projects and ID prefixes (not hard-coded). *(FR-7)*
- [ ] Define enums: `Status`, `Priority`, `ReportGroup`; add the status → report group mapping. *(5.1)*
- [ ] Define the `CR` data model with all fields from 5.2 and required-field validation. *(5.2)*
- [ ] Create CSV headers/schema for `registry.csv`, `drafts.csv`, `history.csv`.
- [ ] Create a CLI entry point with subcommands skeleton (`create`, `list`, `show`, `update`, `status`, `report`).

## Phase 2: Core Features

### Storage layer
- [ ] Implement CSV read/write for registry and drafts (UTF-8, stable column order, diff-friendly). *(NFR-6)*
- [ ] Handle list fields (`affected_systems`, `document_links`) serialization in CSV.
- [ ] Implement atomic writes to avoid corrupting CSV files.

### CR management
- [ ] Implement auto-generated IDs per sub-project prefix (`<PREFIX>-<NNN>`), unique and zero-padded. *(FR-7)*
- [ ] Implement `create` command (manual CR by BA) with required-field validation. *(FR-5, FR-6)*
- [ ] Set `created_date`, `updated_date`, and `is_draft` automatically.
- [ ] Implement `show` command for a single CR.
- [ ] Implement `update` command for editable fields; refresh `updated_date`. *(FR-6)*
- [x] Implement `list` command with filters: sub-project, status, priority, owner. *(FR-6)*
- [ ] Validate `jira_url` and `document_links` as URLs.

### Status lifecycle and history
- [ ] Implement `status` command allowing forward and backward transitions. *(FR-9)*
- [ ] Allow any status to move to `On Hold` or `Rejected`. *(FR-9)*
- [ ] Append each change to `history.csv` (timestamp, CR id, old status, new status, changed by). *(FR-8, NFR-3)*
- [ ] Implement `history` command to view a CR's status log.
- [ ] Reject unknown statuses and no-op transitions.

### Draft handling (manual path)
- [ ] Implement draft creation and `confirm` command that moves a draft to the registry and assigns an ID. *(FR-3, FR-5)*
- [ ] Ensure drafts are excluded from `list` by default and from all reports. *(FR-3, FR-11)*

### Reporting
- [ ] Implement grouping by sub-project, then by report group (Open, In Progress, On Hold, Closed). *(FR-10, 5.1)*
- [ ] Render Markdown tables per spec columns: ID, Title, Status (In Progress only), Priority, Owner, Effort (h), Jira link. *(Section 6)*
- [ ] Implement Closed section per decision D-3 (using the last report date if "since last report"). *(FR-10)*
- [ ] Exclude `cost` and drafts from reports and exports. *(FR-11, NFR-2)*
- [ ] Handle empty groups and sub-projects cleanly.
- [ ] Write the report to `reports/cr-report-YYYY-MM-DD.md`; implement `report` command.
- [ ] Track the last report date for "since last report" logic.

## Phase 3: Integration

### Decisions (blocking)
- [ ] D-4: Choose the mailbox/folder to monitor and the Microsoft Graph auth approach; start the organizational approval (spec Q5). *(FR-1, NFR-4)*
- [ ] D-5: Choose the sync mechanism (Confluence page, Jira attachment, other) and who runs it (spec Q4). *(NFR-1)*
- [ ] D-6: Decide how the report is distributed to stakeholders (spec Q6).

### Email intake (mock first)
- [ ] Define an `EmailSource` interface (list messages with id, subject, body, sender, received date).
- [ ] Implement a mock/sample email source (JSON or `.eml` fixtures) for development and testing.
- [ ] Filter messages whose subject contains `[CR]`. *(FR-1)*
- [ ] Map email to draft: title ← subject (strip `[CR]`), description ← body, requester ← sender, received date. *(FR-2)*
- [ ] Deduplicate by message ID; store `source_email_id` on the CR. *(FR-4)*
- [ ] Implement `ingest` command writing to `drafts.csv`.
- [ ] Implement `drafts` review commands: list, edit, confirm, discard. *(FR-3)*
- [ ] Implement the Microsoft Graph source with read-only permissions; load credentials from environment/secure store only. *(FR-1, NFR-4)*
- [ ] Handle Graph errors, throttling, and token expiry.

### Sync and access
- [ ] Implement the publish step to the permissioned location per D-5. *(NFR-1)*
- [ ] Ensure `cost` is never included in published files or exports. *(NFR-2)*
- [ ] Document the manual/automated process for who syncs and when.
- [ ] Add a safeguard against writing the registry or reports to non-permissioned locations.

## Phase 4: Testing

### Unit tests
- [ ] ID generation: uniqueness, per-prefix sequencing, padding. *(FR-7)*
- [ ] Model validation: required fields, enums, URL fields. *(5.2)*
- [ ] Status transitions: forward, backward, to On Hold/Rejected. *(FR-9)*
- [ ] History logging fields and append behavior. *(FR-8, NFR-3)*
- [ ] Status → report group mapping. *(5.1)*
- [ ] CSV round-trip including list fields and special characters.
- [ ] List filters (sub-project, status, priority, owner). *(FR-6)*

### Report tests
- [ ] Report grouping per sub-project and the four groups. *(FR-10)*
- [ ] Cost never appears in the report output. *(FR-11, NFR-2)*
- [ ] Drafts are excluded from the report. *(FR-11)*
- [ ] Closed section behavior per D-3.
- [ ] Empty data and empty-group edge cases.

### Intake tests
- [ ] A `[CR]` email produces exactly one draft; re-running ingestion creates no duplicate. *(FR-2, FR-4)*
- [ ] Emails without `[CR]` are ignored. *(FR-1)*
- [ ] Draft stays out of reports until confirmed. *(FR-3)*
- [ ] Graph source tested with mocked HTTP responses (no real credentials).

### Acceptance and sample data
- [ ] Create sample dataset (~20 CRs across several sub-projects, all statuses).
- [ ] Walk through each acceptance criterion in `project_spec.md` Section 11 against the sample data.
- [ ] Verify no secrets or real cost data are committed. *(NFR-1, NFR-4)*

## Phase 5: Documentation

- [ ] README: purpose, setup, and quick start.
- [ ] CLI command reference with examples (create, list, update, status, history, report, ingest, drafts).
- [ ] Data dictionary for CR fields and CSV file formats. *(5.2, 5.3)*
- [ ] Status lifecycle diagram and report group mapping. *(5.1)*
- [ ] BA runbook: weekly report routine, draft review, and sync/publish steps.
- [ ] Mailbox/Graph setup guide: permissions, credentials handling, approval status. *(NFR-4)*
- [ ] Access and confidentiality guidance: local copy handling and cost data rules. *(NFR-1, NFR-2)*
- [ ] Record resolved decisions (D-1 to D-6) and update the spec's open questions.

## Phase Acceptance Criteria

| Phase | Done when |
|---|---|
| Setup | Decisions D-1 to D-3 are recorded, the layout and models exist, and the CLI skeleton runs. |
| Core Features | A CR can be created, edited, and moved between any statuses with history recorded; IDs are unique and follow the prefix format; the weekly report shows CRs per sub-project in four groups and never shows cost. |
| Integration | A `[CR]` email produces exactly one draft that stays out of reports until confirmed; registry and reports are published only to the permissioned location. |
| Testing | All unit, report, and intake tests pass; every Section 11 acceptance criterion is verified on sample data. |
| Documentation | A new BA can set up, run the weekly report, and review drafts using only the docs. |
