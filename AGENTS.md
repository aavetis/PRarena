# Repository-wide instructions

## Onboarding a new agent into PRarena

Follow every step below when we start tracking a new coding agent. Skipping items here is what caused the Jules onboarding fixes—treat this as the single source of truth.

### 1. Gather canonical agent metadata first
- Decide on the agent `key` (lowercase slug with no spaces). This drives CSV column names and template lookups.
- Record the public-facing names:
  - `display`: short label for tables.
  - `long_name`: full name for the leaderboard cards.
- Pick a distinctive color triple (total bar, merged bar, line). Reuse the soft/bright/dark convention already in `generate_chart.py`.
- Collect every GitHub search URL the site surfaces. We need four queries per agent:
  1. **Total PRs** – `is:pr+head:<branch-prefix>/` or `is:pr+author:<bot>`
  2. **Merged PRs** – add `+is:merged`
  3. **Ready PRs** – add `+-is:draft`
  4. **Draft PRs** – add `+is:draft` (used only in the UI, but keep it in metadata)
  Verify each query manually in the browser before codifying it.

### 2. Wire the GitHub collection pipeline (`collect_data.py`)
- Extend the `Q` dictionary with three entries for the new agent (`total`, `merged`, `nondraft`). Match the naming pattern: `<key>_total`, `<key>_merged`, `<key>_nondraft`.
- Update the `row` list and the CSV header block right below it to append the new metrics. Order matters – keep all metrics grouped by agent, and ensure the header labels exactly match the keys from `Q`.
- Sanity-check that every key referenced in `row` is defined in `Q`; the script fails later if you miss one.
- Historical data:
  - Update the first row in both `data.csv` and `data_backup.csv` so the header now contains the three new `<key>_*` columns. If a migration is needed, either backfill realistic values by querying the API per timestamp (patterned after `scripts/add_nondraft_final.py`) or set placeholder zeros with a follow-up backfill plan. Do not leave `Unnamed:` columns in the CSV.
  - If you add a migration helper, include the new agent in any `agents = [...]` or query maps inside `scripts/` (e.g., `scripts/add_nondraft_final.py`).

### 3. Extend the analytics & templating engine (`generate_chart.py`)
- Add a full entry for the agent inside the global `AGENTS` list (key, labels, colors, and all four query URLs). This single list feeds the README template, GitHub Pages template, and chart toggles.
- Touch every hard-coded per-agent section:
  - Percentage calculations: duplicate the existing lambda blocks for `df["<key>_percentage"]` and `df["<key>_total_percentage"]`.
  - Matplotlib bars and lines: create the paired `bars_<key>_total`, `bars_<key>_merged`, and the line trace for success rate, including color and label strings.
  - Success-rate annotations: extend the annotation block so the new agent prints values (color, offsets, formatting).
  - JSON export: add the color triple to the `colors` dictionary and include the new key in every `for agent in [...]` list. (Search for `for agent in ["copilot", "codex", "cursor", "devin", "codegen", "jules"]` and append your new key everywhere.)
- Confirm `build_stats` and downstream calculations automatically pick up the new columns because they iterate over `AGENTS`.

### 4. Update front-end logic that relies on explicit agent lists
- In `templates/index_template.html`, expand the regex used to match agent labels (`labelLower.match(/(...)/)`) to include the new key. This avoids missing toggle behavior.
- No manual edits are required in `docs/index.html`; running the generator will rebuild it from the template.

### 5. Regenerate derived assets (automated outputs)
- Run `python collect_data.py` once to verify API connectivity and append a fresh data row that includes the new columns. This also updates `docs/index.html` timestamps.
- Run `python generate_chart.py` to:
  - Recompute the chart image (`docs/chart.png`).
  - Emit `docs/chart-data.json` with the expanded datasets.
  - Re-render `README.md` and `docs/index.html` from their templates. Never hand-edit those generated files.
- Open the rendered README and `docs/index.html` to visually confirm the new agent appears everywhere (leaderboard card, chart toggles, data sources, stats table).

### 6. Final validation
- Load `data.csv` with pandas (`python - <<'PY' ...`) to ensure no `Unnamed` columns remain and the new `<key>_*` headers exist.
- Skim the git diff for only intentional changes (especially large CSV diffs). Make sure both `data.csv` and `data_backup.csv` stay in sync.
- Commit once everything builds, then create the PR via the automation tool.

Stick to this checklist whenever onboarding an agent; deviating caused the regressions we had with Jules.
