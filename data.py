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

ROUTE_ANALYSIS_TABLES = {
    "location_overview": [
        {"Parameter": "Origin", "Value": "109 Pagoda Dr, Anna, TX 75409"},
        {"Parameter": "Origin Coords", "Value": "33.3444, -96.5612"},
        {"Parameter": "Destination", "Value": "313 Kelvinton Drive, Anna, TX 75409"},
        {"Parameter": "Dest Coords", "Value": "33.3361, -96.5745"},
        {"Parameter": "City", "Value": "Anna"},
        {"Parameter": "County", "Value": "Collin County, Texas"},
        {"Parameter": "Straight-line Distance", "Value": "~1.10 mi"},
        {"Parameter": "Estimated Road Distance", "Value": "~1.55 mi"},
    ],
    "route_a": [
        {"Segment": "1", "Road": "Pagoda Dr south to Hackberry Dr / Taylor Blvd", "Distance": "~0.3 mi", "Method": "Micro-trench (neighborhood ROW)", "Cost": "$10,500"},
        {"Segment": "2", "Road": "Taylor Blvd west to N Powell Pkwy (SH-5)", "Distance": "~0.5 mi", "Method": "Micro-trench", "Cost": "$17,500"},
        {"Segment": "3", "Road": "N Powell Pkwy (SH-5) Intersection", "Distance": "~0.1 mi", "Method": "Directional bore (TxDOT highway crossing)", "Cost": "$12,000"},
        {"Segment": "4", "Road": "West Crossing Blvd westbound", "Distance": "~0.4 mi", "Method": "Micro-trench", "Cost": "$14,000"},
        {"Segment": "5", "Road": "West Crossing Blvd to Kelvinton Dr (destination)", "Distance": "~0.25 mi", "Method": "Directional bore / micro-trench", "Cost": "$9,500"},
        {"Segment": "Total", "Road": "", "Distance": "~1.55 mi", "Method": "", "Cost": "$63,500"},
    ],
    "route_b": [
        {"Segment": "1", "Road": "Pagoda Dr North to Willow Creek Blvd / Rosamond Pkwy", "Distance": "~0.4 mi", "Method": "Micro-trench", "Cost": "$14,000"},
        {"Segment": "2", "Road": "Rosamond Pkwy West to N Powell Pkwy (SH-5)", "Distance": "~0.6 mi", "Method": "Micro-trench", "Cost": "$21,000"},
        {"Segment": "3", "Road": "SH-5 Crossing at Rosamond / Finley", "Distance": "~0.1 mi", "Method": "Directional bore", "Cost": "$12,000"},
        {"Segment": "4", "Road": "Finley Blvd West into West Crossing sector", "Distance": "~0.7 mi", "Method": "Micro-trench + bore", "Cost": "$26,500"},
        {"Segment": "Total", "Road": "", "Distance": "~1.8 mi", "Method": "", "Cost": "$73,500"},
    ],
    "route_c": [
        {"Segment": "1", "Road": "Neighborhood egress south to E White St (FM 455)", "Distance": "~0.6 mi", "Method": "Micro-trench", "Cost": "$21,000"},
        {"Segment": "2", "Road": "FM 455 West underpass / crossing at SH-5 & Railroad", "Distance": "~0.5 mi", "Method": "Deep directional bore", "Cost": "$35,000"},
        {"Segment": "3", "Road": "West Crossing neighborhood entry moving north", "Distance": "~0.7 mi", "Method": "Micro-trench", "Cost": "$24,500"},
        {"Segment": "Total", "Road": "", "Distance": "~1.8 mi", "Method": "", "Cost": "$80,500"},
    ],
    "obstructions": [
        {"Factor": "Road Crossings", "Finding": "Multiple residential collector intersections", "Severity": "Low"},
        {"Factor": "State Highway 5 (N Powell Pkwy)", "Finding": "Active TxDOT right-of-way — bore mandatory", "Severity": "High"},
        {"Factor": "Fences / Landscaping", "Finding": "Standard suburban lot density; minimal footprint issue", "Severity": "Low"},
        {"Factor": "DART ROW / Rail", "Finding": "Runs parallel to SH-5 in areas; crossing clearance required", "Severity": "High"},
        {"Factor": "Utility Conflicts", "Finding": "Intersecting neighborhood water, residential gas (Atmos)", "Severity": "Medium"},
    ],
    "civil_work": [
        {"Parameter": "Primary Method", "Value": "Micro-trenching in soft/hardscape + directional boring at major roadways"},
        {"Parameter": "Trench Depth", "Value": "24-36 inches (Anna city construction code specification)"},
        {"Parameter": "Conduit", "Value": '2" HDPE SDR-11 innerduct'},
        {"Parameter": "Soil Type", "Value": "Houston Black Clay (Highly expansive, requires proper tension metrics during boring)"},
        {"Parameter": "ROW Availability", "Value": "Utilizes municipal utility easements flanking public sidewalks"},
    ],
    "existing_infrastructure": [
        {"Asset": "Existing Fiber", "Available?": "Yes", "Details": "AT&T / Suddenlink (Optimum) infrastructure present; overbuild required"},
        {"Asset": "Utility Poles", "Available?": "Partial", "Details": "Neighborhoods are primarily undergrounded utilities; backhaul feeds are on Oncor poles"},
        {"Asset": "Natural Gas Lines", "Available?": "Yes", "Details": "Atmos Energy residential lines active; requires potholing before boring"},
        {"Asset": "Water / Storm Infrastructure", "Available?": "Yes", "Details": "City of Anna water/sewer networks mapped to public ROW edges"},
    ],
    "fiber_spec": [
        {"Parameter": "Feeder Cable", "Specification": "144F loose-tube single-mode (OS2, G.652.D)"},
        {"Parameter": "Distribution Cable", "Specification": "48F / 72F single-mode inside subdivision loops"},
        {"Parameter": "Drop Cable", "Specification": "2F flat-drop, toneable for locating"},
        {"Parameter": "Splice Method", "Specification": "Fusion splice (Max attenuation target < 0.1 dB per splice)"},
        {"Parameter": "Testing Requirement", "Specification": "Bi-directional OTDR validation at 1310nm and 1550nm"},
    ],
    "splice_plan": [
        {"Splice Point": "SP-01", "Location": "Egress near 109 Pagoda Dr", "Type": "Handhole Splice", "Notes": "Tie-in to neighborhood tap point"},
        {"Splice Point": "SP-02", "Location": "Intersection of Taylor Blvd & Powell Pkwy", "Type": "Vault Splice", "Notes": "Transition point prior to highway bore"},
        {"Splice Point": "SP-03", "Location": "West Crossing entry vault", "Type": "Vault Splice", "Notes": "Distribution hub node"},
        {"Splice Point": "SP-04", "Location": "313 Kelvinton Dr", "Type": "Handhole/MST", "Notes": "Hand-off drop terminal"},
    ],
    "power_equipment": [
        {"Parameter": "FDH Power", "Value": "Fully passive splitters (no electrical feed required at cabinet)"},
        {"Parameter": "OLT Hub Platform", "Value": "Scaled for regional node deployment"},
        {"Parameter": "Splitter Ratio", "Value": "1:32 standard architecture"},
        {"Parameter": "Optical Budget", "Value": "Highly favorable; deployment path distance is exceptionally short (< 2 miles)"},
    ],
    "permits": [
        {"Requirement": "City of Anna ROW Permit", "Status": "Required for all neighborhood trenching", "Timeline": "2-3 weeks"},
        {"Requirement": "TxDOT Utility Permit", "Status": "Required for SH-5 / Powell Pkwy directional bore", "Timeline": "4-6 weeks"},
        {"Requirement": "Texas Central / Railroad Crossing Permit", "Status": "May apply depending on parallel track boundaries", "Timeline": "6-8 weeks"},
        {"Requirement": "Texas 811 Locate Notice", "Status": "Mandatory requirement before any ground penetration", "Timeline": "48-72 hours"},
    ],
    "cost_comparison": [
        {"Route": "A: Willow Creek to West Crossing (BEST)", "Distance": "~1.55 mi", "Cost": "$63,500", "Cost/mi": "~$40,967/mi", "Complexity": "Medium", "Key Risk": "SH-5 Highway Crossing"},
        {"Route": "B: Finley Blvd Extension", "Distance": "~1.80 mi", "Cost": "$73,500", "Cost/mi": "~$40,833/mi", "Complexity": "Medium", "Key Risk": "Longer civil build distance"},
        {"Route": "C: Southern Perimeter (White St)", "Distance": "~1.80 mi", "Cost": "$80,500", "Cost/mi": "~$44,722/mi", "Complexity": "High", "Key Risk": "Commercial grid conflicts"},
    ],
    "pon_capacity": [
        {"Parameter": "Technology Standard", "Value": "GPON / XGS-PON overlay capability"},
        {"Parameter": "144F Feeder Potential", "Value": "144 fibers × 32 split ratio = 4,608 residential endpoints max capacity"},
        {"Parameter": "Subdivision Density", "Value": "High local home density creates ideal metrics for high take-rate monetization"},
    ],
    "risk_assessment": [
        {"Risk": "Highly expansive clay soil", "Severity": "Medium", "Likelihood": "High", "Mitigation": "Maintain strict depth controls and verify conduit tensioning"},
        {"Risk": "TxDOT permit pushbacks", "Severity": "Medium", "Likelihood": "Medium", "Mitigation": "Engage regional utility coordinates early in design phase"},
        {"Risk": "Strike on existing neighborhood lines", "Severity": "High", "Likelihood": "Medium", "Mitigation": "Execute comprehensive hydro-potholing at every critical crossing"},
    ],
    "timeline": [
        {"Phase": "Pre-engineering & site-walk validation", "Duration": "2-3 weeks"},
        {"Phase": "Permitting submission track (City + TxDOT)", "Duration": "4-6 weeks (Run concurrently)"},
        {"Phase": "Civil construction (Micro-trenching & long-runs)", "Duration": "3-4 weeks"},
        {"Phase": "Boring operations (SH-5 Crossing focus)", "Duration": "1 week"},
        {"Phase": "Splicing, node testing, and fiber turn-up", "Duration": "2 weeks"},
        {"Phase": "Total Project Timeline to Active Service", "Duration": "~10-14 weeks"},
    ],
}

