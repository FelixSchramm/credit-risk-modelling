# Handover archive

Snapshots of `HANDOVER.md`, written after every merged issue PR, at every
90%-budget handover, and at relay completion
(see CLAUDE.md, section "Handover archive").

- File name: `YYYY-MM-DD_HHMM.md` (UTC timestamp of the snapshot).
- Content: the current `HANDOVER.md`, prefixed with one line naming the
  timestamp and the reason ("issue #N merged", "90% budget reached",
  "all issues done").
- Snapshots are append-only history: never edit or delete old snapshots.

The current working state always lives in `/HANDOVER.md` at the repo root;
this folder is the read-only history of past handovers.
