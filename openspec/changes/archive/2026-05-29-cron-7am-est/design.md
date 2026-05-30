## Context

The daily build cron runs at 13:00 UTC (8am EST). The sole change is shifting it one hour earlier to 12:00 UTC (7am EST).

## Goals / Non-Goals

**Goals:**
- Update the cron expression in `daily_build.yml` from `0 13 * * *` to `0 12 * * *`

**Non-Goals:**
- Changing any other workflow behavior
- Timezone-aware scheduling (UTC is the canonical reference)

## Decisions

Single-line change to the cron expression. No alternatives considered — this is a direct value update.

## Risks / Trade-offs

- GitHub Actions cron schedules are best-effort and may fire late during high-load periods — no mitigation needed, behavior is unchanged.