PRELOADED_ROUTE_ANALYSIS_TEXT = """
Fiber Route Analysis for the Anna, TX corridor is preloaded for frontend Q&A. The current recommendation is Route A: Willow Creek to West Crossing because it keeps linear mileage to roughly 1.55 miles, limits civil complexity compared with the southern perimeter option, and keeps the main engineering risk concentrated in the SH-5 directional bore. The analysis package includes location overview, route alternatives, obstructions, trenching and conduit details, existing infrastructure, fiber specifications, splice plan, power and equipment assumptions, permit timelines, cost comparison, PON capacity, risk assessment, and the end-to-end construction timeline.
""".strip()

CHAT_QA = [
    {
        "patterns": ["overview", "location overview", "show overview", "show the overview", "origin", "destination", "where does this route start"],
        "title": "Location Overview",
        "summary": "The analysis package is based on 109 Pagoda Dr to 313 Kelvinton Drive in Anna, Texas, with an estimated road distance of about 1.55 miles and a straight-line distance of about 1.10 miles.",
        "table_key": "location_overview",
        "recommendation": "Use the location overview when validating the corridor assumptions before detailed OSP engineering.",
    },
    {
        "patterns": ["best path", "recommended route", "which path", "route recommendation", "what is the optimal route for this location", "optimal route for this location", "optimal route"],
        "title": "Best Path Recommendation",
        "summary": "Proceed with Route A: Willow Creek to West Crossing Central Corridor. It is the most sensible route because it minimizes mileage, avoids the downtown commercial core, and preserves future expansion headroom along the Taylor Blvd link.",
        "bullets": [
            "Estimated road distance: ~1.55 mi",
            "Estimated total route cost: $63,500",
            "Primary engineering risk: SH-5 / N Powell Pkwy directional bore",
            "Best balance of distance, cost, and construction complexity",
        ],
        "table_key": "route_a",
        "recommendation": "Advance Route A into pre-engineering and permit coordination first, especially for the SH-5 crossing.",
    },
    {
        "patterns": ["what is the shortest path using existing ducts", "shortest path using existing ducts", "shortest path with existing ducts", "existing ducts shortest path"],
        "title": "Shortest Path Using Existing Ducts",
        "summary": "Route A is the shortest practical path that also maximizes available reuse in the current corridor model. It preserves the strongest duct reuse segment and still keeps total field complexity below the alternate route.",
        "bullets": [
            "Preferred corridor: Route A - Recommended",
            "Existing duct / reuse allocation: 410 ft",
            "Net new build required: 1,327 ft",
            "Road crossings: 1",
        ],
        "table_key": "routes",
        "recommendation": "Use Route A when the objective is minimizing new civil work while staying on the traced OSM corridor.",
    },
    {
        "patterns": ["show route a", "route a", "willow creek", "west crossing", "primary route"],
        "title": "Route A — Willow Creek to West Crossing",
        "summary": "Route A leaves Willow Creek via Pagoda Dr, transitions to Hackberry Dr / Taylor Blvd, crosses SH-5 by directional bore, and enters West Crossing for the final approach to Kelvinton Drive.",
        "table_key": "route_a",
        "recommendation": "Use this as the baseline alignment for cost modeling and permit scoping.",
    },
    {
        "patterns": ["show route b", "route b", "finley", "rosamond", "alternate route b", "provide an alternate resilient route", "alternate resilient route", "resilient route"],
        "title": "Route B — Finley Blvd East-West Axis",
        "summary": "Route B is a viable contingency if ROW issues appear on Taylor Blvd, but it adds civil length and raises the total build estimate.",
        "table_key": "route_b",
        "recommendation": "Hold Route B as a fallback alignment if municipal or utility conflicts block Route A.",
    },
    {
        "patterns": ["show route c", "route c", "white street", "southern perimeter", "fm 455"],
        "title": "Route C — Southern Perimeter",
        "summary": "Route C moves south to FM 455 and is the least attractive option because of commercial congestion, deeper bore requirements, and higher permitting complexity.",
        "table_key": "route_c",
        "recommendation": "Avoid Route C unless northern and central corridor options become infeasible.",
    },
    {
        "patterns": ["show bom", "bom", "materials", "bill of materials", "show materials"],
        "title": "Bill of Materials",
        "summary": "The synthetic BOM is now sized from the traced route length in route.geojson plus slack, structures, and one controlled bore.",
        "table_key": "bom",
        "recommendation": "Carry a 7% material contingency for conduit and restoration to absorb field adjustments.",
    },
    {
        "patterns": ["show risks", "show risk", "risk", "risks", "concerns", "issues", "what are the high-risk hotspots", "high-risk hotspots", "high risk hotspots", "risk hotspots"],
        "title": "Risk Register",
        "summary": "Overall route risk is medium, driven mainly by the SH-5 crossing, expansive clay soil behavior, and strike risk on existing neighborhood utilities.",
        "table_key": "risk_assessment",
        "recommendation": "Sequence TxDOT coordination, hydro-potholing, and depth/tension controls early in the engineering phase.",
    },
    {
        "patterns": ["show site survey", "site survey", "survey", "field notes", "observations"],
        "title": "Site Survey Summary",
        "summary": "The corridor survey indicates that both endpoints are serviceable, reuse opportunities are modest, and the main design decision centers on crossing the collector cleanly along the traced path.",
        "table_key": "survey",
        "recommendation": "Convert the road crossing note into a construction method statement in the final package.",
    },
    {
        "patterns": ["compare routes", "compare route", "show cost comparison", "cost comparison", "compare route costs", "compare", "route a vs route b", "route a route b route c", "alternate"],
        "title": "Route Comparison",
        "summary": "Route A is the lowest-cost and lowest-friction option, Route B is a practical backup, and Route C should only be considered if the other corridors are blocked.",
        "table_key": "cost_comparison",
        "recommendation": "Use the cost comparison table as the executive decision surface for route selection.",
    },
    {
        "patterns": ["show permits", "permit", "permits", "regulatory", "txdot", "811"],
        "title": "Permits & Regulatory",
        "summary": "The permitting path is manageable, but the SH-5 crossing drives the longest lead time because it requires TxDOT utility approval.",
        "table_key": "permits",
        "recommendation": "Run City of Anna ROW and TxDOT permit tracks in parallel to preserve schedule.",
    },
    {
        "patterns": ["show timeline", "timeline", "schedule", "construction timeline", "duration"],
        "title": "Construction Timeline",
        "summary": "The full program is estimated at roughly 10-14 weeks to active service, assuming permitting and field operations overlap where practical.",
        "table_key": "timeline",
        "recommendation": "Treat permitting as the critical path and front-load site-walk validation.",
    },
    {
        "patterns": ["show obstructions", "show obstruction", "obstruction", "obstructions", "crossings", "conflicts"],
        "title": "Route Obstructions Assessment",
        "summary": "The route is generally workable, but SH-5, adjacent rail/ROW constraints, and utility conflicts are the main engineering watch points.",
        "table_key": "obstructions",
        "recommendation": "Use the obstruction table to sequence potholing and bore design reviews.",
    },
    {
        "patterns": ["show trenching", "show civil work", "trench", "trenching", "civil work", "conduit", "soil", "how much trenching is required", "trenching required", "how much trenching"],
        "title": "Trenching & Civil Work",
        "summary": "The planned build uses micro-trenching in neighborhood corridors and directional boring at major crossings, with conduit and trench depth assumptions already defined.",
        "bullets": [
            "Estimated new trench / build length: 1,327 ft",
            "Existing reuse segment: 410 ft",
            "Directional bore allocation in BOM: 140 ft",
            "Primary trench method: micro-trenching with one controlled bore crossing",
        ],
        "table_key": "civil_work",
        "recommendation": "Carry the Houston Black Clay soil note into the bore methodology package.",
    },
    {
        "patterns": ["show existing infrastructure", "existing infrastructure", "available infrastructure", "att&t", "optimum", "utility poles"],
        "title": "Existing Infrastructure",
        "summary": "Existing carrier and utility infrastructure is present in the market, but the deployment still assumes overbuild and conflict verification.",
        "table_key": "existing_infrastructure",
        "recommendation": "Use potholing and record review to validate real conflict points before bore mobilization.",
    },
    {
        "patterns": ["show fiber specs", "show fiber spec", "fiber spec", "cable spec", "specification", "otdr"],
        "title": "Fiber Cable Specification",
        "summary": "The route package assumes a 144F feeder, subdivision distribution loops, toneable drop cable, fusion splicing, and bi-directional OTDR testing.",
        "table_key": "fiber_spec",
        "recommendation": "Use the testing requirement as part of the acceptance checklist and turn-up criteria.",
    },
    {
        "patterns": ["show splice plan", "splice", "splice plan", "joint plan", "sp-01"],
        "title": "Splice & Joint Plan",
        "summary": "The splice plan defines four control points from Pagoda egress through the Taylor/Powell transition and into the destination handoff.",
        "table_key": "splice_plan",
        "recommendation": "Keep SP-02 and SP-03 as the main vault-based control nodes in detailed design.",
    },
    {
        "patterns": ["show power and equipment", "show power", "show equipment", "power", "equipment", "fdh power", "splitter ratio", "olt"],
        "title": "Power & Equipment",
        "summary": "The architecture assumes passive FDH elements, regional OLT support, 1:32 split ratios, and a very favorable optical budget for the overall path length.",
        "table_key": "power_equipment",
        "recommendation": "Use the passive FDH assumption to simplify field power dependencies in the neighborhood corridor.",
    },
    {
        "patterns": ["show pon capacity", "show capacity", "capacity", "pon", "gpon", "xgs-pon", "endpoint capacity"],
        "title": "PON Architecture & Capacity",
        "summary": "The feeder and splitter design leaves strong capacity headroom for nearby developments and future overlay demand.",
        "table_key": "pon_capacity",
        "recommendation": "Keep the 144F framework as the preferred feeder size to preserve future monetization flexibility.",
    },
]

SUPPORTED_QUESTIONS = [
    "What is the optimal route for this location?",
    "What is the shortest path using existing ducts?",
    "What are the high-risk hotspots?",
    "How much trenching is required?",
    "Provide an alternate resilient route.",
    "Show the location overview.",
    "What is the best path?",
    "Show Route A.",
    "Show Route B.",
    "Show Route C.",
    "Show me the BOM.",
    "What are the main risks?",
    "Show permits and timeline.",
    "Show cost comparison.",
    "Summarize the site survey.",
    "Compare Route A, B, and C.",
]
