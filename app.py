from __future__ import annotations

from datetime import datetime

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

import data
from planning import build_bom_dataframe, build_risk_dataframe, build_route_dataframe, build_survey_dataframe, find_chat_response, get_chat_tables, get_recommendation
from reporting import generate_pdf_report


st.set_page_config(
    page_title="FiberPlanAI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


CUSTOM_CSS = """
<style>
    .stApp {
        background: #f6f6f6;
        color: #111111;
    }
    .block-container {
        max-width: 1880px;
        padding-top: 0.65rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    [data-testid="stMetricValue"] {
        font-weight: 800;
    }
    .fp-topbar {
        background: #ffffff;
        border: 1px solid #e9e9e9;
        border-radius: 16px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 8px 24px rgba(17, 17, 17, 0.04);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .fp-brand {
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }
    .fp-brand-icon {
        width: 30px;
        height: 30px;
        border-radius: 8px;
        background: #e60000;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        font-weight: 800;
    }
    .fp-brand-title {
        font-weight: 800;
        font-size: 1rem;
        color: #161616;
    }
    .fp-brand-subtitle {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #8a8a8a;
        margin-top: 0.1rem;
    }
    .fp-pill-wrap {
        display: flex;
        gap: 0.45rem;
    }
    .fp-pill {
        border: 1px solid #e7e7e7;
        background: #ffffff;
        border-radius: 999px;
        padding: 0.28rem 0.55rem;
        font-size: 0.67rem;
        color: #666666;
    }
    .fp-section-label {
        font-size: 0.69rem;
        font-weight: 800;
        letter-spacing: 0.11em;
        text-transform: uppercase;
        color: #7e7e7e;
        margin-bottom: 0.45rem;
    }
    .fp-address-tag {
        color: #e60000;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    .fp-address-value {
        color: #202020;
        font-size: 0.92rem;
        line-height: 1.4;
    }
    .fp-map-actions {
        display: flex;
        gap: 0.6rem;
        margin-bottom: 0.7rem;
    }
    .fp-map-pill {
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        font-size: 0.78rem;
        color: #555555;
        font-weight: 600;
    }
    .fp-map-chips-label {
        font-size: 0.69rem;
        font-weight: 800;
        letter-spacing: 0.11em;
        text-transform: uppercase;
        color: #8a8a8a;
        margin-bottom: 0.4rem;
    }
    .fp-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
        background: #242833;
        padding: 0.5rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
    }
    .fp-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: #ffffff;
        border-radius: 8px;
        border: 1px solid #dfe3ea;
        color: #2d2d2d;
        font-size: 0.76rem;
        font-weight: 600;
        padding: 0.35rem 0.55rem;
    }
    .fp-map-footer {
        display: grid;
        grid-template-columns: 1fr 1fr 1.35fr;
        gap: 0.55rem;
        margin-top: 0.6rem;
    }
    .fp-map-footer-card {
        background: #ffffff;
        border: 1px solid #ececec;
        border-radius: 10px;
        padding: 0.65rem 0.7rem;
        font-size: 0.73rem;
        color: #575757;
    }
    .fp-map-footer-title {
        color: #6a6a6a;
        font-size: 0.62rem;
        font-weight: 800;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }
    .fp-assistant-header {
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #6f6f6f;
        margin-bottom: 0.75rem;
    }
    .fp-chat-user {
        background: #242833;
        color: #ffffff;
        padding: 0.75rem 0.9rem;
        border-radius: 18px 18px 8px 18px;
        width: fit-content;
        max-width: 92%;
        margin: 0.2rem 0 0.8rem auto;
    }
    .fp-chat-ai {
        background: #ffffff;
        border: 1px solid #ececec;
        border-radius: 14px;
        padding: 0.8rem 0.9rem;
        margin-bottom: 0.8rem;
    }
    .fp-chat-badge {
        display: inline-block;
        background: #f1f1f1;
        color: #555555;
        border-radius: 999px;
        padding: 0.18rem 0.5rem;
        font-size: 0.66rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.45rem;
    }
    .fp-subtle {
        color: #6f6f6f;
        font-size: 0.78rem;
    }
    .fp-summary-note {
        font-size: 0.84rem;
        color: #505050;
        line-height: 1.5;
    }
</style>
"""

FALLBACK_ROUTE_POINTS = [
    (33.35094, -96.55949),
    (33.35098, -96.55948),
    (33.35110, -96.55943),
    (33.35103, -96.55910),
    (33.35098, -96.55881),
    (33.35095, -96.55847),
    (33.35092, -96.55684),
    (33.35134, -96.55683),
    (33.35147, -96.55683),
    (33.35148, -96.55735),
    (33.35291, -96.55729),
]

CHAT_STATE_VERSION = 1
SURVEY_IMAGE_PATHS = [
    "/Users/shahnawaazshaikh/Downloads/Before-1.png",
    "/Users/shahnawaazshaikh/Downloads/Before-2.png",
    "/Users/shahnawaazshaikh/Downloads/After-1.png",
    "/Users/shahnawaazshaikh/Downloads/After-2.png",
]
DEFAULT_PRELOADED_ROUTE_ANALYSIS_TEXT = """
Fiber Route Analysis for the Anna, TX corridor is preloaded for frontend Q&A. The current recommendation is Route A: Willow Creek to West Crossing because it keeps linear mileage to roughly 1.55 miles, limits civil complexity compared with the southern perimeter option, and keeps the main engineering risk concentrated in the SH-5 directional bore. The analysis package includes location overview, route alternatives, obstructions, trenching and conduit details, existing infrastructure, fiber specifications, splice plan, power and equipment assumptions, permit timelines, cost comparison, PON capacity, risk assessment, and the end-to-end construction timeline.
""".strip()
ENDPOINT_OPTIONS = {
    "121 Pagoda Drive, Anna, TX 75409": "121 Pagoda Drive, Anna, TX 75409",
    "313 Kelvinton Drive, Anna, TX 75409": "313 Kelvinton Drive, Anna, TX 75409",
    "1250 W Park Blvd, Plano, TX 75075": "1250 W Park Blvd, Plano, TX 75075",
    "8200 Independence Pkwy, Plano, TX 75025": "8200 Independence Pkwy, Plano, TX 75025",
}
HANDHOLE_POINTS = [
    {"name": "Handhole HH-01", "lat": 33.35099, "lon": -96.55892},
    {"name": "Handhole HH-02", "lat": 33.35100, "lon": -96.55795},
    {"name": "Handhole HH-03", "lat": 33.35146, "lon": -96.55684},
]


def initialize_state() -> None:
    if st.session_state.get("chat_state_version") != CHAT_STATE_VERSION:
        st.session_state.messages = []
        st.session_state.chat_state_version = CHAT_STATE_VERSION
    elif "messages" not in st.session_state:
        st.session_state.messages = []
    if "show_streamlit_header" not in st.session_state:
        st.session_state.show_streamlit_header = False
    if "email_sent" not in st.session_state:
        st.session_state.email_sent = False
    if "last_email_meta" not in st.session_state:
        st.session_state.last_email_meta = {}


def render_dynamic_css() -> None:
    if st.session_state.get("show_streamlit_header"):
        return
    st.markdown(
        """
        <style>
            .stAppHeader,
            [data-testid="stHeader"],
            [data-testid="stToolbar"],
            [data-testid="stDecoration"] {
                display: none !important;
            }
            .block-container {
                padding-top: 0.25rem !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_timeline_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Phase": "OTDR inspection (existing segment)", "Duration": "2 days"},
            {"Phase": "Engineering & permitting", "Duration": "3-4 weeks"},
            {"Phase": "Material procurement", "Duration": "1-2 weeks"},
            {"Phase": "Construction - bore / pull", "Duration": "1-2 days"},
            {"Phase": "Splicing & acceptance testing", "Duration": "1 day"},
            {"Phase": "Total", "Duration": "~6-8 weeks"},
        ]
    )


def get_display_route_segments() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    existing_points = getattr(data, "DISPLAY_EXISTING_ROUTE_POINTS", None)
    proposed_points = getattr(data, "DISPLAY_PROPOSED_ROUTE_POINTS", None)
    if existing_points and proposed_points:
        return existing_points, proposed_points

    route_points = getattr(data, "ACTUAL_ROUTE_POINTS", None) or FALLBACK_ROUTE_POINTS
    if len(route_points) < 2:
        route_points = FALLBACK_ROUTE_POINTS
    split_index = min(getattr(data, "ROUTE_SPLIT_INDEX", 5), max(len(route_points) - 1, 1))
    existing_points = route_points[: split_index + 1]
    proposed_points = route_points[split_index:]
    if len(existing_points) < 2:
        existing_points = route_points[:2]
    if len(proposed_points) < 2:
        proposed_points = route_points[-2:]
    return existing_points, proposed_points


def get_safe_map_center() -> dict[str, float]:
    center = getattr(data, "MAP_CENTER", None)
    if isinstance(center, dict) and "lat" in center and "lon" in center:
        return center
    points = getattr(data, "ACTUAL_ROUTE_POINTS", None) or FALLBACK_ROUTE_POINTS
    return {
        "lat": sum(point[0] for point in points) / len(points),
        "lon": sum(point[1] for point in points) / len(points),
    }


def get_safe_endpoints() -> dict[str, object]:
    endpoints = getattr(data, "ENDPOINTS", None)
    if endpoints and "start" in endpoints and "end" in endpoints:
        return endpoints
    class _Endpoint:
        def __init__(self, address: str, lat: float, lon: float):
            self.address = address
            self.lat = lat
            self.lon = lon
    return {
        "start": _Endpoint("121 Pagoda Drive, Anna, TX 75409", FALLBACK_ROUTE_POINTS[0][0], FALLBACK_ROUTE_POINTS[0][1]),
        "end": _Endpoint("313 Kelvinton Drive, Anna, TX 75409", FALLBACK_ROUTE_POINTS[-1][0], FALLBACK_ROUTE_POINTS[-1][1]),
    }


def build_map() -> folium.Map:
    existing_route_points, proposed_route_points = get_display_route_segments()
    safe_center = get_safe_map_center()
    safe_endpoints = get_safe_endpoints()
    route_map = folium.Map(
        location=[safe_center["lat"], safe_center["lon"]],
        zoom_start=17,
        tiles=None,
        control_scale=True,
        zoom_control=True,
    )

    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attr='&copy; OpenStreetMap contributors &copy; CARTO',
        name="CARTO Positron",
        control=False,
    ).add_to(route_map)

    if len(existing_route_points) >= 2:
        folium.PolyLine(
            locations=existing_route_points,
            color="#34c759",
            weight=5,
            opacity=0.95,
            tooltip="Existing fiber segment",
        ).add_to(route_map)

    if len(proposed_route_points) >= 2:
        folium.PolyLine(
            locations=proposed_route_points,
            color="#f6a623",
            weight=4,
            opacity=0.95,
            dash_array="8, 6",
            tooltip="Proposed fiber segment",
        ).add_to(route_map)

    folium.Marker(
        [safe_endpoints["start"].lat, safe_endpoints["start"].lon],
        tooltip=f"Start point: {safe_endpoints['start'].address}",
        popup=f"<b>Start</b><br>{safe_endpoints['start'].address}",
        icon=folium.DivIcon(
            html="""
            <div style="display:flex;align-items:center;justify-content:center;width:24px;height:24px;
                        background:#73b62c;border:3px solid white;border-radius:999px;
                        box-shadow:0 2px 10px rgba(0,0,0,0.20);color:white;font-size:12px;font-weight:900;">▶</div>
            """
        ),
    ).add_to(route_map)
    folium.Marker(
        [safe_endpoints["start"].lat - 0.00018, safe_endpoints["start"].lon + 0.00009],
        tooltip="FDH",
        icon=folium.DivIcon(
            html="""
            <div style="display:flex;align-items:center;justify-content:center;width:16px;height:16px;
                        background:#1f8fff;border:2px solid white;border-radius:4px;
                        box-shadow:0 1px 8px rgba(0,0,0,0.18);color:white;font-size:10px;font-weight:800;">F</div>
            """
        ),
    ).add_to(route_map)
    folium.Marker(
        [safe_endpoints["end"].lat, safe_endpoints["end"].lon],
        tooltip=f"End point: {safe_endpoints['end'].address}",
        popup=f"<b>End</b><br>{safe_endpoints['end'].address}",
        icon=folium.DivIcon(
            html="""
            <div style="display:flex;align-items:center;justify-content:center;width:24px;height:24px;
                        background:#ef6d3c;border:3px solid white;border-radius:999px;
                        box-shadow:0 2px 10px rgba(0,0,0,0.20);color:white;font-size:12px;font-weight:900;">⚑</div>
            """
        ),
    ).add_to(route_map)
    folium.Marker(
        [safe_endpoints["end"].lat - 0.00015, safe_endpoints["end"].lon + 0.00010],
        tooltip="FDH",
        icon=folium.DivIcon(
            html="""
            <div style="display:flex;align-items:center;justify-content:center;width:16px;height:16px;
                        background:#1f8fff;border:2px solid white;border-radius:4px;
                        box-shadow:0 1px 8px rgba(0,0,0,0.18);color:white;font-size:10px;font-weight:800;">F</div>
            """
        ),
    ).add_to(route_map)

    point_specs = [
        {"color": "#b255d4", "symbol": "◆", "lat": data.SURVEY_FINDINGS[0]["lat"] + 0.00018, "lon": data.SURVEY_FINDINGS[0]["lon"] + 0.00005, "tooltip": "Survey marker"},
        {"color": "#8f8f8f", "symbol": "⬤", "lat": proposed_route_points[0][0], "lon": proposed_route_points[0][1], "tooltip": "Manhole MH-01"},
        {"color": "#b255d4", "symbol": "◆", "lat": data.SURVEY_FINDINGS[1]["lat"] + 0.00010, "lon": data.SURVEY_FINDINGS[1]["lon"] - 0.00015, "tooltip": "Survey marker"},
        {"color": "#8f8f8f", "symbol": "⬤", "lat": proposed_route_points[min(2, len(proposed_route_points) - 1)][0], "lon": proposed_route_points[min(2, len(proposed_route_points) - 1)][1], "tooltip": "Manhole MH-02"},
        {"color": "#b255d4", "symbol": "◆", "lat": data.SURVEY_FINDINGS[2]["lat"], "lon": data.SURVEY_FINDINGS[2]["lon"] - 0.00008, "tooltip": "Survey marker"},
        {"color": "#f45d48", "symbol": "⊗", "lat": data.RISK_ITEMS[1]["lat"] - 0.00120, "lon": data.RISK_ITEMS[1]["lon"] - 0.00035, "tooltip": "Risk point"},
        {"color": "#19a0aa", "symbol": "●", "lat": data.SURVEY_FINDINGS[3]["lat"] - 0.00110, "lon": data.SURVEY_FINDINGS[3]["lon"] + 0.00055, "tooltip": "Vault"},
    ]
    for point in point_specs:
        folium.Marker(
            [point["lat"], point["lon"]],
            tooltip=point["tooltip"],
            icon=folium.DivIcon(
                html=f"""
                <div style="display:flex;align-items:center;justify-content:center;width:18px;height:18px;
                            color:{point["color"]};font-size:13px;font-weight:800;text-shadow:0 0 2px white;">{point["symbol"]}</div>
                """
            ),
        ).add_to(route_map)

    for handhole in HANDHOLE_POINTS:
        folium.Marker(
            [handhole["lat"], handhole["lon"]],
            tooltip=handhole["name"],
            icon=folium.DivIcon(
                html="""
                <div style="display:flex;align-items:center;justify-content:center;width:16px;height:16px;
                            background:#20b7b6;border:2px solid white;border-radius:999px;
                            box-shadow:0 1px 8px rgba(0,0,0,0.18);"></div>
                """
            ),
        ).add_to(route_map)

    route_map.fit_bounds([*existing_route_points, *proposed_route_points], padding=(20, 20))
    return route_map


def render_topbar() -> None:
    st.markdown(
        """
        <div class="fp-topbar">
            <div class="fp-brand">
                <div class="fp-brand-icon">■</div>
                <div>
                    <div class="fp-brand-title">FiberPlanAI</div>
                    <div class="fp-brand-subtitle">Map Viewer</div>
                </div>
            </div>
            <div class="fp-pill-wrap">
                <div class="fp-pill">LIVE</div>
                <div class="fp-pill">ANNA, TX</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_left_rail() -> None:
    recommendation = get_recommendation()
    safe_endpoints = get_safe_endpoints()
    with st.container(border=True):
        st.markdown('<div class="fp-section-label">Route Endpoints</div>', unsafe_allow_html=True)
        from_options = list(ENDPOINT_OPTIONS.keys())
        to_options = list(ENDPOINT_OPTIONS.keys())
        st.selectbox(
            "From",
            from_options,
            index=from_options.index(safe_endpoints["start"].address) if safe_endpoints["start"].address in from_options else 0,
            key="from_address_select",
        )
        st.selectbox(
            "To",
            to_options,
            index=to_options.index(safe_endpoints["end"].address) if safe_endpoints["end"].address in to_options else min(1, len(to_options) - 1),
            key="to_address_select",
        )
        st.toggle("Show Streamlit Header", key="show_streamlit_header")

    with st.container(border=True):
        st.markdown('<div class="fp-section-label">Layers & Assets</div>', unsafe_allow_html=True)
        metric_col_1, metric_col_2 = st.columns(2)
        with metric_col_1:
            st.metric("Sites", "4")
            st.metric("Risks", "3")
        with metric_col_2:
            st.metric("Assets", "8")
            st.metric("Routes", "2")

    with st.container(border=True):
        st.markdown('<div class="fp-section-label">Corridor Summary</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="fp-summary-note">
                Preferred route: <b>{recommendation["selected_route_name"]}</b><br/><br/>
                Distance: <b>{recommendation["distance_ft"]:,} ft</b><br/>
                New build: <b>{recommendation["estimated_new_build_ft"]:,} ft</b><br/>
                Capex: <b>${recommendation["estimated_capex"]:,.0f}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_map_workspace() -> None:
    chips = ["FDH", "Handhole", "Cabinet", "Vault", "Pole", "Splice Closure", "Fiber Cable", "Duct"]
    st.markdown(
        """
        <div class="fp-map-actions">
            <div class="fp-map-pill">+ Route</div>
            <div class="fp-map-pill">✕ Clear</div>
        </div>
        <div class="fp-map-chips-label">Infrastructure Assets</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="fp-chip-row">' + "".join([f'<div class="fp-chip">{chip} ×</div>' for chip in chips]) + "</div>",
        unsafe_allow_html=True,
    )
    st_folium(build_map(), use_container_width=True, height=720, returned_objects=[])
    st.markdown(
        """
        <div class="fp-map-footer">
            <div class="fp-map-footer-card">
                <div class="fp-map-footer-title">Site Risk Level</div>
                High | Medium | Low
            </div>
            <div class="fp-map-footer-card">
                <div class="fp-map-footer-title">Infrastructure Assets</div>
                FDH | Handhole | Cabinet | Vault | Pole
            </div>
            <div class="fp-map-footer-card">
                <div class="fp-map-footer-title">Risk Classification Criteria</div>
                High: utility span / road crossing. Medium: vegetation / offset. Low: clear ROW / direct placement.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_default_assistant_content() -> None:
    recommendation = get_recommendation()
    route_analysis_tables = get_chat_tables()
    preloaded_route_analysis_text = getattr(data, "PRELOADED_ROUTE_ANALYSIS_TEXT", DEFAULT_PRELOADED_ROUTE_ANALYSIS_TEXT)
    location_overview_df = route_analysis_tables.get("location_overview", pd.DataFrame([{"Parameter": "Origin", "Value": "109 Pagoda Dr, Anna, TX 75409"}, {"Parameter": "Destination", "Value": "313 Kelvinton Drive, Anna, TX 75409"}]))
    risk_assessment_df = route_analysis_tables.get("risk_assessment", build_risk_dataframe()[["Risk", "Severity", "Mitigation"]])
    timeline_df = route_analysis_tables.get("timeline", build_timeline_dataframe())
    route_a_df = route_analysis_tables.get("route_a", build_route_dataframe())

    with st.container(border=True):
        st.subheader("Fiber Route Analysis")
        st.markdown(preloaded_route_analysis_text)
        st.dataframe(location_overview_df, use_container_width=True, hide_index=True)

    with st.container(border=True):
        st.subheader("Risk Summary")
        st.dataframe(risk_assessment_df, use_container_width=True, hide_index=True)

    with st.container(border=True):
        st.subheader("Timeline")
        st.dataframe(timeline_df, use_container_width=True, hide_index=True)

    with st.container(border=True):
        st.subheader("Best Path Recommendation")
        st.markdown(
            f"""
            <div class="fp-summary-note">
                <b>{recommendation["selected_route_name"]}</b> remains the preferred corridor because it follows the traced OSM path
                and maintains the strongest risk-adjusted construction profile.<br/><br/>
                Distance: <b>{recommendation["distance_ft"]:,} ft</b><br/>
                New build: <b>{recommendation["estimated_new_build_ft"]:,} ft</b><br/>
                Capex: <b>${recommendation["estimated_capex"]:,.0f}</b><br/>
                Risk score: <b>{recommendation["risk_score"]} / 100</b>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(route_a_df, use_container_width=True, hide_index=True)

    with st.container(border=True):
        st.subheader("Site Survey")
        st.markdown(
            """
            The preloaded site survey confirms a viable exterior fiber entry path, a clean telecom room transition,
            and a ready switch-room environment for final termination and cutover. The annotated photos below capture
            the field condition before installation and the target post-installation state for entry, rack, cooling,
            and power readiness.
            """
        )
        st.markdown("Before installation")
        before_col_1, before_col_2 = st.columns(2)
        with before_col_1:
            st.image(SURVEY_IMAGE_PATHS[0], use_container_width=True)
        with before_col_2:
            st.image(SURVEY_IMAGE_PATHS[1], use_container_width=True)
        st.markdown("After installation")
        after_col_1, after_col_2 = st.columns(2)
        with after_col_1:
            st.image(SURVEY_IMAGE_PATHS[2], use_container_width=True)
        with after_col_2:
            st.image(SURVEY_IMAGE_PATHS[3], use_container_width=True)


def render_chat_response(response: dict) -> None:
    st.markdown(
        f"""
        <div class="fp-chat-ai">
            <div class="fp-chat-badge">{response["title"]}</div>
            <div>{response["summary"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if response.get("bullets"):
        for item in response["bullets"]:
            st.markdown(f"- {item}")
    if response.get("table") is not None:
        st.dataframe(response["table"], use_container_width=True, hide_index=True)
    if response.get("recommendation"):
        st.caption(response["recommendation"])


@st.dialog("Send Email")
def send_email_dialog() -> None:
    with st.form("email_dialog_form"):
        recipient = st.text_input("Recipient", value="network.ops@anna-enterprise.example")
        subject = st.text_input("Subject", value="Anna Fiber Planning Survey Package")
        message = st.text_area(
            "Message",
            value=(
                "Attached is the synthetic site survey, route recommendation, and material summary "
                "for the Anna fiber planning corridor following the traced OpenStreetMap path."
            ),
            height=140,
        )
        col_1, col_2 = st.columns(2)
        with col_1:
            send = st.form_submit_button("Send", use_container_width=True)
        with col_2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)

    if send:
        st.session_state.email_sent = True
        st.session_state.last_email_meta = {
            "recipient": recipient,
            "subject": subject,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
        }
        st.rerun()
    if cancel:
        st.rerun()


def render_assistant_panel() -> None:
    st.markdown('<div class="fp-assistant-header">AI Assistant</div>', unsafe_allow_html=True)

    if st.session_state.email_sent:
        meta = st.session_state.last_email_meta
        st.success(
            f"Email queued to {meta['recipient']} at {meta['timestamp']} with the PDF package attached.",
            icon=":material/mail:",
        )

    with st.container(height=620, border=False):
        render_default_assistant_content()

        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="fp-chat-user">{message["question"]}</div>', unsafe_allow_html=True)
            else:
                render_chat_response(message["response"])

    with st.form("chat_form", clear_on_submit=True):
        prompt = st.text_input(
            "Planning question",
            placeholder="Ask about the fiber network...",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Send", use_container_width=True)
    if submitted and prompt.strip():
        st.session_state.messages.append({"role": "user", "question": prompt, "response": None})
        st.session_state.messages.append({"role": "assistant", "question": prompt, "response": find_chat_response(prompt)})
        st.rerun()

    st.markdown(
        '<div class="fp-subtle">Suggested prompts: ' + " | ".join(data.SUPPORTED_QUESTIONS) + "</div>",
        unsafe_allow_html=True,
    )

    pdf_bytes = generate_pdf_report()
    action_col_1, action_col_2 = st.columns(2)
    with action_col_1:
        st.download_button(
            "Export PDF",
            data=pdf_bytes,
            file_name="anna_fiber_plan_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with action_col_2:
        if st.button("Send Email", use_container_width=True):
            send_email_dialog()


def main() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    initialize_state()
    render_dynamic_css()
    render_topbar()
    left_col, center_col, right_col = st.columns([1.0, 3.6, 2.0], gap="large")
    with left_col:
        render_left_rail()
    with center_col:
        render_map_workspace()
    with right_col:
        render_assistant_panel()


if __name__ == "__main__":
    main()
