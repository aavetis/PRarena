### PR Analytics: Volume vs Success Rate (auto-updated)

View the [interactive dashboard](https://prarena.ai) for these statistics.

## Understanding the Metrics

Different AI coding agents follow different workflows when creating pull requests:

- **All PRs**: Every pull request created by an agent, including DRAFT PRs
- **Ready PRs**: Non-draft pull requests that are ready for review and merging
- **Merged PRs**: Pull requests that were successfully merged into the codebase

**Key workflow differences**: Some agents like **Codex** iterate privately and create ready PRs directly, resulting in very few drafts but high merge rates. Others like **Copilot** and **Codegen** create draft PRs first, encouraging public iteration before marking them ready for review.

The statistics below focus on **Ready PRs only** to fairly compare agents across different workflows, measuring each agent's ability to produce mergeable code regardless of whether they iterate publicly (with drafts) or privately.

## Data sources

Explore the GitHub search queries used:



- **All Copilot PRs**: [https://github.com/search?q=is:pr+head:copilot/&type=pullrequests](https://github.com/search?q=is:pr+head:copilot/&type=pullrequests)
- **Merged Copilot PRs**: [https://github.com/search?q=is:pr+head:copilot/+is:merged&type=pullrequests](https://github.com/search?q=is:pr+head:copilot/+is:merged&type=pullrequests)
  

- **All Codex PRs**: [https://github.com/search?q=is:pr+head:codex/&type=pullrequests](https://github.com/search?q=is:pr+head:codex/&type=pullrequests)
- **Merged Codex PRs**: [https://github.com/search?q=is:pr+head:codex/+is:merged&type=pullrequests](https://github.com/search?q=is:pr+head:codex/+is:merged&type=pullrequests)
  

- **All Cursor PRs**: [https://github.com/search?q=is:pr+head:cursor/&type=pullrequests](https://github.com/search?q=is:pr+head:cursor/&type=pullrequests)
- **Merged Cursor PRs**: [https://github.com/search?q=is:pr+head:cursor/+is:merged&type=pullrequests](https://github.com/search?q=is:pr+head:cursor/+is:merged&type=pullrequests)
  

- **All Devin PRs**: [https://github.com/search?q=is:pr+author:devin-ai-integration[bot]&type=pullrequests](https://github.com/search?q=is:pr+author:devin-ai-integration[bot]&type=pullrequests)
- **Merged Devin PRs**: [https://github.com/search?q=is:pr+author:devin-ai-integration[bot]+is:merged&type=pullrequests](https://github.com/search?q=is:pr+author:devin-ai-integration[bot]+is:merged&type=pullrequests)
  

- **All Codegen PRs**: [https://github.com/search?q=is:pr+author:codegen-sh[bot]&type=pullrequests](https://github.com/search?q=is:pr+author:codegen-sh[bot]&type=pullrequests)
- **Merged Codegen PRs**: [https://github.com/search?q=is:pr+author:codegen-sh[bot]+is:merged&type=pullrequests](https://github.com/search?q=is:pr+author:codegen-sh[bot]+is:merged&type=pullrequests)
  

- **All Jules PRs**: [https://github.com/search?q=is:pr+author:google-labs-jules[bot]&type=pullrequests](https://github.com/search?q=is:pr+author:google-labs-jules[bot]&type=pullrequests)
- **Merged Jules PRs**: [https://github.com/search?q=is:pr+author:google-labs-jules[bot]+is:merged&type=pullrequests](https://github.com/search?q=is:pr+author:google-labs-jules[bot]+is:merged&type=pullrequests)
  

---

![chart](docs/chart.png)

## Current Statistics

| Project | Ready PRs | Merged PRs | Success Rate |
| ------- | --------- | ---------- | ------------ |
| Copilot | 1,104,766 | 1,056,695 | 95.65% |
| Codex | 3,722,355 | 3,235,749 | 86.93% |
| Cursor | 187,038 | 179,706 | 96.08% |
| Devin | 74,886 | 45,880 | 61.27% |
| Codegen | 6,922 | 4,428 | 63.97% |
| Jules | 203,310 | 189,562 | 93.24% |