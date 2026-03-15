# Contributing to High Noon

Thanks for your interest in Hedonics Driven Development.

## Quick Start

```bash
git clone https://github.com/altpath-ai/highnoon.git
cd highnoon

# Install all packages in editable mode
pip install -e packages/hedonics
pip install -e packages/altpath
pip install -e .                      # highnoon
pip install -e packages/mainstreet
pip install -e packages/frontpage

# Test the CLIs
hedonics domains
altpath domains
highnoon scan .
mainstreet time-budget
frontpage suggest 07
```

## Package Structure

```
highnoon/                    # Root package (highnoon CLI + MCP)
packages/
  hedonics/                  # Shared taxonomy + fungibility calculus
  altpath/                   # Personal hedonic assessment
  mainstreet/                # Public policy assessment
  frontpage/                 # Hedonic content discovery
```

`hedonics` is the shared dependency. Changes to the taxonomy affect all packages.

## Ways to Contribute

- **Taxonomy refinement**: Are the 10 domains right? Are the cost subcategories complete?
- **Exchange rate calibration**: Help ground the fungibility calculus in empirical research
- **Data connectors**: BLS API, MIT Living Wage scraper, Census ACS, RSS feeds
- **Tests**: We need pytest coverage across all packages
- **Documentation**: Examples, tutorials, use cases
- **MCP integration**: Testing with different LLMs (Claude, GPT, Cursor, etc.)

## Guidelines

- Keep it simple. Don't over-engineer.
- Ground claims in data. The framework is empirical, not ideological.
- One PR per concern. Small, focused changes.
- Add tests for new functionality.

## Code of Conduct

Be thoughtful. This project deals with human well-being. Approach it with the seriousness it deserves.
