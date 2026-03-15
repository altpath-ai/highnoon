"""
Hedonics — Human Hedonics Teleology Classification System

The classification framework behind Hedonics Driven Development (HDD).
Provides the taxonomy, assessment tools, and quality measurement for
classifying software and human activity by purpose.

Part of the High Noon project: https://github.com/altpath-ai/highnoon
"""

__version__ = "0.1.1"

from hedonics.taxonomy import DOMAINS, get_domain, list_domains
from hedonics.htc import HTC
from hedonics.hqc import HQC, HQCM
