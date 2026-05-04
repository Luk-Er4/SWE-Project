export default function ResultsRecommendations({ recommendations }) {
  return (
    <section className="results-panel">
      <div className="panel-heading">
        <p className="panel-kicker">Recommendations</p>
        <h2>What to do next</h2>
        <p className="muted">
          These are practical starting points based on the strongest patterns the
          model noticed in your inputs.
        </p>
      </div>

      <ul className="recommendation-list">
        {recommendations.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}
