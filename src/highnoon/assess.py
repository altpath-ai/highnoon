"""
Software purpose assessment engine.

Reads project artifacts (README, specs, code) and proposes
Hedonic Teleology Classifications (HTCs).
"""

from dataclasses import dataclass, field
from pathlib import Path

from hedonics.htc import HTC
from hedonics.hqc import HQC, HQCM


@dataclass
class SoftwareAssessment:
    """Assessment of a software project's human purpose."""
    project_path: str = ""
    project_name: str = ""
    htcs: list[HTC] = field(default_factory=list)
    hqcs: list[HQC] = field(default_factory=list)
    summary: str = ""
    method: str = "manual"  # manual | llm-proposed | certified

    def add_purpose(self, domain_code: str, activity: str = "", quality: dict = None, description: str = ""):
        self.htcs.append(HTC(
            domain_code=domain_code,
            activity=activity,
            quality=quality or {},
            description=description,
        ))

    def add_cost(self, category: str, subcategory: str = "", description: str = "", **modifiers):
        self.hqcs.append(HQC(
            category=category,
            subcategory=subcategory,
            description=description,
            modifier=HQCM(**modifiers),
        ))

    def to_dict(self) -> dict:
        return {
            "project": self.project_name,
            "path": self.project_path,
            "method": self.method,
            "summary": self.summary,
            "purposes": [
                {"htc": str(h), "domain": h.domain_code, "quality": h.quality, "description": h.description}
                for h in self.htcs
            ],
            "costs": [
                {"hqc": str(c), "category": c.category_name, "modifiers": c.modifier.to_dict(), "description": c.description}
                for c in self.hqcs
            ],
        }


def read_project_signals(path: str) -> dict:
    """Read README, pyproject.toml, and other signals from a project."""
    p = Path(path)
    signals = {"path": str(p.resolve()), "name": p.name}

    readme_candidates = ["README.md", "README.rst", "README.txt", "README"]
    for name in readme_candidates:
        readme = p / name
        if readme.exists():
            signals["readme"] = readme.read_text(errors="replace")[:5000]
            break

    pyproject = p / "pyproject.toml"
    if pyproject.exists():
        signals["pyproject"] = pyproject.read_text(errors="replace")[:3000]

    package_json = p / "package.json"
    if package_json.exists():
        signals["package_json"] = package_json.read_text(errors="replace")[:3000]

    return signals
