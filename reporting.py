from __future__ import annotations

from io import BytesIO

from PIL import Image as PILImage
from PIL import ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from data import BOM_ITEMS, ENDPOINTS, FIBER_SEGMENTS, PROJECT, RISK_ITEMS, SURVEY_FINDINGS
from planning import build_bom_dataframe, build_risk_dataframe, get_recommendation


def _normalize_points():
    all_points = []
    for segment in FIBER_SEGMENTS:
        all_points.extend(segment["points"])

    lats = [point[0] for point in all_points]
    lons = [point[1] for point in all_points]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    lat_span = max_lat - min_lat
    lon_span = max_lon - min_lon

    def scale(lat: float, lon: float, width: int = 1000, height: int = 640, padding: int = 80):
        x = padding + ((lon - min_lon) / lon_span) * (width - 2 * padding)
        y = height - padding - ((lat - min_lat) / lat_span) * (height - 2 * padding)
        return (int(x), int(y))

    return scale


def generate_route_snapshot() -> bytes:
    width, height = 1000, 640
    image = PILImage.new("RGB", (width, height), "#f5f1e8")
    draw = ImageDraw.Draw(image)
    scale = _normalize_points()

    draw.rounded_rectangle((28, 28, width - 28, height - 28), radius=18, outline="#d0d0d0", width=3, fill="#ffffff")
    draw.rounded_rectangle((40, 38, 360, 98), radius=12, fill="#cd040b")
    draw.text((60, 52), "Anna, Texas Fiber Corridor Snapshot", fill="#ffffff")
    draw.text((60, 108), "OpenStreetMap path with synthetic plant overlays", fill="#333333")

    street_guides = [
        ((90, 170), (920, 170)),
        ((90, 295), (920, 295)),
        ((90, 430), (920, 430)),
        ((200, 120), (800, 560)),
    ]
    for start, end in street_guides:
        draw.line([start, end], fill="#dad3c7", width=6)

    for segment in FIBER_SEGMENTS:
        points = [scale(lat, lon) for lat, lon in segment["points"]]
        color = segment["color"]
        if segment["dash_array"]:
            for index in range(len(points) - 1):
                start = points[index]
                end = points[index + 1]
                draw.line([start, end], fill=color, width=8)
        else:
            draw.line(points, fill=color, width=9, joint="curve")

    start_xy = scale(ENDPOINTS["start"].lat, ENDPOINTS["start"].lon)
    end_xy = scale(ENDPOINTS["end"].lat, ENDPOINTS["end"].lon)
    draw.ellipse((start_xy[0] - 10, start_xy[1] - 10, start_xy[0] + 10, start_xy[1] + 10), fill="#111111")
    draw.ellipse((end_xy[0] - 10, end_xy[1] - 10, end_xy[0] + 10, end_xy[1] + 10), fill="#cd040b")
    draw.text((start_xy[0] + 14, start_xy[1] - 18), "121 Pagoda Dr", fill="#23313d")
    draw.text((end_xy[0] + 14, end_xy[1] - 18), "313 Kelvinton Dr", fill="#23313d")

    legend_y = 520
    legends = [
        ("#111111", "Existing fiber"),
        ("#cd040b", "Recommended build"),
        ("#8b8b8b", "Alternate route"),
    ]
    for offset, (color, label) in enumerate(legends):
        x = 70 + offset * 260
        draw.line([(x, legend_y), (x + 40, legend_y)], fill=color, width=8)
        draw.text((x + 55, legend_y - 10), label, fill="#23313d")

    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def _make_cost_table():
    dataframe = build_bom_dataframe()
    rows = [list(dataframe.columns)] + dataframe.values.tolist()
    table = Table(rows, repeatRows=1, colWidths=[0.85 * inch, 2.0 * inch, 0.65 * inch, 0.6 * inch, 0.85 * inch, 1.1 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#eef2f4")]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c5ced6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def _make_risk_table():
    dataframe = build_risk_dataframe()[["Risk", "Severity", "Score", "Owner"]]
    rows = [list(dataframe.columns)] + dataframe.values.tolist()
    table = Table(rows, repeatRows=1, colWidths=[3.1 * inch, 1.1 * inch, 0.8 * inch, 1.4 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#cd040b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#fff8f1"), colors.HexColor("#f9efe5")]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d3b59d")),
            ]
        )
    )
    return table


def generate_pdf_report() -> bytes:
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=letter, topMargin=0.55 * inch, bottomMargin=0.55 * inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SectionTitle", parent=styles["Heading2"], textColor=colors.HexColor("#1f2d3a"), spaceAfter=8))
    styles.add(ParagraphStyle(name="BodyTight", parent=styles["BodyText"], fontSize=9, leading=12, textColor=colors.HexColor("#334e68")))

    recommendation = get_recommendation()
    bom_total = sum(item["quantity"] * item["unit_cost"] for item in BOM_ITEMS)

    snapshot_buffer = BytesIO(generate_route_snapshot())
    snapshot = Image(snapshot_buffer, width=6.7 * inch, height=4.2 * inch)

    story = [
        Paragraph(PROJECT["name"], styles["Title"]),
        Paragraph(f"{PROJECT['customer']} | {PROJECT['market']}", styles["Heading3"]),
        Paragraph(f"Prepared by {PROJECT['planner']} on {PROJECT['report_date']}", styles["BodyTight"]),
        Spacer(1, 0.15 * inch),
        snapshot,
        Spacer(1, 0.15 * inch),
        Paragraph("Executive Summary", styles["SectionTitle"]),
        Paragraph(
            (
                f"The recommended alignment is <b>{recommendation['selected_route_name']}</b> between "
                f"{ENDPOINTS['start'].address} and {ENDPOINTS['end'].address}. "
                f"The design reuses existing outside plant where practical, limits new build to "
                f"{recommendation['estimated_new_build_ft']:,} feet, and keeps the corridor risk posture manageable."
            ),
            styles["BodyTight"],
        ),
        Spacer(1, 0.12 * inch),
        Paragraph("Route Metrics", styles["SectionTitle"]),
        Paragraph(
            (
                f"Preferred route distance: {recommendation['distance_ft']:,} ft<br/>"
                f"Estimated capex: ${recommendation['estimated_capex']:,.0f}<br/>"
                f"Average risk score: {recommendation['risk_score']} / 100<br/>"
                f"Survey coverage window: {PROJECT['survey_window']}"
            ),
            styles["BodyTight"],
        ),
        Spacer(1, 0.12 * inch),
        Paragraph("Bill of Materials", styles["SectionTitle"]),
        _make_cost_table(),
        Spacer(1, 0.12 * inch),
        Paragraph(f"Material total: ${bom_total:,.0f}", styles["BodyTight"]),
        Spacer(1, 0.12 * inch),
        Paragraph("Risk Register", styles["SectionTitle"]),
        _make_risk_table(),
        Spacer(1, 0.12 * inch),
        Paragraph("Field Survey Notes", styles["SectionTitle"]),
    ]

    for finding in SURVEY_FINDINGS:
        story.append(
            Paragraph(
                f"<b>{finding['name']}</b>: {finding['details']} ({finding['status']} / {finding['priority']} priority)",
                styles["BodyTight"],
            )
        )
        story.append(Spacer(1, 0.05 * inch))

    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Next Step", styles["SectionTitle"]))
    story.append(Paragraph(recommendation["reason_summary"], styles["BodyTight"]))

    document.build(story)
    return output.getvalue()
