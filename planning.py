from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd

import data

DEFAULT_ROUTE_ANALYSIS_TABLES = {
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
    "permits": [
        {"Requirement": "City of Anna ROW Permit", "Status": "Required for all neighborhood trenching", "Timeline": "2-3 weeks"},
        {"Requirement": "TxDOT Utility Permit", "Status": "Required for SH-5 / Powell Pkwy directional bore", "Timeline": "4-6 weeks"},
        {"Requirement": "Texas Central / Railroad Crossing Permit", "Status": "May apply depending on parallel track boundaries", "Timeline": "6-8 weeks"},
        {"Requirement": "Texas 811 Locate Notice", "Status": "Mandatory requirement before any ground penetration", "Timeline": "48-72 hours"},
    ],
    "timeline": [
        {"Phase": "Pre-engineering & site-walk validation", "Duration": "2-3 weeks"},
        {"Phase": "Permitting submission track (City + TxDOT)", "Duration": "4-6 weeks (Run concurrently)"},
        {"Phase": "Civil construction (Micro-trenching & long-runs)", "Duration": "3-4 weeks"},
        {"Phase": "Boring operations (SH-5 Crossing focus)", "Duration": "1 week"},
        {"Phase": "Splicing, node testing, and fiber turn-up", "Duration": "2 weeks"},
        {"Phase": "Total Project Timeline to Active Service", "Duration": "~10-14 weeks"},
    ],
    "cost_comparison": [
        {"Route": "A: Willow Creek to West Crossing (BEST)", "Distance": "~1.55 mi", "Cost": "$63,500", "Cost/mi": "~$40,967/mi", "Complexity": "Medium", "Key Risk": "SH-5 Highway Crossing"},
        {"Route": "B: Finley Blvd Extension", "Distance": "~1.80 mi", "Cost": "$73,500", "Cost/mi": "~$40,833/mi", "Complexity": "Medium", "Key Risk": "Longer civil build distance"},
        {"Route": "C: Southern Perimeter (White St)", "Distance": "~1.80 mi", "Cost": "$80,500", "Cost/mi": "~$44,722/mi", "Complexity": "High", "Key Risk": "Commercial grid conflicts"},
    ],
    "risk_assessment": [
        {"Risk": "Highly expansive clay soil", "Severity": "Medium", "Likelihood": "High", "Mitigation": "Maintain strict depth controls and verify conduit tensioning"},
        {"Risk": "TxDOT permit pushbacks", "Severity": "Medium", "Likelihood": "Medium", "Mitigation": "Engage regional utility coordinates early in design phase"},
        {"Risk": "Strike on existing neighborhood lines", "Severity": "High", "Likelihood": "Medium", "Mitigation": "Execute comprehensive hydro-potholing at every critical crossing"},
    ],
}

REQUIRED_ROUTE_ANALYSIS_KEYS = [
    "location_overview",
    "route_a",
    "route_b",
    "route_c",
    "permits",
    "timeline",
    "cost_comparison",
    "risk_assessment",
]

DEFAULT_CHAT_QA = [
    {
        "patterns": ["overview", "location overview", "show overview", "show the overview", "origin", "destination", "where does this route start"],
        "title": "Location Overview",
        "summary": "The analysis package is based on 109 Pagoda Dr to 313 Kelvinton Drive in Anna, Texas, with an estimated road distance of about 1.55 miles and a straight-line distance of about 1.10 miles.",
        "table_key": "location_overview",
        "recommendation": "Use the location overview when validating the corridor assumptions before detailed OSP engineering.",
    },
    {
        "patterns": ["best path", "recommended route", "which path", "route recommendation"],
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
        "patterns": ["show route a", "route a", "willow creek", "west crossing", "primary route"],
        "title": "Route A — Willow Creek to West Crossing",
        "summary": "Route A leaves Willow Creek via Pagoda Dr, transitions to Hackberry Dr / Taylor Blvd, crosses SH-5 by directional bore, and enters West Crossing for the final approach to Kelvinton Drive.",
        "table_key": "route_a",
        "recommendation": "Use this as the baseline alignment for cost modeling and permit scoping.",
    },
    {
        "patterns": ["show route b", "route b", "finley", "rosamond", "alternate route b"],
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
        "summary": "The BOM is sized around the recommended corridor, conduit, structures, and controlled bore activity.",
        "table_key": "bom",
        "recommendation": "Carry a 7% material contingency for conduit and restoration to absorb field adjustments.",
    },
    {
        "patterns": ["show risks", "show risk", "risk", "risks", "concerns", "issues"],
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
        "patterns": ["show trenching", "show civil work", "trench", "trenching", "civil work", "conduit", "soil"],
        "title": "Trenching & Civil Work",
        "summary": "The planned build uses micro-trenching in neighborhood corridors and directional boring at major crossings, with conduit and trench depth assumptions already defined.",
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


def build_bom_dataframe() -> pd.DataFrame:
    rows = []
    for item in data.BOM_ITEMS:
        extended_cost = item["quantity"] * item["unit_cost"]
        rows.append(
            {
                "Category": item["category"],
                "Item": item["item"],
                "Qty": item["quantity"],
                "Unit": item["unit"],
                "Unit Cost ($)": item["unit_cost"],
                "Extended Cost ($)": round(extended_cost, 2),
            }
        )
    return pd.DataFrame(rows)


def build_survey_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Observation": item["name"],
                "Category": item["category"],
                "Status": item["status"],
                "Priority": item["priority"],
                "Details": item["details"],
            }
            for item in data.SURVEY_FINDINGS
        ]
    )


