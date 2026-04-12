import { useState } from "react";
import Landingpg from "./Pages/Landingpg";
import Authpage from "./Pages/Authpage";
import Questionaire from "./Pages/Questionaire";
import "./index.css";

export default function App() {
  const [screen, setScreen] = useState("landing");
  const [user, setUser] = useState(null);

  if (screen === "landing") {
    return <Landingpg onStart={() => setScreen("auth")} />;
  }

  if (screen === "auth") {
    return (
      <Authpage
        onBack={() => setScreen("landing")}
        onAuthSuccess={(userData) => {
          setUser(userData);
          setScreen("questionnaire");
        }}
      />
    );
  }

  return (
    <Questionaire
      user={user}
      onLogout={() => {
        setUser(null);
        setScreen("landing");
      }}
    />
  );
}