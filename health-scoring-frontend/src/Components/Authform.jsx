import { useState } from "react";
import { createUser, loginUser } from "../lib/api";

export default function AuthForm({ onAuthSuccess }) {
  const [mode, setMode] = useState("signin");
  const [form, setForm] = useState({
    firstName: "",
    lastName: "",
    userId: "",
    password: "",
    confirmPassword: "",
  });
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState("idle");

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");

    if (mode === "signup" && form.password !== form.confirmPassword) {
      setMessage("Passwords do not match.");
      return;
    }

    setStatus("loading");

    try {
      const response =
        mode === "signin"
          ? await loginUser({
              id: form.userId.trim(),
              pw: form.password,
            })
          : await createUser({
              id: form.userId.trim(),
              pw: form.password,
              first: form.firstName.trim(),
              last: form.lastName.trim(),
            });

      const displayName =
        mode === "signup"
          ? `${form.firstName} ${form.lastName}`.trim()
          : (response.message || "")
              .replace(/^Welcome!\s*/i, "")
              .replace(/!+$/, "")
              .trim() || form.userId.trim();

      setMessage(response.message || "Success.");
      setStatus("success");

      onAuthSuccess({
        id: form.userId.trim(),
        name: displayName,
        user_uuid: response.user_uuid,
      });
    } catch (error) {
      setStatus("error");
      setMessage(error.message || "Authentication failed.");
    }
  }

  return (
    <div className="auth-card">
      <div className="auth-tabs">
        <button
          className={mode === "signin" ? "auth-tab active-tab" : "auth-tab"}
          type="button"
          onClick={() => {
            setMode("signin");
            setMessage("");
          }}
        >
          Sign In
        </button>
        <button
          className={mode === "signup" ? "auth-tab active-tab" : "auth-tab"}
          type="button"
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
          <>
            <input
              type="text"
              name="firstName"
              placeholder="First Name"
              value={form.firstName}
              onChange={handleChange}
              required
            />
            <input
              type="text"
              name="lastName"
              placeholder="Last Name"
              value={form.lastName}
              onChange={handleChange}
              required
            />
          </>
        )}

        <input
          type="text"
          name="userId"
          placeholder="User ID"
          value={form.userId}
          onChange={handleChange}
          required
        />

        <input
          type="password"
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          required
        />

        {mode === "signup" && (
          <input
            type="password"
            name="confirmPassword"
            placeholder="Confirm Password"
            value={form.confirmPassword}
            onChange={handleChange}
            required
          />
        )}

        <button type="submit" className="submit-button" disabled={status === "loading"}>
          {status === "loading"
            ? "Submitting..."
            : mode === "signin"
              ? "Sign In"
              : "Create Account"}
        </button>
      </form>

      {message && <p className="auth-message">{message}</p>}
    </div>
  );
}
