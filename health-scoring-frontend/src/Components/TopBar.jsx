export default function TopBar({ user, onLogout }) {
  return (
    <div className="topbar">
      <div>
        <p className="topbar-label">Signed in as</p>
        <h3>{user?.name || user?.email || "User"}</h3>
      </div>

      <button className="logout-button" onClick={onLogout}>
        Log Out
      </button>
    </div>
  );
}