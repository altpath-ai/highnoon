"""
Shared storage for the Hedonics ecosystem.

All 5 packages (altpath, hedonics, highnoon, mainstreet, frontpage)
read/write to ~/.hedonics/ so results flow between them.

Structure:
  ~/.hedonics/
    profile/
      assessment.json         # altpath: current personal assessment
      history/                # altpath: timestamped assessment history
        assessment_YYYYMMDD_HHMMSS.json
    software/
      assessments/            # highnoon: project purpose assessments
        {project_name}.json
    policy/
      assessments/            # mainstreet: policy hedonic assessments
        {policy_name}.json
    feed/
      items.json              # frontpage: saved feed items with scores
      graded/                 # frontpage: graded content
        {item_hash}.json
    grades/
      software/               # hedonic grades for software
        {project_name}.json
      policy/                 # hedonic grades for policies
        {policy_name}.json
      content/                # hedonic grades for news/research
        {item_hash}.json
    config.json               # shared config
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict


HEDONICS_DIR = Path.home() / ".hedonics"


def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_root() -> Path:
    return _ensure_dir(HEDONICS_DIR)


# === PROFILE (altpath) ===

def save_profile(assessment: dict) -> Path:
    """Save the current personal assessment."""
    d = _ensure_dir(HEDONICS_DIR / "profile")
    path = d / "assessment.json"
    assessment["saved_at"] = datetime.now().isoformat()
    with open(path, "w") as f:
        json.dump(assessment, f, indent=2)
    # Also save to history
    hd = _ensure_dir(d / "history")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    hist_path = hd / f"assessment_{ts}.json"
    with open(hist_path, "w") as f:
        json.dump(assessment, f, indent=2)
    return path


def load_profile() -> dict | None:
    """Load the current personal assessment. Returns None if no assessment exists."""
    path = HEDONICS_DIR / "profile" / "assessment.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def list_profile_history() -> list[Path]:
    """List all historical assessments, newest first."""
    hd = HEDONICS_DIR / "profile" / "history"
    if not hd.exists():
        return []
    return sorted(hd.glob("assessment_*.json"), reverse=True)


# === SOFTWARE ASSESSMENTS (highnoon) ===

def save_software_assessment(project_name: str, assessment: dict) -> Path:
    """Save a software purpose assessment."""
    d = _ensure_dir(HEDONICS_DIR / "software" / "assessments")
    safe_name = project_name.replace("/", "_").replace(" ", "_").lower()
    path = d / f"{safe_name}.json"
    assessment["assessed_at"] = datetime.now().isoformat()
    assessment["project_name"] = project_name
    with open(path, "w") as f:
        json.dump(assessment, f, indent=2)
    return path


def load_software_assessment(project_name: str) -> dict | None:
    safe_name = project_name.replace("/", "_").replace(" ", "_").lower()
    path = HEDONICS_DIR / "software" / "assessments" / f"{safe_name}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def list_software_assessments() -> list[dict]:
    """List all assessed software projects."""
    d = HEDONICS_DIR / "software" / "assessments"
    if not d.exists():
        return []
    results = []
    for p in sorted(d.glob("*.json")):
        with open(p) as f:
            data = json.load(f)
            results.append({
                "project": data.get("project_name", p.stem),
                "file": str(p),
                "assessed_at": data.get("assessed_at", ""),
            })
    return results


# === POLICY ASSESSMENTS (mainstreet) ===

def save_policy_assessment(policy_name: str, assessment: dict) -> Path:
    """Save a policy hedonic assessment."""
    d = _ensure_dir(HEDONICS_DIR / "policy" / "assessments")
    safe_name = policy_name.replace("/", "_").replace(" ", "_").lower()
    path = d / f"{safe_name}.json"
    assessment["assessed_at"] = datetime.now().isoformat()
    assessment["policy_name"] = policy_name
    with open(path, "w") as f:
        json.dump(assessment, f, indent=2)
    return path


def load_policy_assessment(policy_name: str) -> dict | None:
    safe_name = policy_name.replace("/", "_").replace(" ", "_").lower()
    path = HEDONICS_DIR / "policy" / "assessments" / f"{safe_name}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def list_policy_assessments() -> list[dict]:
    d = HEDONICS_DIR / "policy" / "assessments"
    if not d.exists():
        return []
    results = []
    for p in sorted(d.glob("*.json")):
        with open(p) as f:
            data = json.load(f)
            results.append({
                "policy": data.get("policy_name", p.stem),
                "file": str(p),
                "assessed_at": data.get("assessed_at", ""),
            })
    return results


# === FEED ITEMS (frontpage) ===

def save_feed_items(items: list[dict]) -> Path:
    """Save the current feed items with scores."""
    d = _ensure_dir(HEDONICS_DIR / "feed")
    path = d / "items.json"
    with open(path, "w") as f:
        json.dump({"items": items, "saved_at": datetime.now().isoformat()}, f, indent=2)
    return path


def load_feed_items() -> list[dict]:
    path = HEDONICS_DIR / "feed" / "items.json"
    if path.exists():
        with open(path) as f:
            return json.load(f).get("items", [])
    return []


# === GRADES (shared grading system) ===

@dataclass
class HedonicGrade:
    """A hedonic grade for any item (software, policy, content).

    Grades assess how well something serves hedonic purposes
    and how it modifies costs, relative to the user's profile."""
    item_type: str              # "software" | "policy" | "content"
    item_name: str
    item_id: str = ""           # hash or unique identifier

    # Ends served
    domains_served: list[str] = field(default_factory=list)
    domain_quality: dict = field(default_factory=dict)  # domain_code → quality rating

    # Costs modified
    costs_modified: list[str] = field(default_factory=list)
    cost_effects: dict = field(default_factory=dict)  # cost_code → {direction, magnitude}

    # Scores
    purpose_score: float = 0.0      # 0-10: how well does it serve its declared purpose?
    cost_efficiency: float = 0.0    # 0-10: how efficiently does it modify costs?
    relevance_score: float = 0.0    # 0-10: how relevant to YOUR profile?
    overall_grade: str = ""         # A/B/C/D/F

    # Context
    graded_at: str = ""
    graded_by: str = "user"         # "user" | "llm" | "community"
    notes: str = ""

    def compute_overall(self):
        """Compute overall letter grade from scores."""
        avg = (self.purpose_score + self.cost_efficiency + self.relevance_score) / 3
        if avg >= 9: self.overall_grade = "A+"
        elif avg >= 8: self.overall_grade = "A"
        elif avg >= 7: self.overall_grade = "B+"
        elif avg >= 6: self.overall_grade = "B"
        elif avg >= 5: self.overall_grade = "C+"
        elif avg >= 4: self.overall_grade = "C"
        elif avg >= 3: self.overall_grade = "D"
        else: self.overall_grade = "F"
        return self.overall_grade

    def to_dict(self) -> dict:
        self.compute_overall()
        return {
            "item_type": self.item_type,
            "item_name": self.item_name,
            "item_id": self.item_id,
            "domains_served": self.domains_served,
            "domain_quality": self.domain_quality,
            "costs_modified": self.costs_modified,
            "cost_effects": self.cost_effects,
            "purpose_score": self.purpose_score,
            "cost_efficiency": self.cost_efficiency,
            "relevance_score": self.relevance_score,
            "overall_grade": self.overall_grade,
            "graded_at": self.graded_at or datetime.now().isoformat(),
            "graded_by": self.graded_by,
            "notes": self.notes,
        }


