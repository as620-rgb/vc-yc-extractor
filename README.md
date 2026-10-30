# YC Directory Extractor

A `nanoagent.plugin/v0001` plugin, built on the structure of NanoAgent's reference plugin,
[arxiv-source](https://github.com/zeyuyang8/arxiv-source). The agent reads company cards from a saved
snapshot of the YC Startup Directory page (40 companies, bundled in `src/plugin/data/yc_directory.html`)
and extracts the companies that match a filter as structured records. Everything runs offline, so every
run reads the same data.

## Tools

| Tool | Does | Code |
|---|---|---|
| `read_directory` | Reads up to 20 cards from an offset: slug, name, location, tagline, pills | `src/plugin/directory.py` |
| `pin_matches` | Reference tool: parses every card by code and keeps the ones the filter matches (the answer key, hidden from the agent) | `src/plugin/directory.py` |

### Tasks

| Task | Does | Runner |
|---|---|---|
| `extract-companies` | Extracts every company matching an industry, batch season and inclusive year range | `agent`, with `read_directory`; reference `pin_matches` |

Example input: `{"industry": "Fintech", "season": "any", "year_from": 2005, "year_to": 2026}`; the
correct answer is Coinbase, Groww, Truebill, Brex and Sendwave, in directory order.

### Verifier

`verify_task` compares the submission with the answer key in seven checks: `count`, `no-duplicates`,
`within-filter`, `no-missing`, `no-extra`, `fields-exact` (all 8 fields of every company) and
`directory-order`. The verdict is valid only when all hold; the score is the share that holds. An
impossible filter (`year_from > year_to`, years outside 2005–2026, padded industry) is refused.

## Layout

```text
.
├── nanoagent.yaml   # manifest: id, runtime, permissions, tools, tasks
├── contract.py      # each tool's and task's typed input and output
├── src/plugin/      # the MCP server (__main__.py) and directory.py; data/ holds the snapshot
├── tests/           # verifier tests: correct, missing, extra, wrong, malformed and boundary cases
├── ui/              # renderers (outputs drawn from their JSON Schema)
├── product/         # product page: product.yaml and icon.svg
└── verifier/        # deterministic verifier: read.py, task.py, checks.py
```

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

Publishing checks every plugin rule: push the plugin to a public GitHub repository and submit its URL
on RUSH Lab's Marketplace.
