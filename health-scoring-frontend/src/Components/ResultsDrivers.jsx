function renderFactorList(title, items, emptyText) {
  return (
    <article className="driver-card">
      <h3>{title}</h3>
      {!items.length ? (
        <p className="muted">{emptyText}</p>
      ) : (
        <ul className="factor-list">
          {items.map((item) => (
            <li key={`${title}-${item.feature}-${item.contribution}`}>
              <span>{item.feature}</span>
              <strong>{item.contribution}</strong>
            </li>
          ))}
        </ul>
      )}
    </article>
  );
}

export default function ResultsDrivers({ healthFactors, lifestyleFactors }) {
  return (
    <section className="results-panel">
      <div className="panel-heading">
        <p className="panel-kicker">Key Drivers</p>
        <h2>What influenced the score most</h2>
        <p className="muted">
          These are the strongest signals the model surfaced from your answers. They
          are not diagnoses, just the biggest contributors in this prediction pass.
        </p>
      </div>

      <div className="driver-grid">
        {renderFactorList(
          "Top health factors",
          healthFactors,
          "No health factor contributions were returned."
        )}
        {renderFactorList(
          "Top lifestyle factors",
          lifestyleFactors,
          "No lifestyle factor contributions were returned."
        )}
      </div>
    </section>
  );
}
