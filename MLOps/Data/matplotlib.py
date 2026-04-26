import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

df = pd.read_csv('.\MLOps\Data\RawData.csv')
df = df.rename(columns={"Unnamed: 0": "ID"})

USER_ID_COL = "ID"
TARGET_USER = 2

METRICS = [
    "SLEEP_HOURS",
    "PHYSICAL_ACTIVITY_HOURS_PER_DAY",
    "DIET_CALORIES",
    "HEALTH_RISK_SCORE",
    "LIFESTYLE_SCORE"
]

df = df[[USER_ID_COL] + METRICS].dropna()

df_user_level = df.copy()

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

user_row = df_user_level[df_user_level[USER_ID_COL] == TARGET_USER]
if user_row.empty:
    raise ValueError(f"User {TARGET_USER} not found.")

user_row = user_row.iloc[0]

summary = []
for metric in METRICS:
    user_value = user_row[metric]
    peer_values = df_user_level.loc[df_user_level[USER_ID_COL] != TARGET_USER, metric]
    pct = percentile_against_others(peer_values, user_value)
    summary.append({
        "metric": metric,
        "user_value": user_value,
        "percentile": pct,
        "message": comparison_text(metric.replace("_", " "), user_value, pct)
    })

summary_df = pd.DataFrame(summary)

for msg in summary_df["message"]:
    print("•", msg)

n = len(METRICS)
fig, axes = plt.subplots(n, 1, figsize=(10, 4 * n))

if n == 1:
    axes = [axes]

for ax, metric in zip(axes, METRICS):
    peer_values = df_user_level.loc[df_user_level[USER_ID_COL] != TARGET_USER, metric]
    user_value = user_row[metric]
    pct = summary_df.loc[summary_df["metric"] == metric, "percentile"].iloc[0]

    sns.histplot(peer_values, kde=True, ax=ax, color="skyblue")
    ax.axvline(user_value, color="darkblue", linestyle="--", linewidth=2)
    ax.set_title(f"{metric.replace('_', ' ').title()} — higher than {pct:.0f}% of people")
    ax.set_xlabel(metric.replace("_", " ").title())

plt.tight_layout()
plt.show()