def build_risk_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Risk": item["title"],
                "Severity": item["severity"],
                "Score": item["score"],
                "Owner": item["owner"],
                "Mitigation": item["mitigation"],
            }
            for item in data.RISK_ITEMS
        ]
    )


def build_route_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Route": item["route_name"],
                "Distance (ft)": item["distance_ft"],
                "Reuse (ft)": item["reuse_ft"],
                "New Build (ft)": item["new_build_ft"],
                "Road Crossings": item["road_crossings"],
                "Risk Count": item["risk_count"],
                "Est. Capex ($)": item["estimated_capex"],
            }
            for item in data.ROUTE_OPTIONS
        ]
    )


def score_route(route: dict[str, Any]) -> float:
    return (
        route["distance_ft"] * 0.004
        + route["new_build_ft"] * 0.01
        + route["road_crossings"] * 12
        + route["risk_count"] * 7
        + route["complexity"] * 10
    )


def get_recommendation() -> dict[str, Any]:
    scored = []
    for route in data.ROUTE_OPTIONS:
        candidate = dict(route)
        candidate["score"] = round(score_route(route), 1)
        scored.append(candidate)

    best = min(scored, key=lambda route: route["score"])
    return {
        "selected_route_id": best["route_id"],
        "selected_route_name": best["route_name"],
        "distance_ft": best["distance_ft"],
        "estimated_new_build_ft": best["new_build_ft"],
        "risk_score": sum(item["score"] for item in data.RISK_ITEMS) // len(data.RISK_ITEMS),
        "estimated_capex": best["estimated_capex"],
        "reason_summary": best["narrative"],
        "score": best["score"],
    }


def get_dashboard_metrics() -> dict[str, str]:
    recommendation = get_recommendation()
    total_material_cost = build_bom_dataframe()["Extended Cost ($)"].sum()
    return {
        "Preferred Route": recommendation["selected_route_name"],
        "Existing Fiber Reuse": f"{data.ROUTE_OPTIONS[0]['reuse_ft']:,} ft",
        "New Build": f"{recommendation['estimated_new_build_ft']:,} ft",
        "Risk Posture": f"{recommendation['risk_score']} / 100",
        "Material Cost": f"${total_material_cost:,.0f}",
        "Survey Window": data.PROJECT["survey_window"],
    }


def get_chat_tables() -> dict[str, pd.DataFrame]:
    tables = {
        "bom": build_bom_dataframe(),
        "survey": build_survey_dataframe(),
        "risks": build_risk_dataframe(),
        "routes": build_route_dataframe(),
    }
    route_analysis_tables = getattr(data, "ROUTE_ANALYSIS_TABLES", {}) or {}
    merged_route_analysis_tables = dict(DEFAULT_ROUTE_ANALYSIS_TABLES)
    merged_route_analysis_tables.update(route_analysis_tables)
    for required_key in REQUIRED_ROUTE_ANALYSIS_KEYS:
        merged_route_analysis_tables.setdefault(required_key, DEFAULT_ROUTE_ANALYSIS_TABLES[required_key])
    for table_key, rows in merged_route_analysis_tables.items():
        tables[table_key] = pd.DataFrame(rows)
    return tables


def find_chat_response(question: str) -> dict[str, Any]:
    normalized = question.lower().strip()
    chat_qa = getattr(data, "CHAT_QA", None) or DEFAULT_CHAT_QA
    for answer in chat_qa:
        if any(pattern in normalized for pattern in answer["patterns"]):
            payload = dict(answer)
            table_key = payload.get("table_key")
            if table_key:
                payload["table"] = get_chat_tables().get(table_key, pd.DataFrame())
            return payload

    return {
        "title": "Planning Assistant",
        "summary": (
            "I can help with route overview, Route A/B/C analysis, cost comparison, permits, "
            "timeline, risks, fiber specifications, splice planning, BOM, and site survey details."
        ),
        "bullets": [
            "Try: Show the location overview.",
            "Try: What is the best path?",
            "Try: Show permits and timeline.",
        ],
        "recommendation": "Use one of the supported planning prompts to navigate the preloaded route analysis package.",
    }


def dataframe_to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(index=False).encode("utf-8")


def dataframe_to_excel_bytes(dataframe_map: dict[str, pd.DataFrame]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, dataframe in dataframe_map.items():
            dataframe.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    return output.getvalue()
