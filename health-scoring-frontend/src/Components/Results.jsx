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
  return (
    <div className="results-card">
      <h2>Results Dashboard</h2>

      {!result ? (
        <p className="muted">
          Fill out the questionnaire and submit it to see your results.
        </p>
      ) : (
        <>
          <div className="score-grid">
            <div className="score-box">
              <h3>{formatScore(result.health_risk_score)}</h3>
              <p>Health Risk Score</p>
            </div>

            <div className="score-box secondary-score">
              <h3>{formatScore(result.lifestyle_score)}</h3>
              <p>Lifestyle Score</p>
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
              <p className="muted">
                Dashboard figure data loaded from the API and ready for chart rendering.
              </p>
            ) : null}
          </div>
        </>
      )}
    </div>
  );
}
