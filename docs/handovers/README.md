# Handover archive

One snapshot per autonomous session, written at handover time
(see CLAUDE.md, section "Autonomous session protocol", step 5a).

- File name: `YYYY-MM-DD_HHMM.md` (UTC timestamp of the handover).
- Content: the session's finalized `HANDOVER.md`, prefixed with one line
  naming the timestamp and the reason the session ended.
- Snapshots are append-only history: never edit or delete old snapshots.

The current working state always lives in `/HANDOVER.md` at the repo root;
this folder is the read-only history of past handovers.
