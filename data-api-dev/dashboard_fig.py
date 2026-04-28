import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fastapi import FastAPI, Form, Depends, HTTPException
import copy

import dashboard_sum

def build_base_figure(df, METRIC_MAP):

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

def build_user_dashboard(body, METRIC_MAP, df_base, base_fig):

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

        pct = dashboard_sum.percentile_against_others(
            peer_values,
            user_value
        )

        summary.append({
            "metric": body_key,
            "percentile": pct,
            "message": dashboard_sum.comparison_text(
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