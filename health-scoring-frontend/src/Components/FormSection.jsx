export default function FormSection({ eyebrow, title, description, children }) {
  return (
    <section className="form-section">
      <div className="form-section-header">
        <p className="section-eyebrow">{eyebrow}</p>
        <h3>{title}</h3>
        <p className="section-description">{description}</p>
      </div>
      <div className="form-section-grid">{children}</div>
    </section>
  );
}
