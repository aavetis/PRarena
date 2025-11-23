#!/usr/bin/env python3
"""
ONE-TIME SCRIPT: Add non-draft PR data to existing data.csv
Used to retroactively add nondraft columns to historical data by querying GitHub API.
This script strategically samples data points and handles GitHub API limitations properly.
Completed: Added non-draft tracking for all agents in the dataset.
"""

import csv
import datetime as dt
import time
import os
from pathlib import Path
import requests
from typing import Dict

# GitHub API headers - include PAT if available
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "PR-Watcher"}
if github_token := os.getenv("GITHUB_TOKEN"):
    HEADERS["Authorization"] = f"token {github_token}"
    print("✅ Using GitHub PAT for authentication")
else:
    print("⚠️  No GitHub PAT found, using unauthenticated requests")

# Non-draft queries (excluding drafts with -is:draft)
NONDRAFT_QUERIES = {
    "is:pr+head:copilot/+-is:draft": "copilot_nondraft",
    "is:pr+head:codex/+-is:draft": "codex_nondraft",
    "is:pr+head:cursor/+-is:draft": "cursor_nondraft",
    "is:pr+author:devin-ai-integration[bot]+-is:draft": "devin_nondraft",
    "is:pr+author:codegen-sh[bot]+-is:draft": "codegen_nondraft",
    "is:pr+author:google-labs-jules[bot]+-is:draft": "jules_nondraft",
}


def parse_timestamp(timestamp_str: str) -> dt.datetime:
    """Parse CSV timestamp to datetime object."""
    return dt.datetime.strptime(timestamp_str.replace("‑", "-"), "%Y-%m-%d %H:%M:%S")


def format_github_date(timestamp: dt.datetime) -> str:
    """Format datetime for GitHub API (ISO format with UTC)."""
    return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_single_query():
    """Test a single query to verify our approach works."""
    print("Testing single query...")
    test_query = "is:pr+head:copilot/+-is:draft"

    try:
        r = requests.get(
            f"https://api.github.com/search/issues?q={test_query}",
            headers=HEADERS,
            timeout=30,
        )
        r.raise_for_status()
        total = r.json()["total_count"]
        print(f"✓ Test query successful: {test_query} -> {total} results")
        return True
    except Exception as e:
        print(f"✗ Test query failed: {e}")
        return False


def get_nondraft_counts_at_time(timestamp: dt.datetime) -> Dict[str, int]:
    """Get non-draft PR counts at a specific timestamp with proper error handling."""
    counts = {}
    created_before = format_github_date(timestamp)

    print(f"Querying for timestamp: {timestamp} (GitHub format: {created_before})")

    for query_base, key in NONDRAFT_QUERIES.items():
        # Add time filter - PRs created before this timestamp
        full_query = f"{query_base}+created:<{created_before}"

        print(f"  {key}: {full_query}")

        for attempt in range(3):  # Max 3 attempts
            try:
                r = requests.get(
                    f"https://api.github.com/search/issues?q={full_query}",
                    headers=HEADERS,
                    timeout=30,
                )

                if r.status_code == 403:
                    wait_time = 10 * (2**attempt)  # 10s, 20s, 40s
                    print(f"    Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                elif r.status_code == 422:
                    print(f"    Query syntax error for {key}, skipping")
                    counts[key] = 0
                    break

                r.raise_for_status()
                count = r.json()["total_count"]
                counts[key] = count
                print(f"    ✓ {key}: {count}")
                break

            except Exception as e:
                if attempt == 2:  # Last attempt
                    print(f"    ✗ Failed {key}: {e}")
                    counts[key] = 0
                else:
                    print(f"    Retry {attempt + 1} for {key}")

        # No rate limiting needed with PAT (5000 requests/hour)
        time.sleep(0.1)  # Just a tiny delay to be safe

    return counts


def enforce_constraints(row: dict) -> dict:
    """Enforce logical constraints: merged <= nondraft <= total for each agent."""
    agents = ["copilot", "codex", "cursor", "devin", "codegen", "jules"]

    for agent in agents:
        total_key = f"{agent}_total"
        merged_key = f"{agent}_merged"
        nondraft_key = f"{agent}_nondraft"

        if all(key in row for key in [total_key, merged_key, nondraft_key]):
            total = int(row[total_key])
            merged = int(row[merged_key])
            nondraft = int(row[nondraft_key])

            # Enforce constraints: merged <= nondraft <= total
            # Start from the bottom and work up
            nondraft = max(
                merged, min(nondraft, total)
            )  # nondraft between merged and total

            row[nondraft_key] = nondraft

    return row


def main():
    """Main function to process data with strategic sampling."""
    input_file = Path("data.csv")
    backup_file = Path("data_backup.csv")

    if not input_file.exists():
        print("❌ Error: data.csv not found!")
        return

    # Test API first
    if not test_single_query():
        print("❌ API test failed. Check your connection and try again.")
        return

    # Create backup of original data
    print(f"📋 Creating backup: {backup_file}")
    import shutil

    shutil.copy2(input_file, backup_file)
    print(f"✅ Backup created")

    print(f"📖 Reading {input_file}")

    # Read all data
    with input_file.open("r", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    total_rows = len(rows)
    print(f"📊 Found {total_rows} rows")

    # New fieldnames with non-draft columns (only add if not already present)
    nondraft_columns = list(NONDRAFT_QUERIES.values())
    missing_columns = [col for col in nondraft_columns if col not in fieldnames]
    new_fieldnames = fieldnames + missing_columns

    if missing_columns:
        print(f"📋 Adding columns: {missing_columns}")
    else:
        print("📋 All nondraft columns already present")

    print(f"🎯 Getting exact data for all {total_rows} timestamps")
    print("📡 This will query GitHub API for each timestamp - may take a while")

    # Process all rows with exact data - write to temp file first
    temp_file = input_file.with_suffix(".tmp")
    with temp_file.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()

        for idx in range(total_rows):
            row = rows[idx].copy()
            timestamp = parse_timestamp(row["timestamp"])

            print(f"\n📡 Row {idx+1}/{total_rows}: {row['timestamp']}")

            try:
                counts = get_nondraft_counts_at_time(timestamp)
                row.update(counts)

                # Enforce constraints to ensure data integrity
                row = enforce_constraints(row)

                print(f"✅ Data retrieved and validated")
            except Exception as e:
                print(f"❌ Failed: {e}")
                # Use zeros for failed queries
                for key in NONDRAFT_QUERIES.values():
                    row[key] = 0

            writer.writerow(row)

            # No rate limiting needed between rows with PAT
            if idx < total_rows - 1:
                print("⏱️  Brief pause...")
                time.sleep(0.2)

    # Replace original file with temp file
    temp_file.replace(input_file)

    print(f"\n✅ Complete! Updated {input_file} with exact non-draft data")
    print(f"📈 Queried {total_rows} exact timestamps")
    print(f"💾 Original data backed up to {backup_file}")

    # Show sample of results
    print(f"\n📋 Sample results:")
    with input_file.open("r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i < 3:  # Show first 3 rows
                print(
                    f"  Row {i+1}: copilot_nondraft={row['copilot_nondraft']}, codex_nondraft={row['codex_nondraft']}"
                )


if __name__ == "__main__":
    print("🚀 Adding non-draft PR data to data.csv")
    print("This will query GitHub API for exact data at each timestamp.")

    response = input("\nContinue? (y/N): ")
    if response.lower() == "y":
        main()
    else:
        print("Cancelled.")
