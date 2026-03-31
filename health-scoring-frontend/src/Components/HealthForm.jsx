import { useState } from "react";

export default function HealthForm({ setResult }) {
  const [form, setForm] = useState({
    age: "",
    gender: "",
    height: "",
    weight: "",
    exercise: "",
    sleep: "",
    water: "",
    stress: "",
    smoking: "no",
    alcohol: "",
  });

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();

    const score = 78;
    const percentile = 72;

    const riskAreas = [];
    if (Number(form.exercise) < 3) riskAreas.push("Low exercise");
    if (Number(form.sleep) < 7) riskAreas.push("Low sleep");
    if (Number(form.water) < 6) riskAreas.push("Low hydration");
    if (Number(form.stress) > 7) riskAreas.push("High stress");
    if (form.smoking === "yes") riskAreas.push("Smoking habit");

    setResult({
      score,
      percentile,
      riskAreas,
      recommendations: [
        "Exercise at least 3–5 days per week",
        "Aim for 7–9 hours of sleep",
        "Stay hydrated throughout the day",
      ],
    });
  }

  return (
    <div className="form-card">
      <h2>Health Questionnaire</h2>
      <p className="muted">Enter your health information to receive your score.</p>

      <form onSubmit={handleSubmit} className="health-form">
        <input type="number" name="age" placeholder="Age" value={form.age} onChange={handleChange} />

        <select name="gender" value={form.gender} onChange={handleChange}>
          <option value="">Select Gender</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
          <option value="prefer_not_to_say">Prefer not to say</option>
        </select>

        <input type="number" name="height" placeholder="Height (inches)" value={form.height} onChange={handleChange} />
        <input type="number" name="weight" placeholder="Weight (lbs)" value={form.weight} onChange={handleChange} />
        <input type="number" name="exercise" placeholder="Exercise days per week" value={form.exercise} onChange={handleChange} />
        <input type="number" name="sleep" placeholder="Sleep hours" value={form.sleep} onChange={handleChange} />
        <input type="number" name="water" placeholder="Water cups per day" value={form.water} onChange={handleChange} />
        <input type="number" name="stress" placeholder="Stress level (1-10)" value={form.stress} onChange={handleChange} />

        <select name="smoking" value={form.smoking} onChange={handleChange}>
          <option value="no">Do you smoke? No</option>
          <option value="yes">Do you smoke? Yes</option>
        </select>

        <input type="number" name="alcohol" placeholder="Alcoholic drinks per week" value={form.alcohol} onChange={handleChange} />

        <button type="submit" className="submit-button">
          Get My Health Score
        </button>
      </form>
    </div>
  );
}