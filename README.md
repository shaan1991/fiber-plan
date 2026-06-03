# Anna Fiber Planning Dashboard

Streamlit enterprise demo for a synthetic fiber planning workflow in Anna, Texas. The dashboard uses an OpenStreetMap basemap and overlays synthetic plant, site survey, BOM, and risk data for the default corridor between `121 Pagoda Drive` and `313 Kelvinton Drive`.

## Run locally

```bash
pip3 install -r requirements.txt
streamlit run app.py
```

## Demo features

- Left-side corridor map with existing fiber, recommended route, alternate route, survey markers, and risk markers
- Right-side AI-style planning chat with preloaded Q&A and formatted tables
- KPI cards, route comparison, site survey, risk register, and BOM
- Functional PDF report export
- Synthetic email handoff flow
