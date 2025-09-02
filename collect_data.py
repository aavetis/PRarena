import csv
import datetime as dt
import os
import re
from pathlib import Path
import requests
import time


# Delay between API requests to respect rate limits
API_DELAY_SECONDS = float(os.getenv("API_DELAY_SECONDS", 6))


# GitHub API headers with optional authentication
def get_headers():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "PR-Watcher"}

    # Add authentication if token is available
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"
        print("Using authenticated GitHub API requests")
    else:
        print("Using unauthenticated GitHub API requests (rate limited)")

    return headers


# Search queries - tracking all PR metrics
# Organized by agent: total, merged, non-draft for each
Q = {
    # Copilot metrics
    "is:pr+head:copilot/": "copilot_total",
    "is:pr+head:copilot/+is:merged": "copilot_merged",
    "is:pr+head:copilot/+-is:draft": "copilot_nondraft",
    # Codex metrics
    "is:pr+head:codex/": "codex_total",
    "is:pr+head:codex/+is:merged": "codex_merged",
    "is:pr+head:codex/+-is:draft": "codex_nondraft",
    # Cursor metrics
    "is:pr+head:cursor/": "cursor_total",
    "is:pr+head:cursor/+is:merged": "cursor_merged",
    "is:pr+head:cursor/+-is:draft": "cursor_nondraft",
    # Devin metrics - using head:devin pattern only
    "is:pr+head:devin": "devin_head_total",
    "is:pr+head:devin+is:merged": "devin_head_merged",
    "is:pr+head:devin+-is:draft": "devin_head_nondraft",
    "is:pr+head:devin/": "devin_head_slash_total", 
    "is:pr+head:devin/+is:merged": "devin_head_slash_merged",
    "is:pr+head:devin/+-is:draft": "devin_head_slash_nondraft",
    # Codegen metrics
    "is:pr+author:codegen-sh[bot]": "codegen_total",
    "is:pr+author:codegen-sh[bot]+is:merged": "codegen_merged",
    "is:pr+author:codegen-sh[bot]+-is:draft": "codegen_nondraft",
}


def collect_data():
    # Get data from GitHub API - 15 metrics total (3 per agent: total, merged, non-draft)
    cnt = {}

    # Get headers with authentication if available
    headers = get_headers()

    # Collect all metrics in one loop
    for query, key in Q.items():
        print(f"Collecting {key}...")
        
        # Simple retry logic - 3 attempts with pause
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                r = requests.get(
                    f"https://api.github.com/search/issues?q={query}",
                    headers=headers,
                    timeout=30,
                )

                # If rate limited, wait until reset and retry
                if (
                    r.status_code == 403
                    and r.headers.get("X-RateLimit-Remaining") == "0"
                ):
                    reset = int(r.headers.get("X-RateLimit-Reset", 0))
                    wait_for = max(reset - time.time(), 0) + 1
                    print(
                        f"    Rate limit exceeded, sleeping for {int(wait_for)}s before retry"
                    )
                    time.sleep(wait_for)
                    continue

                r.raise_for_status()
                cnt[key] = r.json()["total_count"]
                print(f"  {key}: {cnt[key]}")
                break

            except Exception as e:
                if attempt == max_attempts - 1:  # Last attempt - fail the job
                    raise e
                else:
                    print(
                        f"    Attempt {attempt + 1} failed ({e}), retrying in 10s..."
                    )
                    time.sleep(10)  # Wait 10 seconds before retry

        # Rate limiting: wait between API calls
        time.sleep(API_DELAY_SECONDS)

    cnt["devin_total"] = max(cnt["devin_head_total"], cnt["devin_head_slash_total"])
    cnt["devin_merged"] = max(cnt["devin_head_merged"], cnt["devin_head_slash_merged"])
    cnt["devin_nondraft"] = max(cnt["devin_head_nondraft"], cnt["devin_head_slash_nondraft"])
    
    print(f"Combined Devin counts:")
    print(f"  devin_total: {cnt['devin_total']} (head:devin: {cnt['devin_head_total']}, head:devin/: {cnt['devin_head_slash_total']})")
    print(f"  devin_merged: {cnt['devin_merged']} (head:devin: {cnt['devin_head_merged']}, head:devin/: {cnt['devin_head_slash_merged']})")
    print(f"  devin_nondraft: {cnt['devin_nondraft']} (head:devin: {cnt['devin_head_nondraft']}, head:devin/: {cnt['devin_head_slash_nondraft']})")

    # Save data to CSV
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y‑%m‑%d %H:%M:%S")
    row = [
        timestamp,
        cnt["copilot_total"],
        cnt["copilot_merged"],
        cnt["codex_total"],
        cnt["codex_merged"],
        cnt["cursor_total"],
        cnt["cursor_merged"],
        cnt["devin_total"],
        cnt["devin_merged"],
        cnt["codegen_total"],
        cnt["codegen_merged"],
        cnt["copilot_nondraft"],
        cnt["codex_nondraft"],
        cnt["cursor_nondraft"],
        cnt["devin_nondraft"],
        cnt["codegen_nondraft"],
    ]

    csv_file = Path("data.csv")
    is_new_file = not csv_file.exists()
    with csv_file.open("a", newline="") as f:
        writer = csv.writer(f)
        if is_new_file:
            writer.writerow(
                [
                    "timestamp",
                    "copilot_total",
                    "copilot_merged",
                    "codex_total",
                    "codex_merged",
                    "cursor_total",
                    "cursor_merged",
                    "devin_total",
                    "devin_merged",
                    "codegen_total",
                    "codegen_merged",
                    "copilot_nondraft",
                    "codex_nondraft",
                    "cursor_nondraft",
                    "devin_nondraft",
                    "codegen_nondraft",
                ]
            )
        writer.writerow(row)

    return csv_file


def update_html_with_latest_data():
    """Update the HTML file with the latest statistics from the chart data."""
    # The HTML will be updated by JavaScript automatically when chart-data.json loads
    # This is a placeholder for any additional HTML updates needed
    html_file = Path("docs/index.html")
    if not html_file.exists():
        print("HTML file not found, skipping HTML update")
        return

    # Update the last updated timestamp in the HTML
    html_content = html_file.read_text()

    # Get current timestamp in the format used in the HTML
    now = dt.datetime.now(dt.UTC)
    timestamp_str = now.strftime("%B %d, %Y %H:%M UTC")

    # Update the timestamp in the HTML
    updated_html = re.sub(
        r'<span id="last-updated">[^<]*</span>',
        f'<span id="last-updated">{timestamp_str}</span>',
        html_content,
    )

    html_file.write_text(updated_html)
    print(f"Updated HTML timestamp to: {timestamp_str}")


if __name__ == "__main__":
    collect_data()
    update_html_with_latest_data()
    print("Data collection complete. To generate chart, run generate_chart.py")
