# Project Tasks

## Phase 1: Setup and Planning
- [x] Create project repository
- [x] Brainstorm automation ideas (PROJECT_IDEAS.md)
- [x] Write CR Registry technical specification (project_spec.md)
- [x] Create weekly status report template (work/weekly-status-report.md)
- [x] Complete Module 03 calculator exercise with .gitignore and two commits
- [x] Write Module 03 and Module 08 completion reports
- [ ] Resolve open questions in the spec (sub-project names/ID prefixes, edit rights, "Closed" section scope)
- [ ] Set up development environment

## Phase 2: Core Registry
- [ ] Define CR data model and enums (statuses, priority, sub-project)
- [ ] Implement CSV storage (registry.csv, drafts.csv, history.csv)
- [ ] Implement CR create, view, update, and list with filters
- [ ] Implement ID generation per sub-project prefix
- [ ] Implement status transitions (forward, backward, On Hold, Rejected) with history log

## Phase 3: Reporting
- [ ] Build weekly report template (Markdown tables per sub-project)
- [ ] Group CRs into Open, In Progress, On Hold, Closed
- [ ] Exclude cost and drafts from reports
- [ ] Add report file output (reports/cr-report-YYYY-MM-DD.md)

## Phase 4: Email Intake
- [ ] Decide mailbox and Microsoft Graph authentication approach
- [ ] Implement `[CR]` email ingestion producing drafts
- [ ] Deduplicate by message ID
- [ ] Implement BA review and confirm step

## Phase 5: Sync, Access, and Release
- [ ] Decide sync mechanism to the Jira/Confluence-permissioned location
- [ ] Publish registry and reports to that location
- [ ] Verify acceptance criteria from the spec
- [ ] Document usage in a README

## Progress Notes
_AI updates this section as work progresses_
