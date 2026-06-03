from __future__ import annotations

from dataclasses import dataclass
import json
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path


@dataclass(frozen=True)
class Endpoint:
    label: str
    address: str
    lat: float
    lon: float


PROJECT = {
    "name": "Anna Fiber Planning Dashboard",
    "customer": "Anna Enterprise Campus",
    "market": "Anna, Texas",
    "planner": "Synthetic Network Engineering Group",
    "report_date": "2026-06-03",
    "survey_window": "2026-06-03 08:00-11:30 CDT",
}

ROUTE_GEOJSON_PATH = Path("/Users/shahnawaazshaikh/Downloads/route.geojson")


def _haversine_feet(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_m = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return radius_m * c * 3.28084


def load_actual_route_points() -> list[tuple[float, float]]:
    if not ROUTE_GEOJSON_PATH.exists():
        return [
            (33.35094, -96.55949),
            (33.35110, -96.55943),
            (33.35095, -96.55847),
            (33.35092, -96.55684),
            (33.35147, -96.55683),
            (33.35291, -96.55729),
        ]

    data = json.loads(ROUTE_GEOJSON_PATH.read_text())
    coordinates = data["geometry"]["coordinates"]
    route_points: list[tuple[float, float]] = []
    for lon, lat in coordinates:
        point = (lat, lon)
        if not route_points or route_points[-1] != point:
            route_points.append(point)
    return route_points


def calculate_route_length_ft(points: list[tuple[float, float]]) -> int:
    total = 0.0
    for first, second in zip(points, points[1:]):
        total += _haversine_feet(first[0], first[1], second[0], second[1])
    return int(round(total))


ACTUAL_ROUTE_POINTS = load_actual_route_points()
ACTUAL_ROUTE_LENGTH_FT = calculate_route_length_ft(ACTUAL_ROUTE_POINTS)
ROUTE_SPLIT_INDEX = 5
DISPLAY_EXISTING_ROUTE_POINTS = ACTUAL_ROUTE_POINTS[: ROUTE_SPLIT_INDEX + 1]
DISPLAY_PROPOSED_ROUTE_POINTS = ACTUAL_ROUTE_POINTS[ROUTE_SPLIT_INDEX:]

ENDPOINTS = {
    "start": Endpoint(
        label="Origin Site",
        address="121 Pagoda Drive, Anna, TX 75409",
        lat=ACTUAL_ROUTE_POINTS[0][0],
        lon=ACTUAL_ROUTE_POINTS[0][1],
    ),
    "end": Endpoint(
        label="Destination Site",
        address="313 Kelvinton Drive, Anna, TX 75409",
        lat=ACTUAL_ROUTE_POINTS[-1][0],
        lon=ACTUAL_ROUTE_POINTS[-1][1],
    ),
}

MAP_CENTER = {
    "lat": sum(point[0] for point in ACTUAL_ROUTE_POINTS) / len(ACTUAL_ROUTE_POINTS),
    "lon": sum(point[1] for point in ACTUAL_ROUTE_POINTS) / len(ACTUAL_ROUTE_POINTS),
}

FIBER_SEGMENTS = [
    {
        "id": "existing-backbone-1",
        "name": "Existing 144ct Backbone",
        "type": "existing",
        "status": "Active",
        "color": "#111111",
        "dash_array": None,
        "points": [
            (33.35305, -96.55720),
            (33.35215, -96.55726),
            (33.35145, -96.55730),
            (33.35092, -96.55684),
        ],
        "length_ft": 940,
        "capacity": "144 count",
        "notes": "Existing feeder with splice access near the north transition of the traced corridor.",
    },
    {
        "id": "existing-lateral-1",
        "name": "Existing 24ct Lateral",
        "type": "existing",
        "status": "Reserved",
        "color": "#6c6c6c",
        "dash_array": "8, 10",
        "points": [
            (33.35090, -96.55952),
            (33.35096, -96.55880),
            (33.35095, -96.55847),
        ],
        "length_ft": 320,
        "capacity": "24 count",
        "notes": "Short reserved lateral section at the southern tie-in near the route origin.",
    },
    {
        "id": "proposed-route-a",
        "name": "Route A - Recommended",
        "type": "proposed",
        "status": "Recommended",
        "color": "#cd040b",
        "dash_array": None,
        "points": ACTUAL_ROUTE_POINTS,
        "length_ft": ACTUAL_ROUTE_LENGTH_FT,
        "capacity": "96 count",
        "notes": "Primary route follows the traced OpenStreetMap corridor supplied in route.geojson.",
    },
    {
        "id": "proposed-route-b",
        "name": "Route B - Alternate",
        "type": "alternate",
        "status": "Alternate",
        "color": "#8b8b8b",
        "dash_array": "12, 10",
        "points": [
            (33.35094, -96.55949),
            (33.35110, -96.55920),
            (33.35108, -96.55862),
            (33.35120, -96.55782),
            (33.35152, -96.55730),
            (33.35291, -96.55729),
        ],
        "length_ft": 810,
        "capacity": "96 count",
        "notes": "Alternate path uses the west side frontage with added bend complexity and reduced reuse.",
    },
]

SURVEY_FINDINGS = [
    {
        "name": "Pole 17 clearance check",
        "category": "Aerial review",
        "status": "Pass",
        "priority": "Low",
        "lat": 33.35102,
        "lon": -96.55928,
        "details": "Existing attachment zone has adequate clearance for lash-overbuild with no make-ready required.",
    },
    {
        "name": "Handhole HH-03 access",
        "category": "Access structure",
        "status": "Monitor",
        "priority": "Medium",
        "lat": 33.35093,
        "lon": -96.55684,
        "details": "Lid and throat accessible, but vegetation trimming should be completed before construction mobilization.",
    },
    {
        "name": "Road crossing at collector",
        "category": "Bore crossing",
        "status": "Review",
        "priority": "High",
        "lat": 33.35135,
        "lon": -96.55683,
        "details": "Directional bore preferred to avoid daytime lane closure. Utility locates required prior to final issue-for-construction package.",
    },
    {
        "name": "Service entry at destination",
        "category": "Customer site",
        "status": "Pass",
        "priority": "Low",
        "lat": 33.35289,
        "lon": -96.55730,
        "details": "South wall demarc ready for 2-inch conduit entry and indoor slack storage cabinet.",
    },
]

RISK_ITEMS = [
    {
        "id": "risk-1",
        "title": "Shared utility corridor congestion",
        "severity": "Medium",
        "score": 62,
        "lat": 33.35095,
        "lon": -96.55847,
        "mitigation": "Use existing handhole pull-through to minimize new trenching and hold pre-construction utility walk.",
        "owner": "OSP Engineering",
    },
    {
        "id": "risk-2",
        "title": "Collector road bore permit timing",
        "severity": "High",
        "score": 84,
        "lat": 33.35135,
        "lon": -96.55683,
        "mitigation": "Submit permit package 10 business days ahead of mobilization and reserve bore crew in parallel.",
        "owner": "Permitting",
    },
    {
        "id": "risk-3",
        "title": "HOA landscaping restoration sensitivity",
        "severity": "Medium",
        "score": 58,
        "lat": 33.35210,
        "lon": -96.55726,
        "mitigation": "Limit open trench areas, restore sod same week, and use matting near ornamental beds.",
        "owner": "Construction",
    },
]

BOM_ITEMS = [
    {
        "item": "96ct single-mode fiber cable",
        "quantity": ACTUAL_ROUTE_LENGTH_FT + 120,
        "unit": "ft",
        "unit_cost": 1.92,
        "category": "Cable",
    },
    {
        "item": "2-inch HDPE conduit",
        "quantity": 420,
        "unit": "ft",
        "unit_cost": 2.35,
        "category": "Conduit",
    },
    {
        "item": "Handhole vault 30x48",
        "quantity": 2,
        "unit": "ea",
        "unit_cost": 940.0,
        "category": "Structures",
    },
    {
        "item": "Fiber splice enclosure",
        "quantity": 2,
        "unit": "ea",
        "unit_cost": 420.0,
        "category": "Splicing",
    },
    {
        "item": "Directional bore crew",
        "quantity": 140,
        "unit": "ft",
        "unit_cost": 24.0,
        "category": "Construction",
    },
    {
        "item": "Restoration and traffic control",
        "quantity": 1,
        "unit": "lot",
        "unit_cost": 2850.0,
        "category": "Construction",
    },
]

ROUTE_OPTIONS = [
    {
        "route_id": "proposed-route-a",
        "route_name": "Route A - Recommended",
        "distance_ft": ACTUAL_ROUTE_LENGTH_FT,
        "reuse_ft": 410,
        "new_build_ft": max(ACTUAL_ROUTE_LENGTH_FT - 410, 0),
        "road_crossings": 1,
        "risk_count": 3,
        "estimated_capex": 16480,
        "complexity": 1.9,
        "narrative": "Best blend of actual OSM corridor fidelity, available tie-in reuse, and manageable field execution.",
    },
    {
        "route_id": "proposed-route-b",
        "route_name": "Route B - Alternate",
        "distance_ft": 810,
        "reuse_ft": 160,
        "new_build_ft": 650,
        "road_crossings": 2,
        "risk_count": 5,
        "estimated_capex": 18760,
        "complexity": 3.4,
        "narrative": "Viable fallback, but carries tighter bend geometry, lower reuse, and higher coordination risk.",
    },
]

CHAT_QA = [
    {
        "patterns": ["best path", "recommended route", "which path", "route recommendation"],
        "title": "Best Path Recommendation",
        "summary": "Route A is the preferred corridor because it follows the supplied OpenStreetMap trace, preserves tie-in reuse where available, and delivers the strongest risk-adjusted execution plan.",
        "bullets": [
            "Route A is anchored to the actual path from route.geojson",
            "Reuse of existing feeder/lateral plant: 410 ft",
            f"Net new construction: {max(ACTUAL_ROUTE_LENGTH_FT - 410, 0):,} ft",
            "Estimated capex: $16,480",
        ],
        "recommendation": "Advance Route A into issue-for-construction after permit pre-check and HH-03 vegetation clearance.",
    },
    {
        "patterns": ["bom", "materials", "bill of materials", "cost"],
        "title": "Bill of Materials",
        "summary": "The synthetic BOM is now sized from the traced route length in route.geojson plus slack, structures, and one controlled bore.",
        "table_key": "bom",
        "recommendation": "Carry a 7% material contingency for conduit and restoration to absorb field adjustments.",
    },
    {
        "patterns": ["risk", "risks", "concerns", "issues"],
        "title": "Risk Register",
        "summary": "Current risk posture is manageable, with one high-severity item around road-bore permitting and two medium-severity corridor constraints.",
        "table_key": "risks",
        "recommendation": "Start permitting immediately and sequence utility locates ahead of construction mobilization.",
    },
    {
        "patterns": ["site survey", "survey", "field notes", "observations"],
        "title": "Site Survey Summary",
        "summary": "The corridor survey indicates that both endpoints are serviceable, reuse opportunities are modest, and the main design decision centers on crossing the collector cleanly along the traced path.",
        "table_key": "survey",
        "recommendation": "Convert the road crossing note into a construction method statement in the final package.",
    },
    {
        "patterns": ["compare", "route a", "route b", "alternate"],
        "title": "Route Comparison",
        "summary": "Route A outperforms Route B on corridor fidelity and operational readiness, even though Route B is shorter on paper.",
        "table_key": "routes",
        "recommendation": "Keep Route B as contingency only if access to the traced corridor becomes blocked.",
    },
]

SUPPORTED_QUESTIONS = [
    "What is the best path?",
    "Show me the BOM.",
    "What are the main risks?",
    "Summarize the site survey.",
    "Compare Route A and Route B.",
]
