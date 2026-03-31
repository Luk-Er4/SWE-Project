import { useState } from "react";
import TopBar from "../Components/TopBar";
import HealthForm from "../Components/HealthForm";
import Results from "../Components/Results";

export default function Questionaire({ user, onLogout }) {
  const [result, setResult] = useState(null);

  return (
    <div className="page">
      <TopBar user={user} onLogout={onLogout} />

      <section className="info-cards">
        <div className="info-card">
          <h3>1. Fill out the form</h3>
          <p>Users answer health and lifestyle questions in a clean interface.</p>
        </div>
        <div className="info-card">
          <h3>2. Generate the score</h3>
          <p>Let the magic happen.</p>
        </div>
        <div className="info-card">
          <h3>3. View results</h3>
          <p>Users get their score, risk areas, and personalized feedback.</p>
        </div>
      </section>

      <section className="main-content">
        <HealthForm setResult={setResult} />
        <Results result={result} />
      </section>

      <footer className="footer">
        <p>
          Disclaimer: This application is for educational purposes only and is
          not intended to provide medical advice or replace professional
          healthcare guidance.
        </p>
      </footer>
    </div>
  );
}