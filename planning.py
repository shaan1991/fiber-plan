from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd

from data import BOM_ITEMS, CHAT_QA, PROJECT, RISK_ITEMS, ROUTE_OPTIONS, SURVEY_FINDINGS


def build_bom_dataframe() -> pd.DataFrame:
    rows = []
    for item in BOM_ITEMS:
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
            for item in SURVEY_FINDINGS
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
            for item in RISK_ITEMS
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
            for item in ROUTE_OPTIONS
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
    for route in ROUTE_OPTIONS:
        candidate = dict(route)
        candidate["score"] = round(score_route(route), 1)
        scored.append(candidate)

    best = min(scored, key=lambda route: route["score"])
    return {
        "selected_route_id": best["route_id"],
        "selected_route_name": best["route_name"],
        "distance_ft": best["distance_ft"],
        "estimated_new_build_ft": best["new_build_ft"],
        "risk_score": sum(item["score"] for item in RISK_ITEMS) // len(RISK_ITEMS),
        "estimated_capex": best["estimated_capex"],
        "reason_summary": best["narrative"],
        "score": best["score"],
    }


def get_dashboard_metrics() -> dict[str, str]:
    recommendation = get_recommendation()
    total_material_cost = build_bom_dataframe()["Extended Cost ($)"].sum()
    return {
        "Preferred Route": recommendation["selected_route_name"],
        "Existing Fiber Reuse": f"{ROUTE_OPTIONS[0]['reuse_ft']:,} ft",
        "New Build": f"{recommendation['estimated_new_build_ft']:,} ft",
        "Risk Posture": f"{recommendation['risk_score']} / 100",
        "Material Cost": f"${total_material_cost:,.0f}",
        "Survey Window": PROJECT["survey_window"],
    }


def get_chat_tables() -> dict[str, pd.DataFrame]:
    return {
        "bom": build_bom_dataframe(),
        "survey": build_survey_dataframe(),
        "risks": build_risk_dataframe(),
        "routes": build_route_dataframe(),
    }


def find_chat_response(question: str) -> dict[str, Any]:
    normalized = question.lower().strip()
    for answer in CHAT_QA:
        if any(pattern in normalized for pattern in answer["patterns"]):
            payload = dict(answer)
            table_key = payload.get("table_key")
            if table_key:
                payload["table"] = get_chat_tables()[table_key]
            return payload

    return {
        "title": "Planning Assistant",
        "summary": (
            "I can help with the recommended route, BOM, risk register, site survey summary, "
            "or a Route A vs Route B comparison."
        ),
        "bullets": [
            "Try: What is the best path?",
            "Try: Show me the BOM.",
            "Try: What are the main risks?",
        ],
        "recommendation": "Use one of the supported planning prompts to keep the demo focused.",
    }


def dataframe_to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(index=False).encode("utf-8")


def dataframe_to_excel_bytes(dataframe_map: dict[str, pd.DataFrame]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, dataframe in dataframe_map.items():
            dataframe.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    return output.getvalue()
