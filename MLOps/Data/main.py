from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

DATA_PATH = r'.\RawData.csv'

METRIC_MAP = {
    "sleep_hours": "SLEEP_HOURS",
    "physical_activity": "PHYSICAL_ACTIVITY_HOURS_PER_DAY",
    "diet_calories": "DIET_CALORIES",
    "health_risk": "HEALTH_RISK_SCORE",
    "health_score": "LIFESTYLE_SCORE"
}

class UserComparisonRequest(BaseModel):
    user_name: str
    sleep_hours: float
    physical_activity: float
    diet_calories: float
    health_risk: float
    health_score: float

def percentile_against_others(values, user_value):
    others = values.dropna()
    pct = (others < user_value).mean() * 100
    return round(pct, 1)

def comparison_text(metric_name, user_value, percentile):
    if percentile == 50:
        return f"Your {metric_name} is about average."
    if percentile > 50:
        return f"Your {metric_name} is higher than {percentile:.0f}% of people."
    return f"Your {metric_name} is lower than {100 - percentile:.0f}% of people."

def build_user_comparison_figure(body: UserComparisonRequest):
    df = pd.read_csv(DATA_PATH)
    df = df.rename(columns={"Unnamed: 0": "ID"})

    metric_columns = list(METRIC_MAP.values())
    df = df[metric_columns].dropna()

    user_values = {
        "sleep_hours": body.sleep_hours,
        "physical_activity": body.physical_activity,
        "diet_calories": body.diet_calories,
        "health_risk": body.health_risk,
        "health_score": body.health_score
    }

    summary = []

    for body_key, csv_col in METRIC_MAP.items():
        user_value = user_values[body_key]
        peer_values = df[csv_col]

        pct = percentile_against_others(peer_values, user_value)

        summary.append({
            "metric": body_key,
            "csv_column": csv_col,
            "user_value": float(user_value),
            "percentile": pct,
            "message": comparison_text(body_key.replace("_", " "), user_value, pct)
        })

    fig = make_subplots(
        rows=len(METRIC_MAP),
        cols=1,
        subplot_titles=[
            f"{body_key.replace('_', ' ').title()} — higher than "
            f"{item['percentile']:.0f}% of people"
            for body_key, item in zip(METRIC_MAP.keys(), summary)
        ],
        vertical_spacing=0.08
    )

    for i, (body_key, csv_col) in enumerate(METRIC_MAP.items(), start=1):
        peer_values = df[csv_col]
        user_value = user_values[body_key]

        fig.add_trace(
            go.Histogram(
                x=peer_values,
                nbinsx=30,
                name=body_key.replace("_", " ").title(),
                opacity=0.75
            ),
            row=i,
            col=1
        )

        fig.add_vline(
            x=user_value,
            line_dash="dash",
            line_width=2,
            annotation_text=body.user_name,
            annotation_position="top right",
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
        title_text=f"{body.user_name}'s Health Metrics Compared to Others",
        showlegend=False,
        bargap=0.05
    )

    return fig, summary

@app.post("/api/user/comparison-chart")
def get_user_comparison_chart(body: UserComparisonRequest):
    fig, summary = build_user_comparison_figure(body)

    return {
        "user_name": body.user_name,
        "summary": summary,
        "figure": json.loads(fig.to_json())
    }