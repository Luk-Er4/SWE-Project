import { useEffect, useState } from "react";
import { fetchWelcome } from "../lib/api";

export default function LandingHero({ onStart }) {
  const [welcomeMessage, setWelcomeMessage] = useState("Educational health questionnaire");

  useEffect(() => {
    let ignore = false;

    async function loadWelcome() {
      try {
        const response = await fetchWelcome();

        if (!ignore && response.message) {
          setWelcomeMessage(response.message);
        }
      } catch {
        if (!ignore) {
          setWelcomeMessage("Educational health questionnaire");
        }
      }
    }

    loadWelcome();

    return () => {
      ignore = true;
    };
  }, []);

  return (
    <section className="hero hero-single">
      <div className="hero-text hero-text-full">
        <p className="hero-badge">{welcomeMessage}</p>
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
