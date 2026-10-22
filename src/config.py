"""Configuration settings, county definitions, and mappings for Met Éireann feeds."""

from typing import Dict, List, Set

MET_EIREANN_WARNINGS_URL = "https://www.met.ie/Open_Data/json/warning_ALL.json"
USER_AGENT = "MetAlertsCalendar/1.0 (+https://github.com/vician/met-alerts)"
DEFAULT_REQUEST_TIMEOUT = 15  # seconds

# FIPS 10-4 / Met Éireann region code mapping to county slugs
EI_REGION_TO_COUNTY: Dict[str, str] = {
    "EI01": "carlow",
    "EI02": "cavan",
    "EI03": "clare",
    "EI04": "cork",
    "EI06": "donegal",
    "EI07": "dublin",
    "EI10": "galway",
    "EI11": "kerry",
    "EI12": "kildare",
    "EI13": "kilkenny",
    "EI14": "leitrim",
    "EI15": "laois",
    "EI16": "limerick",
    "EI18": "longford",
    "EI19": "louth",
    "EI20": "mayo",
    "EI21": "meath",
    "EI22": "monaghan",
    "EI23": "offaly",
    "EI24": "roscommon",
    "EI25": "sligo",
    "EI26": "tipperary",
    "EI27": "waterford",
    "EI29": "westmeath",
    "EI30": "wexford",
    "EI31": "wicklow",
}

# The 26 traditional Republic of Ireland counties
COUNTIES: List[Dict[str, str]] = [
    {"slug": "carlow", "name": "Carlow", "code": "EI01", "province": "Leinster"},
    {"slug": "cavan", "name": "Cavan", "code": "EI02", "province": "Ulster"},
    {"slug": "clare", "name": "Clare", "code": "EI03", "province": "Munster"},
    {"slug": "cork", "name": "Cork", "code": "EI04", "province": "Munster"},
    {"slug": "donegal", "name": "Donegal", "code": "EI06", "province": "Ulster"},
    {"slug": "dublin", "name": "Dublin", "code": "EI07", "province": "Leinster"},
    {"slug": "galway", "name": "Galway", "code": "EI10", "province": "Connacht"},
    {"slug": "kerry", "name": "Kerry", "code": "EI11", "province": "Munster"},
    {"slug": "kildare", "name": "Kildare", "code": "EI12", "province": "Leinster"},
    {"slug": "kilkenny", "name": "Kilkenny", "code": "EI13", "province": "Leinster"},
    {"slug": "laois", "name": "Laois", "code": "EI15", "province": "Leinster"},
    {"slug": "leitrim", "name": "Leitrim", "code": "EI14", "province": "Connacht"},
    {"slug": "limerick", "name": "Limerick", "code": "EI16", "province": "Munster"},
    {"slug": "longford", "name": "Longford", "code": "EI18", "province": "Leinster"},
    {"slug": "louth", "name": "Louth", "code": "EI19", "province": "Leinster"},
    {"slug": "mayo", "name": "Mayo", "code": "EI20", "province": "Connacht"},
    {"slug": "meath", "name": "Meath", "code": "EI21", "province": "Leinster"},
    {"slug": "monaghan", "name": "Monaghan", "code": "EI22", "province": "Ulster"},
    {"slug": "offaly", "name": "Offaly", "code": "EI23", "province": "Leinster"},
    {"slug": "roscommon", "name": "Roscommon", "code": "EI24", "province": "Connacht"},
    {"slug": "sligo", "name": "Sligo", "code": "EI25", "province": "Connacht"},
    {"slug": "tipperary", "name": "Tipperary", "code": "EI26", "province": "Munster"},
    {"slug": "waterford", "name": "Waterford", "code": "EI27", "province": "Munster"},
    {"slug": "westmeath", "name": "Westmeath", "code": "EI29", "province": "Leinster"},
    {"slug": "wexford", "name": "Wexford", "code": "EI30", "province": "Leinster"},
    {"slug": "wicklow", "name": "Wicklow", "code": "EI31", "province": "Leinster"},
]

# Additional 6 Northern Ireland counties (in case referenced in feeds)
NORTHERN_IRELAND_COUNTIES: List[Dict[str, str]] = [
    {"slug": "antrim", "name": "Antrim", "code": "UK-ANT", "province": "Ulster"},
    {"slug": "armagh", "name": "Armagh", "code": "UK-ARM", "province": "Ulster"},
    {"slug": "down", "name": "Down", "code": "UK-DOW", "province": "Ulster"},
    {"slug": "fermanagh", "name": "Fermanagh", "code": "UK-FER", "province": "Ulster"},
    {"slug": "derry", "name": "Derry", "code": "UK-DRY", "province": "Ulster"},
    {"slug": "tyrone", "name": "Tyrone", "code": "UK-TYR", "province": "Ulster"},
]

# Mapping province names to county slugs
PROVINCES: Dict[str, Set[str]] = {
    "leinster": {
        "carlow", "dublin", "kildare", "kilkenny", "laois", "longford",
        "louth", "meath", "offaly", "westmeath", "wexford", "wicklow"
    },
    "munster": {
        "clare", "cork", "kerry", "limerick", "tipperary", "waterford"
    },
    "connacht": {
        "galway", "leitrim", "mayo", "roscommon", "sligo"
    },
    "ulster": {
        "cavan", "donegal", "monaghan", "antrim", "armagh", "down", "fermanagh", "derry", "tyrone"
    },
}

# Lookup dictionaries for fast reference
COUNTY_BY_SLUG: Dict[str, Dict[str, str]] = {c["slug"]: c for c in COUNTIES}
COUNTY_SLUGS: List[str] = [c["slug"] for c in COUNTIES]
ALL_COUNTY_SLUGS: Set[str] = set(COUNTY_SLUGS)

# Marine coastal region codes (EI805 to EI825)
MARINE_REGIONS: Set[str] = {f"EI8{i:02d}" for i in range(1, 30)}
