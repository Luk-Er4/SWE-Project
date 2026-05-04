import PlotlyFigure from "./PlotlyFigure";

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

function formatSummary(value) {
  if (typeof value === "string") {
    return value;
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    return value.toString();
  }

  if (Array.isArray(value)) {
    return value.join(", ");
  }

  if (value && typeof value === "object") {
    if (typeof value.summary === "string") {
      return value.summary;
    }

    try {
      return JSON.stringify(value);
    } catch {
      return "Dashboard summary unavailable.";
    }
  }

  return "Dashboard summary not available yet.";
}

function getScoreBand(score) {
  if (typeof score !== "number" || !Number.isFinite(score)) {
    return {
      label: "Not enough data",
      tone: "neutral",
      message: "We need a valid score before we can meaningfully position your result.",
    };
  }

  if (score <= 25) {
    return {
      label: "High attention",
      tone: "alert",
      message: "The model sees several signals worth improving soon rather than later.",
    };
  }

  if (score <= 50) {
    return {
      label: "Needs work",
      tone: "caution",
      message: "You have a workable baseline, but there are still a few visible pressure points.",
    };
  }

  if (score <= 75) {
    return {
      label: "Promising",
      tone: "good",
      message: "You are in a healthier range overall, with room to fine-tune key habits.",
    };
  }

  return {
    label: "Strong footing",
    tone: "great",
    message: "Your inputs suggest a relatively strong routine compared with the wider baseline.",
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
      "Protect a reliable sleep window for the next two weeks and aim for a bedtime routine that cuts stimulation 30 to 60 minutes before bed."
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
      "Age is influencing the model, which you cannot change, so focus your energy on the controllable lifestyle variables driving the rest of the score."
    );
  }

  if (!recommendations.length) {
    recommendations.push(
      "Keep reinforcing the basics: sleep consistency, regular activity, hydration, and a diet pattern you can maintain without burnout."
    );
  }

  return recommendations.slice(0, 4);
}

function renderFactors(items) {
  if (!items?.length) {
    return <p className="muted">No feature contributions returned.</p>;
  }

  return (
    <ul className="factor-list">
      {items.map((item) => (
        <li key={`${item.Feature}-${item.AbsContribution ?? item.contribution}`}>
          <span>{item.Feature}</span>
          <strong>{formatContribution(item.AbsContribution ?? item.contribution)}</strong>
        </li>
      ))}
    </ul>
  );
}

export default function ResultsPanel({ result }) {
  const healthBand = result ? getScoreBand(result.health_risk_score) : null;
  const lifestyleBand = result ? getScoreBand(result.lifestyle_score) : null;
  const recommendations = result ? buildRecommendations(result) : [];

  return (
    <div className="results-card">
      <div className="panel-heading">
        <p className="panel-kicker">Results</p>
        <h2>Context, not just a number</h2>
        <p className="muted">
          We translate the raw model output into a practical read on what matters most
          right now.
        </p>
      </div>

      {!result ? (
        <div className="results-empty">
          <p className="results-empty-title">Your score story will appear here.</p>
          <p className="muted">
            Submit the questionnaire to unlock score context, key driver analysis, and
            recommendations.
          </p>
        </div>
      ) : (
        <>
          <div className="score-grid">
            <div className={`score-box score-box-${healthBand?.tone || "neutral"}`}>
              <h3>{formatScore(result.health_risk_score)}</h3>
              <p>Health Risk Score</p>
              <span className="score-pill">{healthBand?.label}</span>
            </div>

            <div className={`score-box secondary-score score-box-${lifestyleBand?.tone || "neutral"}`}>
              <h3>{formatScore(result.lifestyle_score)}</h3>
              <p>Lifestyle Score</p>
              <span className="score-pill">{lifestyleBand?.label}</span>
            </div>
          </div>

          <div className="insight-banner">
            <div>
              <p className="insight-label">Health read</p>
              <h4>{healthBand?.message}</h4>
            </div>
            <div>
              <p className="insight-label">Lifestyle read</p>
              <h4>{lifestyleBand?.message}</h4>
            </div>
          </div>

          <div className="result-section">
            <h4>BMI</h4>
            <p>{formatScore(result.bmi)}</p>
          </div>

          <div className="result-section">
            <h4>Top Health Factors</h4>
            {renderFactors(result.top_health_factors)}
          </div>

          <div className="result-section">
            <h4>Top Lifestyle Factors</h4>
            {renderFactors(result.top_lifestyle_factors)}
          </div>

          <div className="result-section">
            <h4>Dashboard Summary</h4>
            <p>{formatSummary(result.dashboard_summary)}</p>
            {result.dashboard_figure ? (
              <PlotlyFigure figure={result.dashboard_figure} />
            ) : null}
          </div>

          <div className="result-section">
            <h4>Recommended next moves</h4>
            <ul className="recommendation-list">
              {recommendations.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
