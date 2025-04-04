# Auto Promote

A GitHub Action that automatically merges PRs with a configurable title prefix after a specified time period.

## Features

- Automatically merges PRs after a configurable waiting period
- Targets specific branches for auto-promotion
- Only merges PRs with a specific title prefix
- Ensures all required checks have passed before merging

## Setup

Add this action to your repository by creating a workflow file (e.g., `.github/workflows/auto-promote.yml`):

```yaml
name: Auto Promote PRs

on:
  schedule:
    - cron: '0 */6 * * *'  # Runs every 6 hours
  workflow_dispatch:  # Allows manual triggering

jobs:
  auto-promote:
    runs-on: ubuntu-latest
    steps:
      - name: Auto Merge Promotion PRs
        uses: your-org/auto-promote@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

## Configuration

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `github-token` | GitHub token for API access | Yes | N/A |
| `threshold-days` | Number of days before PRs are auto-merged | No | `7` |
| `target-branches` | Comma-separated list of branches to target for auto-merge | No | `staging,production` |
| `title-prefix` | The prefix to look for in PR titles | No | `[Promotion]` |

## Example with Custom Configuration

```yaml
name: Auto Merge Promotion PRs

on:
  schedule:
    # Runs at 9:00 UTC (10:00 CET) on Monday-Friday
    - cron: '0 9 * * 1-5'
  workflow_dispatch: # Allow manual triggering

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - name: Auto Merge Promotion PRs
        uses: beekpr/auto-merge-promotions-action@master
        with:
          github-token: ${{ secrets.BKPR_GC_GH_ACTIONS_TOKEN }}
          threshold-days: '7'
          target-branches: 'staging,production'
          title-prefix: '[AutoPromote]'
```

## How It Works

1. The action scans all open PRs in your repository
2. It filters PRs that:
    - Start with the configured title prefix
    - Target one of the specified branches
    - Have been open for longer than the threshold days
    - Have all required checks passing
3. Eligible PRs are automatically merged

## Creating Promotable PRs

To create a PR that will be auto-promoted:

1. Create a PR targeting one of the branches in `target-branches`
2. Add the prefix (e.g., `[Promotion]`) to the PR title
3. Wait for the configured threshold period
4. Ensure all checks are passing

The PR will be automatically merged once all conditions are met.