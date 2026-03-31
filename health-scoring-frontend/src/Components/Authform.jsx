import { useState } from "react";

export default function AuthForm({ onAuthSuccess }) {
  const [mode, setMode] = useState("signin");
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [message, setMessage] = useState("");

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();

    if (mode === "signup" && form.password !== form.confirmPassword) {
      setMessage("Passwords do not match.");
      return;
    }

    setMessage(
      mode === "signin"
        ? "Dummy sign in successful."
        : "Dummy account created successfully."
    );

    setTimeout(() => {
      onAuthSuccess({
        name: form.name || "User",
        email: form.email,
      });
    }, 500);
  }

  return (
    <div className="auth-card">
      <div className="auth-tabs">
        <button
          className={mode === "signin" ? "auth-tab active-tab" : "auth-tab"}
          onClick={() => {
            setMode("signin");
            setMessage("");
          }}
        >
          Sign In
        </button>
        <button
          className={mode === "signup" ? "auth-tab active-tab" : "auth-tab"}
          onClick={() => {
            setMode("signup");
            setMessage("");
          }}
        >
          Sign Up
        </button>
      </div>

      <form onSubmit={handleSubmit} className="auth-form">
        {mode === "signup" && (
          <input
            type="text"
            name="name"
            placeholder="Full Name"
            value={form.name}
            onChange={handleChange}
          />
        )}

        <input
          type="email"
          name="email"
          placeholder="Email Address"
          value={form.email}
          onChange={handleChange}
        />

        <input
          type="password"
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
        />

        {mode === "signup" && (
          <input
            type="password"
            name="confirmPassword"
            placeholder="Confirm Password"
            value={form.confirmPassword}
            onChange={handleChange}
          />
        )}

        <button type="submit" className="submit-button">
          {mode === "signin" ? "Sign In" : "Create Account"}
        </button>
      </form>

      {message && <p className="auth-message">{message}</p>}
    </div>
  );
}