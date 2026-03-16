# High Noon / HDD — Next Steps

> Session: March 15-16, 2026 (Saturday afternoon → Monday morning)
> Status: 5 packages live on PyPI, all with CLI + MCP + dashboards

## Priority 1: Before LinkedIn traffic arrives

- [ ] Verify LinkedIn post published (scheduled Monday morning)
- [ ] Test `pip install altpath hedonics highnoon mainstreet frontpage` on a clean machine
- [ ] Verify `altpath ui` and `frontpage ui` work from fresh PyPI install
- [ ] Check GitHub issues are visible and welcoming (#1-#5 + welcome discussion)

## Priority 2: Testing & Quality

- [ ] Add pytest suites — zero test coverage currently (GitHub Issue #2)
- [ ] Test all 5 MCP servers with Claude Code, Cursor, and GPT
- [ ] Fix BLS API SSL cert issue on macOS (`mainstreet bls` fails locally)
- [ ] Test dashboard import flow end-to-end (altpath UI → download JSON → frontpage UI → import)
- [ ] Frontpage: persist reactions to ~/.hedonics/ (currently in-memory only)

## Priority 3: Framework Refinements

- [ ] Dual-coded activities: work can be BOTH T.1 (cost) AND HTC 07 (connection) — need to model this
- [ ] Upgrade `hedonics classify` from keyword matching to LLM-assisted classification (Issue #3)
- [ ] Calibrate fungibility exchange rates from empirical research (Issue #5)
- [ ] Add processing/nutrient/hedonic three-layer model to the taxonomy code
- [ ] Status Efficiency Ratio (SER) — codify the status cost measurement
- [ ] Attention subcategories A.5/A.6 (willpower) — add to frontpage dashboard suggestions

## Priority 4: Data Connectors

- [ ] Real MIT Living Wage API scraper for `mainstreet` (Issue #4)
- [ ] Census ACS API connector (housing, insurance, commuting by geography)
- [ ] RSS/web search connectors for `frontpage` (live content instead of curated)
- [ ] PyPI/GitHub search for `highnoon` (find real software to tag)

## Priority 5: Features

- [ ] Frontpage: pattern analysis should auto-update altpath profile (revealed preference → re-score)
- [ ] Hedonics registry: federated — share grades across users, not just local
- [ ] Altpath: longitudinal tracking — compare assessments over time, show deltas
- [ ] Highnoon: auto-classify GitHub repos by reading README + package.json
- [ ] Mainstreet: location-based assessment (`mainstreet assess "Los Angeles County"`)
- [ ] All dashboards: add "Share Results" (export as image/link)

## Priority 6: Distribution

- [ ] GitHub CLI extensions (gh-hedonics, gh-altpath, etc.)
- [ ] Host dashboards on altpath.ai (static site)
- [ ] Publish hedonics taxonomy as a standalone reference doc
- [ ] Write the conceptual paper (THO framework, fungibility calculus, research grounding)
- [ ] AltPath.ai website: integrate the 10 HDD domains with existing Life Design Assessment

## Current Package Versions (PyPI)

| Package | Version | Last Published |
|---------|---------|---------------|
| hedonics | 0.1.5 | 2026-03-15 |
| altpath | 0.1.3 | 2026-03-15 |
| highnoon | 0.1.3 | 2026-03-15 |
| mainstreet | 0.1.2 | 2026-03-15 |
| frontpage | 0.1.4 | 2026-03-16 |
