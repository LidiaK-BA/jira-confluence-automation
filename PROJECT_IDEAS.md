# Project Ideas: Jira/Confluence Automation for Managers

## 1. Weekly Team Status Digest

**Problem it solves:** Managers spend time every week manually collecting what shipped, what is in progress, and what is blocked across several Jira boards, then writing it up for stakeholders.

**What it does:** Generates a summarized status report each week and publishes it as a Confluence page (or sends it by email/Slack).

**Data it needs:**
- Jira issues updated in the last 7 days (key, summary, status, assignee, priority, labels)
- Status transitions and their timestamps (to identify completed and newly blocked work)
- Sprint/epic membership and linked issues (to group work by goal)
- Confluence space and parent page ID for publishing

## 2. Stale and At-Risk Work Detector

**Problem it solves:** Tickets silently stall, such as unassigned issues, items stuck in review, or overdue tasks. Managers find out too late, usually in a standup or after a deadline slips.

**What it does:** Runs daily, flags at-risk issues, and sends the manager a prioritized list. It can optionally comment on the ticket to nudge the assignee.

**Data it needs:**
- Issue status, time in current status (from the changelog), and last update date
- Assignee, reporter, due date, and priority
- Sprint end dates and remaining work
- Configurable thresholds (for example, "in review > 3 days" or "no update > 5 days")
- Notification target (Slack webhook or email)

## 3. Meeting Notes to Jira Action Items

**Problem it solves:** Action items from meetings are written in Confluence notes and then forgotten or manually re-entered as Jira tickets, so follow-through is inconsistent.

**What it does:** Scans designated Confluence meeting-notes pages for action items (for example, checkbox tasks with an @mention and date), creates matching Jira issues, and links them back to the page.

**Data it needs:**
- Confluence page content for meeting notes (via a specific space, label, or parent page)
- Action item markup: task text, mentioned user, and due date
- Mapping from Confluence users to Jira accounts
- Target Jira project, issue type, and default labels/components
- A record of already-processed items to avoid duplicate tickets
