# uvicorn main2:app --host 127.0.0.1 --port 8001 --reload

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from pathlib import Path
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

BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "RawData.csv"

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


def build_user_comparison_matplotlib(body: UserDashboardRequest):
    df = pd.read_csv(DATA_PATH)

    if "Unnamed: 0" in df.columns:
        df = df.rename(columns={"Unnamed: 0": "ID"})

    metric_columns = list(METRIC_MAP.values())

    missing_cols = [col for col in metric_columns if col not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=500,
            detail=f"Missing columns in CSV: {missing_cols}"
        )

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
            "message": comparison_text(
                body_key.replace("_", " "),
                user_value,
                pct
            )
        })

    n = len(METRIC_MAP)

    fig, axes = plt.subplots(
        n,
        1,
        figsize=(10, 4 * n)
    )

    if n == 1:
        axes = [axes]

    for ax, (body_key, csv_col), item in zip(
        axes,
        METRIC_MAP.items(),
        summary
    ):
        peer_values = df[csv_col]
        user_value = user_values[body_key]
        pct = item["percentile"]

        ax.hist(peer_values, bins=30, alpha=0.75)
        ax.axvline(user_value, linestyle="--", linewidth=2)

        ax.set_title(
            f"{body_key.replace('_', ' ').title()} — higher than {pct:.0f}% of people"
        )
        ax.set_xlabel(body_key.replace("_", " ").title())
        ax.set_ylabel("Count")

        ax.text(
            user_value,
            ax.get_ylim()[1] * 0.9,
            body.user_name,
            rotation=90,
            verticalalignment="top"
        )

    fig.suptitle(
        f"{body.user_name}'s Health Metrics Compared to Others",
        fontsize=16
    )

    plt.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)

    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    plt.close(fig)

    return image_base64, summary


@app.post("/api/user/create_dashboard")
def get_user_comparison_chart(body: UserDashboardRequest):
    image_base64, summary = build_user_comparison_matplotlib(body)

    return {
        "user_name": body.user_name,
        "summary": summary,
        "figure": {
            "type": "matplotlib",
            "format": "png",
            "image_base64": image_base64
        }
    }