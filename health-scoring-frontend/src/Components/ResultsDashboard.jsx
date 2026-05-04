import PlotlyFigure from "./PlotlyFigure";

export default function ResultsDashboard({ summaryItems, figure }) {
  return (
    <section className="results-panel results-dashboard">
      <div className="panel-heading">
        <p className="panel-kicker">Dashboard</p>
        <h2>Visual follow-through</h2>
        <p className="muted">
          This view translates the score into a quick read plus a chart you can scan
          for pattern context.
        </p>
      </div>

      <div className="dashboard-summary-card">
        <h3>Summary</h3>
        {!summaryItems.length ? (
          <p className="muted">Dashboard summary not available yet.</p>
        ) : (
          <ul className="dashboard-summary-list">
            {summaryItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        )}
      </div>

      <div className="dashboard-chart-card">
        <h3>Graph view</h3>
        {figure ? (
          <PlotlyFigure figure={figure} />
        ) : (
          <p className="muted">No dashboard figure was returned for this result.</p>
        )}
      </div>
    </section>
  );
}
