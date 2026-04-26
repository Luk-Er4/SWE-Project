# uvicorn main:app --host 127.0.0.1 --port 8001 --reload

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import json
import copy

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from contextlib import asynccontextmanager

BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "RawData.csv"
BASE_DASHBOARD_PATH = BASE / "base_dashboard.html"

METRIC_MAP = {
    "sleep_hours": "SLEEP_HOURS",
    "physical_activity": "PHYSICAL_ACTIVITY_HOURS_PER_DAY",
    "diet_calories": "DIET_CALORIES",
    "health_risk": "HEALTH_RISK_SCORE",
    "health_score": "LIFESTYLE_SCORE"
}

class UserDashboardRequest(BaseModel):
    user_name: str
    sleep_hours: float
    physical_activity: float
    diet_calories: float
    health_risk: float
    health_score: float

df_base = None
base_fig = None


def load_base_data():
    df = pd.read_csv(DATA_PATH)

    if "Unnamed: 0" in df.columns:
        df = df.rename(columns={"Unnamed: 0": "ID"})

    metric_columns = list(METRIC_MAP.values())
    missing = [c for c in metric_columns if c not in df.columns]

    if missing:
        raise RuntimeError(f"Missing columns: {missing}")

    return df[metric_columns].dropna()


def build_base_figure(df):

    fig = make_subplots(
        rows=len(METRIC_MAP),
        cols=1,
        subplot_titles=[
            key.replace("_", " ").title()
            for key in METRIC_MAP.keys()
        ],
        vertical_spacing=0.08
    )

    for i, (body_key, csv_col) in enumerate(METRIC_MAP.items(), start=1):

        fig.add_trace(
            go.Histogram(
                x=df[csv_col],
                nbinsx=30,
                opacity=0.75,
                name=body_key
            ),
            row=i,
            col=1
        )

        fig.update_xaxes(
            title_text=body_key.replace("_", " ").title(),
            row=i,
            col=1
        )

        fig.update_yaxes(
            title_text="Count",
            row=i,
            col=1
        )

    fig.update_layout(
        height=350 * len(METRIC_MAP),
        width=1000,
        title_text="Health Metrics Compared to Others",
        showlegend=False,
        bargap=0.05
    )

    return fig


def percentile_against_others(values, user_value):

    pct = (values.dropna() < user_value).mean() * 100
    return round(pct, 1)


def comparison_text(metric_name, percentile):

    if percentile == 50:
        return f"Your {metric_name} is about average."

    if percentile > 50:
        return f"Your {metric_name} is higher than {percentile:.0f}% of people."

    return f"Your {metric_name} is lower than {100 - percentile:.0f}% of people."


@asynccontextmanager
async def lifespan(app: FastAPI):

    global df_base, base_fig

    df_base = load_base_data()
    base_fig = build_base_figure(df_base)

    base_fig.write_html(
        BASE_DASHBOARD_PATH,
        include_plotlyjs="cdn",
        full_html=True
    )

    print(f"Base histogram loaded.")
    print(f"Base dashboard saved to: {BASE_DASHBOARD_PATH}")

    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_user_dashboard(body: UserDashboardRequest):

    if df_base is None or base_fig is None:
        raise HTTPException(
            status_code=500,
            detail="Base graph not ready"
        )

    user_values = {
        "sleep_hours": body.sleep_hours,
        "physical_activity": body.physical_activity,
        "diet_calories": body.diet_calories,
        "health_risk": body.health_risk,
        "health_score": body.health_score
    }

    fig = copy.deepcopy(base_fig)

    fig.update_layout(
        title_text=f"{body.user_name}'s Health Metrics Compared to Others"
    )

    summary = []

    for i, (body_key, csv_col) in enumerate(METRIC_MAP.items(), start=1):

        user_value = user_values[body_key]
        peer_values = df_base[csv_col]

        pct = percentile_against_others(
            peer_values,
            user_value
        )

        summary.append({
            "metric": body_key,
            "percentile": pct,
            "message": comparison_text(
                body_key.replace("_", " "),
                pct
            )
        })

        fig.add_vline(
            x=user_value,
            line_dash="dash",
            line_width=2,
            annotation_text=body.user_name,
            annotation_position="top right",
            row=i,
            col=1
        )

        fig.layout.annotations[i - 1].text = (
            f"{body_key.replace('_',' ').title()} — "
            f"higher than {pct:.0f}% of people"
        )

    return fig, summary

@app.post("/api/user/create_dashboard")
def create_dashboard(body: UserDashboardRequest):

    fig, summary = build_user_dashboard(body)

    return {
        "user_name": body.user_name,
        "summary": summary,
        "figure": json.loads(fig.to_json())
    }