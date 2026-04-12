export default function LandingHero({ onStart }) {
  return (
    <section className="hero hero-single">
      <div className="hero-text hero-text-full">
        <p className="hero-badge">Educational health questionnaire</p>
        <h1>Discover your health score in a simple, guided questionnaire</h1>
        <p className="hero-subtext">
          Answer a few health and lifestyle questions to receive a health
          score, comparison insights, and personalized recommendations.
        </p>
        <button className="hero-button" onClick={onStart}>
          Start Questionnaire
        </button>
      </div>
    </section>
  );
}