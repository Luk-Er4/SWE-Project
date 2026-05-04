import ResultsDashboard from "./ResultsDashboard";
import ResultsDrivers from "./ResultsDrivers";
import ResultsOverview from "./ResultsOverview";
import ResultsRecommendations from "./ResultsRecommendations";

function formatScore(value) {
  return typeof value === "number" && Number.isFinite(value)
    ? value.toFixed(1)
    : "--";
}

function formatContribution(value) {
  return typeof value === "number" && Number.isFinite(value)
    ? value.toFixed(3)
    : "--";
}

function summarizeObject(value) {
  if (!value || typeof value !== "object") {
    return "";
  }

  const preferredKeys = ["summary", "message", "label", "title", "insight"];
  const preferred = preferredKeys
    .map((key) => value[key])
    .filter((item) => typeof item === "string" && item.trim());

  if (preferred.length) {
    return preferred.join(" ");
  }

  const entries = Object.entries(value)
    .filter(([, item]) => item !== null && item !== undefined && item !== "")
    .slice(0, 4)
    .map(([key, item]) => {
      if (typeof item === "object") {
        return `${key}: ${JSON.stringify(item)}`;
      }

      return `${key}: ${item}`;
    });

  return entries.join(" | ");
}

function normalizeSummaryItems(value) {
  if (typeof value === "string" && value.trim()) {
    return [value.trim()];
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    return [value.toString()];
  }

  if (Array.isArray(value)) {
    return value
      .map((item) => {
        if (typeof item === "string") {
          return item.trim();
        }

        if (typeof item === "number" && Number.isFinite(item)) {
          return item.toString();
        }

        return summarizeObject(item);
      })
      .filter(Boolean);
  }

  if (value && typeof value === "object") {
    const summary = summarizeObject(value);
    return summary ? [summary] : [];
  }

  return [];
}

function getScoreBand(score) {
  if (typeof score !== "number" || !Number.isFinite(score)) {
    return {
      label: "Not enough data",
      tone: "neutral",
      message: "We need a valid score before we can position this result with confidence.",
    };
  }

  if (score <= 25) {
    return {
      label: "High attention",
      tone: "alert",
      message: "This lands in the lowest quarter of the scale, which suggests a weaker baseline and more immediate room to improve.",
    };
  }

  if (score <= 50) {
    return {
      label: "Needs work",
      tone: "caution",
      message: "This sits below the midpoint of the scale, so the model sees a few meaningful pressure points worth addressing next.",
    };
  }

  if (score <= 75) {
    return {
      label: "Promising",
      tone: "good",
      message: "This is above average on the 0 to 100 scale and points to a fairly solid routine with some opportunities to sharpen it.",
    };
  }

  return {
    label: "Strong footing",
    tone: "great",
    message: "This is in the upper end of the scale and suggests lower modeled risk with stronger day-to-day health signals overall.",
  };
}

function buildRecommendations(result) {
  const recommendations = [];
  const healthFactors = result.top_health_factors || [];
  const lifestyleFactors = result.top_lifestyle_factors || [];
  const leadingFactors = [...healthFactors, ...lifestyleFactors].map((item) =>
    (item.Feature || "").toLowerCase()
  );

  if (result.bmi >= 30) {
    recommendations.push(
      "Focus on a sustainable calorie deficit and a consistent walking or strength routine to start improving weight-related risk."
    );
  } else if (result.bmi > 25) {
    recommendations.push(
      "Your BMI is slightly elevated, so small improvements in movement consistency and portion control could have an outsized payoff."
    );
  } else if (result.bmi > 0 && result.bmi < 18.5) {
    recommendations.push(
      "Your BMI trends low, so prioritize adequate meals, protein intake, and recovery rather than aggressive restriction."
    );
  }

  if (leadingFactors.some((factor) => factor.includes("sleep"))) {
    recommendations.push(
      "Protect a reliable sleep window for the next two weeks and aim for a bedtime routine that reduces stimulation 30 to 60 minutes before bed."
    );
  }

  if (leadingFactors.some((factor) => factor.includes("physical_activity") || factor.includes("activity"))) {
    recommendations.push(
      "Add movement you can repeat, not just movement that looks ideal. Even one extra intentional hour of activity per week can improve your trajectory."
    );
  }

  if (leadingFactors.some((factor) => factor.includes("smoking"))) {
    recommendations.push(
      "Smoking appears to be a major driver in your score. Reducing frequency is a meaningful first step if quitting all at once feels unrealistic."
    );
  }

  if (leadingFactors.some((factor) => factor.includes("diet"))) {
    recommendations.push(
      "Treat your diet as a pattern, not a single meal. Build around fiber, hydration, and steadier calorie quality before chasing a perfect plan."
    );
  }

  if (leadingFactors.some((factor) => factor.includes("age"))) {
    recommendations.push(
      "Age is influencing the model, which you cannot change, so focus your effort on the controllable sleep, activity, and nutrition patterns around it."
    );
  }

  if (!recommendations.length) {
    recommendations.push(
      "Keep reinforcing the basics: sleep consistency, regular activity, hydration, and a diet pattern you can maintain without burnout."
    );
  }

  return recommendations.slice(0, 4);
}

function normalizeFactors(items) {
  if (!items?.length) {
    return [];
  }

  return items.map((item) => ({
    feature: item.Feature,
    contribution: formatContribution(item.AbsContribution ?? item.contribution),
  }));
}

export default function ResultsPanel({ result, onEdit, onReset }) {
  if (!result) {
    return null;
  }

  const healthBand = getScoreBand(result.health_risk_score);
  const lifestyleBand = getScoreBand(result.lifestyle_score);
  const recommendations = buildRecommendations(result);
  const summaryItems = normalizeSummaryItems(result.dashboard_summary);

  return (
    <section className="results-experience">
      <div className="results-hero-card stage-fade">
        <div>
          <p className="panel-kicker">Results</p>
          <h1>Your health snapshot, with context built in.</h1>
          <p className="muted results-hero-copy">
            Both scores are shown on a 0 to 100 scale. Higher values are better in
            this model and generally indicate lower modeled risk with healthier
            routine signals.
          </p>
        </div>

        <div className="results-actions">
          <button type="button" className="back-link" onClick={onEdit}>
            Edit Answers
          </button>
          <button type="button" className="hero-button" onClick={onReset}>
            Start Fresh
          </button>
        </div>
      </div>

      <div className="results-grid stage-fade">
        <ResultsOverview
          healthScore={formatScore(result.health_risk_score)}
          lifestyleScore={formatScore(result.lifestyle_score)}
          bmi={formatScore(result.bmi)}
          healthBand={healthBand}
          lifestyleBand={lifestyleBand}
        />

        <ResultsDrivers
          healthFactors={normalizeFactors(result.top_health_factors)}
          lifestyleFactors={normalizeFactors(result.top_lifestyle_factors)}
        />

        <ResultsDashboard
          summaryItems={summaryItems}
          figure={result.dashboard_figure}
        />

        <ResultsRecommendations recommendations={recommendations} />
      </div>
    </section>
  );
}
