import Authform from "../Components/Authform";

export default function Authpage({ onBack, onAuthSuccess }) {
  return (
    <div className="page auth-page-wrap">
      <section className="auth-layout">
        <div className="auth-side">
          <p className="hero-badge">Health Scoring System</p>
          <h1>Welcome</h1>
          <p className="hero-subtext">
            Sign in or create an account to continue to the questionnaire.
          </p>
          <button className="back-link" onClick={onBack}>
            ← Back to home
          </button>
        </div>

        <Authform onAuthSuccess={onAuthSuccess} />
      </section>
    </div>
  );
}