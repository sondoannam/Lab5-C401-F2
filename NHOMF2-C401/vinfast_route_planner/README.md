# VinFast Route Planner MVP

Minimal project scaffold based on `NHOMF2-C401/spec-draft.md`.

## Structure

```text
vinfast_route_planner/
├── app/
│   └── streamlit_app.py
├── core/
│   ├── config.py
│   ├── models.py
│   └── planner.py
├── data/
│   ├── stations.json
│   └── station_repository.py
├── services/
│   ├── distance_service.py
│   └── summary_service.py
├── utils/
│   └── formatters.py
└── tests/
    └── test_planner.py
```

## Run

```bash
pip install streamlit requests
streamlit run NHOMF2-C401/vinfast_route_planner/app/streamlit_app.py
```
