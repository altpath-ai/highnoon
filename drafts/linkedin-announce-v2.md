---
status: DRAFT — ready for Bruce's review and edit before posting
target: LinkedIn
tone: Thought leadership — thank inspirations, announce tools, invite community
tags_to_use: Drew Breunig (@drewbreunig)
---

# LinkedIn Post — High Noon Announcement v2

---

Thank you @Drew Breunig — your work directly inspired what I'm releasing today.

Your Spec-Driven Development Triangle and Plumb tool asked the right question: how do we keep specs, tests, and code in sync? But it left a bigger question open: who asks whether the software serves its PURPOSE?

That question became a framework. And the framework became five open-source tools.

---

Introducing **Hedonics Driven Development (HDD)** — classify software, policy, and life decisions by the human purposes they serve.

Five packages. All open source. Each works as a CLI, an MCP server (add to Claude/GPT/Cursor), and a Python library.

```
pip install hedonics      # The shared taxonomy
pip install altpath        # Personal life assessment
pip install highnoon       # Software purpose assessment
pip install mainstreet     # Public policy assessment
pip install frontpage      # Hedonic content discovery
```

---

**hedonics** — The shared language. 10 hedonic life domains (what humans value intrinsically) + 9 fungible cost categories (what blocks access to those domains). Includes a fungibility calculus that computes how to trade surplus resources for deficit resources. Grounded in BLS, MIT Living Wage, and CPI data.

**altpath** — Personal assessment. Score yourself across 10 life domains AND 9 cost burdens. The system identifies not just WHERE you're deficient, but WHY — which costs are blocking you. Then it recommends fungible exchanges: "You have financial surplus but time deficit. Trade money for time to unlock CONNECTION."

**highnoon** — Software assessment. Reads a codebase and classifies it by the human purposes it serves. Not "this is a Python app" — but "this serves CONNECTION at fidelity:high by reducing TIME coordination costs."

**mainstreet** — Policy assessment. Pulls real federal data (BLS American Time Use Survey, MIT Living Wage, CPI) and evaluates whether policy serves Main Street's hedonic needs. Employed Americans spend 45.8% of their day on MEANS (work, commuting, housework) and only 20.5% on ENDS (leisure, connection, care). That's the number mainstreet exists to change.

**frontpage** — The front page of your hedonic life. A content feed ranked by YOUR assessed needs — not engagement metrics. If your CONNECTION is 3/10 and TIME burden is 8/10, it surfaces research on social isolation, tools that save time, and transit policies — all ranked by hedonic relevance to YOU.

---

The insight behind all of this:

We classify software by what it's BUILT WITH — Python, React, microservices. But what if we classified it by what it's BUILT FOR?

Every piece of software serves human purposes (ENDS) and costs human resources (MEANS). Many ends are locked behind means costs. A person who wants more CONNECTION might be blocked by TIME burden from a 60-hour work week. The solution isn't "use a social app." The solution is "reduce TIME burden first, which UNLOCKS CONNECTION."

That's Teleological Hedonic Optimization. Not just assessment — allocation.

---

All five packages are live on PyPI and GitHub. Open for stars, issues, PRs, and discussion.

GitHub: github.com/altpath-ai/highnoon
Website: altpath.ai

Inspired by Drew Breunig's SDD/Plumb work, the BLS hedonic quality adjustment methodology, Aristotle's concept of telos, and a late-night conversation about why the Dewey Decimal system should work for human purposes.

#opensource #hedonics #mcp #python #publicpolicy #wellbeing #altpath #HDD
