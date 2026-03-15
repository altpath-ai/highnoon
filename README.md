# High Noon

**Hedonics Driven Development (HDD)** — classify software, policy, and life decisions by the human purposes they serve.

## Five Packages, One Language

| Package | Install | What it does |
|---------|---------|-------------|
| **[hedonics](packages/hedonics/)** | `pip install hedonics` | Shared taxonomy + fungibility calculus — the common language |
| **[altpath](packages/altpath/)** | `pip install altpath` | Personal hedonic life assessment — score yourself across 10 domains |
| **[highnoon](.)** | `pip install highnoon` | Software purpose assessment — classify code by what it does for humans |
| **[mainstreet](packages/mainstreet/)** | `pip install mainstreet` | Public policy assessment — evaluate policy with real BLS/MIT data |
| **[frontpage](packages/frontpage/)** | `pip install frontpage` | Hedonic content discovery — YOUR front page, ranked by YOUR needs |

Each works as a **CLI**, an **MCP server** (add to Claude/GPT/Cursor), and a **Python library**.

## Quick Start

```bash
pip install hedonics
hedonics domains          # 10 hedonic life domains (ENDS)
hedonics costs            # 9 fungible cost categories (MEANS)
hedonics blockers 07      # What costs block CONNECTION?
hedonics classify "reduce loneliness through community"
```

## The Core Idea

Every piece of software, every policy, every life decision serves **human purposes** (ENDS) and costs **human resources** (MEANS).

**ENDS** — 10 hedonic domains of intrinsic value:
```
01 NOURISHMENT   02 SHELTER    03 HEALTH     04 CARE       05 MOBILITY
06 GROWTH        07 CONNECTION 08 RECREATION 09 EXPRESSION 10 MEANING
```

**MEANS** — 9 fungible cost categories:
```
T TIME    F FINANCIAL   A ATTENTION   P PHYSICAL    S SOCIAL
E ENVIRONMENTAL   R REGULATORY   K KNOWLEDGE   X STATUS
```

Many ends are **locked behind means costs**. Someone who wants more CONNECTION (end) might be blocked by TIME burden (means) from a 60-hour work week. The **fungibility calculus** computes optimal exchanges: trade your FINANCIAL surplus for TIME reduction (hire help, automate) to unlock CONNECTION.

## Add to Your LLM

```json
{
  "mcpServers": {
    "hedonics":   {"command": "python", "args": ["-m", "hedonics.mcp"]},
    "altpath":    {"command": "python", "args": ["-m", "altpath.mcp"]},
    "highnoon":   {"command": "python", "args": ["-m", "highnoon.mcp"]},
    "mainstreet": {"command": "python", "args": ["-m", "mainstreet.mcp"]},
    "frontpage":  {"command": "python", "args": ["-m", "frontpage.mcp"]}
  }
}
```

## Grounded in Empirical Research

- **BLS American Time Use Survey** — how humans actually spend their 24 hours
- **MIT Living Wage Calculator** — what humans need across 8 expenditure categories
- **BLS Consumer Price Index** — hedonic quality adjustment methodology
- **Census American Community Survey** — housing, insurance, commuting, income by geography

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). We especially need help with:
- Test coverage (currently zero)
- Data connectors (BLS API, MIT Living Wage, Census ACS)
- Exchange rate calibration from empirical research
- MCP server testing across different LLMs

## Status

Pre-alpha. The framework is under active development.

## License

MIT

---

Built by [AltPath AI](https://altpath.ai). *Solve problems first. Beautify answers second.*
