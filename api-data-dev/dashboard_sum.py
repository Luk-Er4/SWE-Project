def percentile_against_others(values, user_value):

    pct = (values.dropna() < user_value).mean() * 100
    return round(pct, 1)

def comparison_text(metric_name, percentile):

    if percentile == 50:
        return f"Your {metric_name} is about average."

    if percentile > 50:
        return f"Your {metric_name} is higher than {percentile:.0f}% of people."

    return f"Your {metric_name} is lower than {100 - percentile:.0f}% of people."
