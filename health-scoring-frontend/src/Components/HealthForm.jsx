import { useEffect, useRef, useState } from "react";
import { createDashboard, predictHealth, updateUserHealth } from "../lib/api";
import FormSection from "./FormSection";

const initialForm = {
  age: "",
  gender: "",
  smoking: "Never",
  activity: "",
  sleep: "",
  height: "",
  weight: "",
  stressLevel: "",
  profession: "",
  education: "",
  diet: "",
  diseases: "",
  country: "",
};

function normalizeEducationValue(value) {
  const normalized = value?.trim().toLowerCase();

  if (!normalized) {
    return "";
  }

  if (normalized === "highschool" || normalized === "high school") {
    return "Highschool";
  }

  if (normalized === "some college") {
    return "some college";
  }

  if (
    normalized === "bachelor's degree" ||
    normalized === "bachelors" ||
    normalized === "bachelor"
  ) {
    return "Bachlores";
  }

  if (normalized === "masters" || normalized === "master's degree") {
    return "Masters";
  }

  if (normalized === "phd" || normalized === "ph.d" || normalized === "doctorate") {
    return "PHD";
  }

  return "";
}

function calculateBmi(height, weight) {
  const normalizedHeight = Number(height);
  const normalizedWeight = Number(weight);

  if (!normalizedHeight || !normalizedWeight) {
    return 0;
  }

  return (703 * normalizedWeight) / (normalizedHeight ** 2);
}

function normalizeSavedHealthData(saved) {
  if (!saved) {
    return initialForm;
  }

  return {
    age: saved.age?.toString() || "",
    gender: saved.gender || "",
    smoking: saved.smoking || "Never",
    activity: saved.activity?.toString() || "",
    sleep: saved.sleep?.toString() || "",
    height: "",
    weight: "",
    stressLevel: saved.stress_level?.toString() || "",
    profession: saved.profession || "",
    education: normalizeEducationValue(saved.education),
    diet: saved.diet?.toString() || "",
    diseases: saved.diseases?.toString() || "",
    country: saved.country || "",
  };
}

function transformPredictionResult(apiResult) {
  return {
    health_risk_score: apiResult.Health_Prediction?.Health_Score,
    lifestyle_score: apiResult.Lifestyle_Prediction?.Health_Score,
    top_health_factors: (apiResult.Health_Feature_Importance || []).slice(0, 5),
    top_lifestyle_factors: (apiResult.Lifestyle_Feature_Importance || []).slice(0, 5),
  };
}

