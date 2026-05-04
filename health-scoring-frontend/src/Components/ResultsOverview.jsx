export default function ResultsOverview({
  healthScore,
  lifestyleScore,
  bmi,
  healthBand,
  lifestyleBand,
}) {
  return (
    <section className="results-panel results-overview">
      <div className="panel-heading">
        <p className="panel-kicker">Overview</p>
        <h2>Scores that say what they mean</h2>
        <p className="muted">
          Think of both numbers as a 0 to 100 read. Higher is better in this model,
          with stronger routines and lower modeled risk showing up closer to 100.
        </p>
      </div>

      <div className="overview-score-grid">
        <article className={`score-box score-box-${healthBand.tone}`}>
          <div className="score-scale">out of 100</div>
          <h3>
            {healthScore}
            <span>/100</span>
          </h3>
          <p>Health Risk Score</p>
          <span className="score-pill">{healthBand.label}</span>
          <small>Higher means lower modeled risk and a stronger overall outlook.</small>
        </article>

        <article className={`score-box score-box-${lifestyleBand.tone}`}>
          <div className="score-scale">out of 100</div>
          <h3>
            {lifestyleScore}
            <span>/100</span>
          </h3>
          <p>Lifestyle Score</p>
          <span className="score-pill">{lifestyleBand.label}</span>
          <small>Higher means healthier routine patterns in the signals you entered.</small>
        </article>
      </div>

      <div className="insight-banner">
        <div>
          <p className="insight-label">Health read</p>
          <h4>{healthBand.message}</h4>
        </div>
        <div>
          <p className="insight-label">Lifestyle read</p>
          <h4>{lifestyleBand.message}</h4>
        </div>
      </div>

      <div className="metric-chip-row">
        <div className="metric-chip">
          <span>BMI</span>
          <strong>{bmi}</strong>
        </div>
        <div className="metric-chip">
          <span>Scale note</span>
          <strong>0 is weakest, 100 is strongest</strong>
        </div>
      </div>
    </section>
  );
}
