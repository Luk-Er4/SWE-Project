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
