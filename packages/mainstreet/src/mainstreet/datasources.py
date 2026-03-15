"""
Federal data source connectors.

Pulls real data from public APIs and datasets:
- BLS (Bureau of Labor Statistics): CPI, ATUS, Employment
- MIT Living Wage Calculator
- Census American Community Survey
"""

from dataclasses import dataclass, field
import json
import urllib.request
import urllib.error


BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# Key BLS series IDs
BLS_SERIES = {
    "cpi_all": "CUUR0000SA0",           # CPI All Items
    "cpi_food": "CUUR0000SAF1",          # CPI Food at Home
    "cpi_housing": "CUUR0000SAH1",       # CPI Shelter
    "cpi_medical": "CUUR0000SAM",        # CPI Medical Care
    "cpi_transport": "CUUR0000SAT",      # CPI Transportation
    "cpi_education": "CUUR0000SAE1",     # CPI Education
    "cpi_recreation": "CUUR0000SAR",     # CPI Recreation
    "cpi_apparel": "CUUR0000SAA",        # CPI Apparel
    "avg_hourly_earnings": "CES0500000003",  # Avg Hourly Earnings
    "avg_weekly_hours": "CES0500000002",     # Avg Weekly Hours
    "unemployment_rate": "LNS14000000",      # Unemployment Rate
}

# MIT Living Wage base URL pattern
MIT_LW_URL = "https://livingwage.mit.edu/counties/{fips}"

# ATUS time allocation (national averages, hours per day)
# Source: BLS ATUS 2024 results
ATUS_NATIONAL_AVERAGES = {
    "personal_care": 9.47,      # Includes sleep (~8.5 hrs)
    "eating_drinking": 1.14,
    "household_activities": 1.72,
    "purchasing": 0.63,
    "caring_hh_members": 0.45,
    "caring_nonhh_members": 0.15,
    "working": 3.48,            # Averaged across all persons (employed work more)
    "education": 0.42,
    "organizational_civic": 0.15,
    "leisure_sports": 5.28,
    "telephone": 0.15,
    "traveling": 1.12,
    "other": 0.17,
}

# ATUS for employed persons (the relevant comparison)
ATUS_EMPLOYED_AVERAGES = {
    "working": 7.89,
    "leisure_sports": 3.52,
    "personal_care": 8.68,
    "household_activities": 1.28,
    "eating_drinking": 1.01,
    "traveling": 1.30,
    "caring_hh_members": 0.38,
    "purchasing": 0.51,
}


@dataclass
class LivingWageData:
    """MIT Living Wage data for a location."""
    location: str = ""
    fips: str = ""
    living_wage_1a0c: float = 0.0   # 1 adult, 0 children
    living_wage_1a1c: float = 0.0   # 1 adult, 1 child
    living_wage_2a2c: float = 0.0   # 2 adults, 2 children (1 working)
    poverty_wage: float = 0.0
    minimum_wage: float = 0.0
    food_cost: float = 0.0         # Annual
    housing_cost: float = 0.0      # Annual
    medical_cost: float = 0.0      # Annual
    transportation_cost: float = 0.0
    childcare_cost: float = 0.0
    other_cost: float = 0.0
    civic_cost: float = 0.0
    broadband_cost: float = 0.0
    tax_cost: float = 0.0

    def total_annual_cost(self) -> float:
        return (self.food_cost + self.housing_cost + self.medical_cost +
                self.transportation_cost + self.childcare_cost +
                self.other_cost + self.civic_cost + self.broadband_cost +
                self.tax_cost)

    def to_dict(self) -> dict:
        return {
            "location": self.location,
            "wages": {
                "living_wage_1a0c": self.living_wage_1a0c,
                "living_wage_1a1c": self.living_wage_1a1c,
                "living_wage_2a2c": self.living_wage_2a2c,
                "poverty_wage": self.poverty_wage,
                "minimum_wage": self.minimum_wage,
            },
            "annual_costs": {
                "food": self.food_cost,
                "housing": self.housing_cost,
                "medical": self.medical_cost,
                "transportation": self.transportation_cost,
                "childcare": self.childcare_cost,
                "civic": self.civic_cost,
                "broadband": self.broadband_cost,
                "other": self.other_cost,
                "tax": self.tax_cost,
                "total": self.total_annual_cost(),
            },
        }


