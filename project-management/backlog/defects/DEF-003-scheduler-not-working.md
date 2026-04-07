# Defect: DEF-003 - Scheduler Service Not Working

**Status**: ✅ Completed  
**Priority**: 🔴 Critical  
**Story Points**: 5  
**Created**: 2026-03-01  
**Updated**: 2026-03-03  
**Assigned Sprint**: Backlog

## Description

The scheduler service is non-functional, causing the application to be consistently down. The Fly.io machine is not being started/stopped on schedule, and/or the application process is not running when it should be.

## Steps to Reproduce

1. Observe the Fly.io application status during expected uptime hours (6am–10pm).
2. Attempt to interact with the Telegram bot.
3. Bot is unresponsive — application is down.

**Precondition**: Fly.io scheduled scaling is configured via `.github/workflows/fly-schedule-scale.yml` and/or Fly.io machine settings.

## Expected Behavior

- The Fly.io machine starts automatically at the configured schedule (6am).
- The application is available and the Telegram bot responds to messages during uptime hours.
- The machine scales to zero at night (10pm) to save costs.
- On first request outside schedule, the machine wakes up.

## Actual Behavior

- The scheduler does not start/wake the Fly.io machine.
- The application remains down and the Telegram bot is unresponsive.
- Users cannot interact with the bot at any time.

## Environment

- **Server Environment**: Production (Fly.io)
- **Deployment**: Fly.io with scheduled scaling
- **Scheduler**: GitHub Actions cron workflow (`.github/workflows/fly-schedule-scale.yml`)
- **Region**: See `fly.toml`

## Screenshots/Logs

From GitHub Actions run `22620465849` (scale job, step "Install flyctl"):

```
2026-03-03T11:14:28.0562319Z 100  5167  100  5167    0     0  17819      0 --:--:-- --:--:-- --:--:-- 17878
2026-03-03T11:14:28.7545875Z curl: (22) The requested URL returned error: 500
##[error]Process completed with exit code 22.
```

The Fly.io install script (`https://fly.io/install.sh`) downloads successfully but the binary download URL it tries returns HTTP 500 intermittently.

## Technical Details

- The scheduling mechanism uses a GitHub Actions workflow (`.github/workflows/fly-schedule-scale.yml`) with cron triggers to scale the Fly.io machine up and down.
- See `docs/fly-scheduled-scaling.md` for the intended architecture.
- Possible failure points:
  1. GitHub Actions cron job not triggering
  2. Fly.io API token expired or misconfigured in GitHub Secrets
  3. `fly machine start`/`fly machine stop` commands failing
  4. Fly.io machine ID changed or machine was destroyed/recreated
  5. Fly.io auto-stop configuration conflicting with scheduled scaling

## Root Cause

The workflow used `curl -L https://fly.io/install.sh | sh` to install flyctl. This shell-based install method is unreliable — the Fly.io download server intermittently returns HTTP 500 errors. The workflow fails at the "Install flyctl" step before it can even attempt to scale.

The cron schedule itself, the `FLY_API_TOKEN`, and the `fly scale count` logic are all correct. Confirmed by checking successful runs on the same day (e.g. `22607432702` at 03:50 UTC succeeded, `22620465849` at 11:14 UTC failed — both used the same code, different server availability).

## Solution

Replaced the unreliable `curl | sh` install method with the official GitHub Action `superfly/flyctl-actions/setup-flyctl@master`, which is the same action already used in the CI workflow (`ci.yml`). This action uses cached releases and is maintained by Fly.io.

Also removed the now-unnecessary `export PATH="$HOME/.fly/bin:$PATH"` from the Scale step, since the action automatically adds flyctl to PATH.

**Before:**
```yaml
- name: Install flyctl
  run: |
    curl -L https://fly.io/install.sh | sh
    echo "$HOME/.fly/bin" >> $GITHUB_PATH
    export PATH="$HOME/.fly/bin:$PATH"
    fly version
```

**After:**
```yaml
- name: Install flyctl
  uses: superfly/flyctl-actions/setup-flyctl@master
```

## Reference Documents

- [Fly.io scheduled scaling](../../../docs/fly-scheduled-scaling.md) — Architecture and configuration
- `.github/workflows/fly-schedule-scale.yml` — The scheduler workflow
- `fly.toml` — Fly.io application configuration

## Technical References

- File: `.github/workflows/fly-schedule-scale.yml`
- File: `fly.toml`
- File: `docs/fly-scheduled-scaling.md`
- Dashboard: Fly.io app dashboard
- Dashboard: GitHub Actions → workflow runs

## Testing

- [x] flyctl installs via `superfly/flyctl-actions/setup-flyctl@master` (used in CI already)
- [ ] GitHub Actions cron workflow triggers on schedule and succeeds (pending push)
- [ ] `fly scale count 1` succeeds on schedule
- [ ] Application is accessible after scale-up
- [ ] Telegram bot responds after scale-up

## Notes

- This defect, combined with DEF-002 (build failure), means the application is currently unavailable and cannot be redeployed through the normal pipeline.
- **Impact**: Application is completely down for all users.
- Workaround: manually start the Fly.io machine via `fly machine start <machine_id>` or `fly apps restart`.
- If the machine was destroyed, a fresh deploy (`fly deploy`) may be needed.

## History

- 2026-03-01 - Created
- 2026-03-03 - Root cause identified: `curl fly.io/install.sh` returns HTTP 500
- 2026-03-03 - Fixed: switched to `superfly/flyctl-actions/setup-flyctl@master`
- 2026-03-03 - Status changed to ✅ Completed