def _item_hash(name: str) -> str:
    return hashlib.sha256(name.encode()).hexdigest()[:12]


def save_grade(grade: HedonicGrade) -> Path:
    """Save a hedonic grade for any item."""
    subdir = {"software": "software", "policy": "policy", "content": "content"}
    d = _ensure_dir(HEDONICS_DIR / "grades" / subdir.get(grade.item_type, "other"))
    grade.item_id = grade.item_id or _item_hash(grade.item_name)
    grade.graded_at = grade.graded_at or datetime.now().isoformat()
    safe_name = grade.item_name.replace("/", "_").replace(" ", "_").lower()[:60]
    path = d / f"{safe_name}.json"
    with open(path, "w") as f:
        json.dump(grade.to_dict(), f, indent=2)
    return path


def load_grade(item_type: str, item_name: str) -> dict | None:
    subdir = {"software": "software", "policy": "policy", "content": "content"}
    safe_name = item_name.replace("/", "_").replace(" ", "_").lower()[:60]
    path = HEDONICS_DIR / "grades" / subdir.get(item_type, "other") / f"{safe_name}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def list_grades(item_type: str = None) -> list[dict]:
    """List all grades, optionally filtered by type."""
    results = []
    base = HEDONICS_DIR / "grades"
    if not base.exists():
        return []
    subdirs = [item_type] if item_type else ["software", "policy", "content"]
    for subdir in subdirs:
        d = base / subdir
        if not d.exists():
            continue
        for p in sorted(d.glob("*.json")):
            with open(p) as f:
                data = json.load(f)
                results.append(data)
    return sorted(results, key=lambda g: g.get("graded_at", ""), reverse=True)


def grade_summary() -> dict:
    """Summary of all grades across types."""
    all_grades = list_grades()
    by_type = {}
    for g in all_grades:
        t = g.get("item_type", "other")
        if t not in by_type:
            by_type[t] = {"count": 0, "grades": {}}
        by_type[t]["count"] += 1
        grade_letter = g.get("overall_grade", "?")
        by_type[t]["grades"][grade_letter] = by_type[t]["grades"].get(grade_letter, 0) + 1
    return {
        "total_graded": len(all_grades),
        "by_type": by_type,
        "storage_path": str(HEDONICS_DIR / "grades"),
    }
