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
          <div className="score-box">
            <h3>{result.score}/100</h3>
            <p>Health Score</p>
          </div>

          <div className="result-section">
            <h4>Comparison Percentile</h4>
            <p>{result.percentile}th percentile</p>
          </div>

          <div className="result-section">
            <h4>Risk Areas</h4>
            {result.riskAreas.length === 0 ? (
              <p className="muted">No major risk areas identified.</p>
            ) : (
              <ul>
                {result.riskAreas.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            )}
          </div>

          <div className="result-section">
            <h4>Recommendations</h4>
            <ul>
              {result.recommendations.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}