import { useEffect, useState } from "react";
import TopBar from "../Components/TopBar";
import HealthForm from "../Components/HealthForm";
import Results from "../Components/Results";
import { fetchUserHealth } from "../lib/api";

export default function Questionaire({ user, onLogout }) {
  const [result, setResult] = useState(null);
  const [savedHealthData, setSavedHealthData] = useState(null);
  const [loadMessage, setLoadMessage] = useState("");

  useEffect(() => {
    let ignore = false;

    async function loadHealthProfile() {
      if (!user?.user_uuid) {
        return;
      }

      try {
        const response = await fetchUserHealth(user.user_uuid);

        if (ignore) {
          return;
        }

        if (response.health_data?.length) {
          setSavedHealthData(response.health_data[0]);
          setLoadMessage("Loaded your saved health profile.");
        } else {
          setSavedHealthData(null);
          setLoadMessage(response.message || "");
        }
      } catch (error) {
        if (!ignore) {
          setLoadMessage(error.message || "Unable to load saved health profile.");
        }
      }
    }

    loadHealthProfile();

    return () => {
      ignore = true;
    };
  }, [user?.user_uuid]);

  return (
    <div className="page">
      <TopBar user={user} onLogout={onLogout} />

      <section className="experience-hero">
        <div className="hero-copy-card">
          <p className="hero-badge">Wellness cockpit</p>
          <h1>Your health score should feel interpretable, not cryptic.</h1>
          <p className="hero-subtext">
            Capture the signals that matter, generate a machine-learned score, and
            turn it into practical next steps you can actually act on.
          </p>
        </div>

        <div className="info-cards">
          <div className="info-card">
            <span className="step-chip">01</span>
            <h3>Map your baseline</h3>
            <p>Demographics, body metrics, and recovery data build the model context.</p>
          </div>
          <div className="info-card">
            <span className="step-chip">02</span>
            <h3>Score the routine</h3>
            <p>Daily habits become health and lifestyle scores plus comparative signals.</p>
          </div>
          <div className="info-card">
            <span className="step-chip">03</span>
            <h3>Turn insight into action</h3>
            <p>See recommendations, key drivers, and a dashboard designed for follow-through.</p>
          </div>
        </div>
      </section>

      <section className="main-content">
        <HealthForm
          user={user}
          initialHealthData={savedHealthData}
          setResult={setResult}
          setLoadMessage={setLoadMessage}
        />
        <Results result={result} />
      </section>

      {loadMessage ? <p className="muted status-banner">{loadMessage}</p> : null}

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
