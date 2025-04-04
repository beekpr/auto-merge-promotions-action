#!/usr/bin/env python3
import os
import requests
import datetime
import sys

# Environment variables
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]  # This is automatically provided by GitHub Actions
THRESHOLD_DAYS = int(os.environ.get("THRESHOLD_DAYS", "7"))
# Get target branches from environment variable, defaulting to "staging,production"
TARGET_BRANCHES = os.environ.get("TARGET_BRANCHES", "staging,production")
# Create a list of branches by splitting and stripping spaces
TARGET_BRANCHES_LIST = [branch.strip() for branch in TARGET_BRANCHES.split(",") if branch.strip()]
TITLE_PREFIX = os.environ.get("TITLE_PREFIX", "[Promotion]")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def fetch_open_prs():
    prs = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls?state=open&per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        page_prs = response.json()
        if not page_prs:
            break
        prs.extend(page_prs)
        page += 1
    return prs

def check_commit_status(pr):
    head_sha = pr.get("head", {}).get("sha")
    if not head_sha:
        return False
    status_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/commits/{head_sha}/status"
    response = requests.get(status_url, headers=headers)
    response.raise_for_status()
    status_data = response.json()
    return status_data.get("state") == "success"

def merge_pr(pr):
    merge_url = pr["url"] + "/merge"
    response = requests.put(merge_url, headers=headers, json={"merge_method": "merge"})
    if response.status_code == 200:
        print(f"Successfully merged PR #{pr['number']}.")
    else:
        print(f"Failed to merge PR #{pr['number']}: {response.json()}")

def main():
    try:
        prs = fetch_open_prs()
        now = datetime.datetime.utcnow()

        print(f"Checking for PRs to auto-merge. Target branches: {TARGET_BRANCHES_LIST}, Threshold: {THRESHOLD_DAYS} days")
        print(f"Found {len(prs)} open PRs")

        eligible_prs = 0
        for pr in prs:
            title = pr.get("title", "")
            pr_number = pr.get("number", "unknown")

            if not title.startswith(TITLE_PREFIX):
                continue

            # Only consider PRs targeting the configured branches
            base_branch = pr.get("base", {}).get("ref", "")
            if base_branch not in TARGET_BRANCHES_LIST:
                continue

            eligible_prs += 1
            print(f"Processing PR #{pr_number}: {title} → {base_branch}")

            # Check if the PR is older than the threshold
            created_at_str = pr.get("created_at")
            created_at = datetime.datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
            age_days = (now - created_at).days
            if age_days < THRESHOLD_DAYS:
                print(f"PR #{pr_number} is not older than {THRESHOLD_DAYS} days (age: {age_days} days). Skipping.")
                continue

            # Check if all required checks have passed
            if not check_commit_status(pr):
                print(f"PR #{pr_number} does not have all checks passed. Skipping.")
                continue

            # Merge the PR
            print(f"Attempting to merge PR #{pr_number}")
            merge_pr(pr)

        print(f"Processed {eligible_prs} eligible PRs out of {len(prs)} total PRs")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