export default function HealthForm({
  user,
  initialHealthData,
  setResult,
  setLoadMessage,
}) {
  const [form, setForm] = useState(initialForm);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const hasHydratedProfile = useRef(false);
  const hasUserEdited = useRef(false);

  useEffect(() => {
    if (!initialHealthData || hasHydratedProfile.current || hasUserEdited.current) {
      return;
    }

    setForm(normalizeSavedHealthData(initialHealthData));
    hasHydratedProfile.current = true;
  }, [initialHealthData]);

  function handleChange(e) {
    const { name, value } = e.target;
    hasUserEdited.current = true;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setStatus("loading");
    setError("");

    const bmi = calculateBmi(form.height, form.weight);
    const payload = {
      age: Number(form.age),
      gender: form.gender,
      smoking: form.smoking,
      activity: Number(form.activity),
      sleep: Number(form.sleep),
      height: Number(form.height),
      weight: Number(form.weight),
      profession: form.profession.trim(),
      education: form.education,
      diet: Number(form.diet),
      diseases: Number(form.diseases),
      country: form.country.trim(),
    };

    try {
      const prediction = await predictHealth(payload);
      const normalizedResult = {
        ...transformPredictionResult(prediction),
        bmi,
      };

      try {
        const dashboardResponse = await createDashboard({
          user_name: user?.name || user?.id || "User",
          sleep_hours: payload.sleep,
          physical_activity: payload.activity,
          diet_calories: payload.diet,
          health_risk: normalizedResult.health_risk_score,
          health_score: normalizedResult.lifestyle_score,
        });

        normalizedResult.dashboard_summary = dashboardResponse.summary;
        normalizedResult.dashboard_figure = dashboardResponse.figure;
      } catch (dashboardError) {
        normalizedResult.dashboard_summary =
          dashboardError.message || "Dashboard summary unavailable.";
      }

      setResult(normalizedResult);

      if (user?.user_uuid) {
        try {
          const updateResponse = await updateUserHealth({
            user_uuid: user.user_uuid,
            age: payload.age,
            gender: payload.gender,
            smoking: payload.smoking,
            activity: payload.activity,
            sleep: payload.sleep,
            bmi,
            stress_level: Number(form.stressLevel),
            profession: payload.profession,
            education: payload.education,
            diet: payload.diet,
            diseases: payload.diseases,
            country: payload.country,
          });

          setLoadMessage?.(updateResponse.message || "Updated your saved health profile.");
        } catch (updateError) {
          setLoadMessage?.(
            updateError.message ||
              "Health score generated, but saving your profile did not complete."
          );
        }
      }

      setStatus("success");
    } catch (err) {
      setResult(null);
      setStatus("error");
      setError(err.message || "Unable to generate your health score.");
    }
  }

  return (
    <div className="form-card">
      <div className="panel-heading">
        <p className="panel-kicker">Questionnaire</p>
        <h2>Build your health snapshot</h2>
        <p className="muted">
          Move through the sections below to generate a richer, ML-backed read on
          your current routine.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="health-form">
        <FormSection
          eyebrow="Section 01"
          title="Identity and profile"
          description="Start with the core demographic details the model uses to anchor your comparison group."
        >
          <input
            type="number"
            name="age"
            placeholder="Age"
            value={form.age}
            onChange={handleChange}
            min="1"
            required
          />

          <select name="gender" value={form.gender} onChange={handleChange} required>
            <option value="">Select Gender</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
          </select>

          <input
            type="text"
            name="profession"
            placeholder="Profession"
            value={form.profession}
            onChange={handleChange}
            required
          />

          <select
            name="education"
            value={form.education}
            onChange={handleChange}
            required
          >
            <option value="">Education Level</option>
            <option value="Highschool">Highschool</option>
            <option value="some college">Some college</option>
            <option value="Bachlores">Bachelors</option>
            <option value="Masters">Masters</option>
            <option value="PHD">PHD</option>
          </select>

          <input
            type="text"
            name="country"
            placeholder="Country"
            value={form.country}
            onChange={handleChange}
            required
          />
        </FormSection>

        <FormSection
          eyebrow="Section 02"
          title="Body and recovery"
          description="These metrics shape how the model interprets your current condition and recovery quality."
        >
          <input
            type="number"
            name="height"
            placeholder="Height (inches)"
            value={form.height}
            onChange={handleChange}
            min="1"
            required
          />

          <input
            type="number"
            name="weight"
            placeholder="Weight (lbs)"
            value={form.weight}
            onChange={handleChange}
            min="1"
            required
          />

          <input
            type="number"
            name="sleep"
            placeholder="Sleep hours per night"
            value={form.sleep}
            onChange={handleChange}
            min="0"
            required
          />

          <input
            type="number"
            name="stressLevel"
            placeholder="Stress level (1-10)"
            value={form.stressLevel}
            onChange={handleChange}
            min="0"
            max="10"
            required
          />

          <input
            type="number"
            name="diseases"
            placeholder="Current disease count"
            value={form.diseases}
            onChange={handleChange}
            min="0"
            required
          />
        </FormSection>

        <FormSection
          eyebrow="Section 03"
          title="Lifestyle signals"
          description="Daily habits and behavior patterns are what drive most of the recommendations you’ll see."
        >
          <select name="smoking" value={form.smoking} onChange={handleChange}>
            <option value="Never">Never smoked</option>
            <option value="Low">Low smoking frequency</option>
            <option value="Medium">Medium smoking frequency</option>
            <option value="High">High smoking frequency</option>
          </select>

          <input
            type="number"
            name="activity"
            placeholder="Activity hours per day"
            value={form.activity}
            onChange={handleChange}
            min="0"
            required
          />

          <input
            type="number"
            name="diet"
            placeholder="Calories per day"
            value={form.diet}
            onChange={handleChange}
            min="0"
            required
          />
        </FormSection>

        <button type="submit" className="submit-button" disabled={status === "loading"}>
          {status === "loading" ? "Generating Score..." : "Get My Health Score"}
        </button>
      </form>

      {error ? <p className="auth-message error-text">{error}</p> : null}
      {initialHealthData ? (
        <p className="muted helper-text">
          Saved profile data was loaded, but height and weight are not returned by the
          backend, so you&apos;ll need to enter them again before generating a score.
        </p>
      ) : null}
      <p className="muted helper-text">
        The model expects values close to the training data, such as `Female`,
        `Never`, `Engineer`, `Bachlores`, and `United States`.
      </p>
    </div>
  );
}
