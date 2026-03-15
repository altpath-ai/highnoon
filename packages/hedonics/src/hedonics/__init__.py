"""
Hedonics — Human Hedonics Teleology Classification System

The classification framework behind Hedonics Driven Development (HDD).
Provides the taxonomy, assessment tools, and quality measurement for
classifying software and human activity by purpose.

Part of the High Noon project: https://github.com/altpath-ai/highnoon
"""

__version__ = "0.1.4"

from hedonics.taxonomy import DOMAINS, get_domain, list_domains
from hedonics.htc import HTC
from hedonics.hqc import HQC, HQCM, list_all_costs, get_cost_subcategories
from hedonics.fungibility import CostProfile, Exchange, compute_exchanges
from hedonics.storage import (
    save_profile, load_profile, save_grade, load_grade, list_grades,
    save_software_assessment, save_policy_assessment, save_feed_items,
    HedonicGrade, grade_summary,
)
from hedonics.registry import search, search_by_need, search_cost_reducers, rebuild_index, registry_stats
