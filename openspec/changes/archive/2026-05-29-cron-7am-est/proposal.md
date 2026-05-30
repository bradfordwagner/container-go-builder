## Why

The daily build cron currently fires at 8am EST (13:00 UTC). Moving it to 7am EST (12:00 UTC) aligns the build with earlier start-of-day availability, so fresh images are ready before the workday begins.

## What Changes

- Update the cron schedule in `.github/workflows/daily_build.yml` from `0 13 * * *` to `0 12 * * *`

## Capabilities

### New Capabilities

### Modified Capabilities

- `daily-cron`: Cron trigger time changes from 13:00 UTC (8am EST) to 12:00 UTC (7am EST)

## Impact

- `.github/workflows/daily_build.yml` — cron expression updated