def fetch_bls_series(series_ids: list[str], start_year: int = 2024,
                     end_year: int = 2025, api_key: str = "") -> dict:
    """Fetch data from the BLS public API.

    Args:
        series_ids: List of BLS series IDs
        start_year: Start year
        end_year: End year
        api_key: Optional BLS API key (higher rate limits)

    Returns:
        Dict of series_id → list of data points
    """
    payload = json.dumps({
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
    }).encode()

    url = BLS_API_URL
    if api_key:
        url += f"?registrationkey={api_key}"

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            results = {}
            if data.get("status") == "REQUEST_SUCCEEDED":
                for series in data.get("Results", {}).get("series", []):
                    sid = series["seriesID"]
                    results[sid] = [
                        {"year": d["year"], "period": d["period"],
                         "value": float(d["value"])}
                        for d in series.get("data", [])
                    ]
            return results
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        return {"error": str(e)}


def get_atus_profile(employed: bool = True) -> dict:
    """Get ATUS time allocation profile.

    Returns national average hours/day by activity.
    Maps to hedonic domains and cost categories.
    """
    averages = ATUS_EMPLOYED_AVERAGES if employed else ATUS_NATIONAL_AVERAGES

    # Map ATUS categories to hedonic domains and cost categories
    mapped = {}
    for activity, hours in averages.items():
        if activity == "working":
            mapped[activity] = {
                "hours_per_day": hours,
                "type": "MEANS",
                "cost_category": "T.1",
                "note": "Labor time — a cost borne in exchange for income",
            }
        elif activity == "traveling":
            mapped[activity] = {
                "hours_per_day": hours,
                "type": "MEANS",
                "cost_category": "T.5",
                "note": "Transit time — instrumental movement",
            }
        elif activity == "household_activities":
            mapped[activity] = {
                "hours_per_day": hours,
                "type": "MEANS",
                "cost_category": "T.6",
                "note": "Maintenance/upkeep — instrumental",
            }
        elif activity == "purchasing":
            mapped[activity] = {
                "hours_per_day": hours,
                "type": "MEANS",
                "cost_category": "T.4",
                "note": "Coordination — instrumental",
            }
        elif activity == "leisure_sports":
            mapped[activity] = {
                "hours_per_day": hours,
                "type": "END",
                "htc_domains": ["07", "08"],
                "note": "CONNECTION + RECREATION — intrinsic hedonic value",
            }
        elif activity == "eating_drinking":
            mapped[activity] = {
                "hours_per_day": hours,
                "type": "END",
                "htc_domains": ["01"],
                "note": "NOURISHMENT — intrinsic hedonic value",
            }
        elif activity == "personal_care":
            mapped[activity] = {
                "hours_per_day": hours,
                "type": "PROCESSING",
                "htc_domains": ["02", "03"],
                "note": "SHELTER + HEALTH — processing capacity (includes sleep)",
            }
        elif activity == "caring_hh_members":
            mapped[activity] = {
                "hours_per_day": hours,
                "type": "END",
                "htc_domains": ["04"],
                "note": "CARE — intrinsic hedonic value",
            }
        else:
            mapped[activity] = {
                "hours_per_day": hours,
                "type": "OTHER",
            }

    # Compute time budget
    total_means = sum(
        v["hours_per_day"] for v in mapped.values() if v.get("type") == "MEANS"
    )
    total_ends = sum(
        v["hours_per_day"] for v in mapped.values() if v.get("type") == "END"
    )
    total_processing = sum(
        v["hours_per_day"] for v in mapped.values() if v.get("type") == "PROCESSING"
    )

    return {
        "profile": "employed" if employed else "all_persons",
        "activities": mapped,
        "time_budget": {
            "means_hours": round(total_means, 2),
            "ends_hours": round(total_ends, 2),
            "processing_hours": round(total_processing, 2),
            "means_pct": round(total_means / 24 * 100, 1),
            "ends_pct": round(total_ends / 24 * 100, 1),
            "processing_pct": round(total_processing / 24 * 100, 1),
        },
    }
