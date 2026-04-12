import LandingPage from "../Components/LandingPage";

export default function Landingpg({ onStart }) {
  return (
    <div className="page">
      <LandingPage onStart={onStart} />
    </div>
  );
}