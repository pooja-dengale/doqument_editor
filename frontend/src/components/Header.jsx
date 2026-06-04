/**
 * Header — top navigation bar.
 *
 * Contains the app title and a user-switcher dropdown.
 * The dropdown acts as mock authentication: selecting a user
 * updates the API token and re-fetches documents scoped to that user.
 */
const USERS = ['alice', 'bob', 'charlie'];

const AVATAR_COLORS = {
  alice:   '#6366f1',
  bob:     '#10b981',
  charlie: '#f59e0b',
};

export default function Header({ activeUser, onUserChange }) {
  return (
    <header style={styles.header}>
      <div style={styles.brand}>
        <span style={styles.logo}>📝</span>
        <span style={styles.title}>AjaiaDoc</span>
      </div>

      <div style={styles.userSwitcher}>
        <span style={styles.switcherLabel}>Active user:</span>
        <div style={styles.avatarCircle(activeUser)}>
          {activeUser[0].toUpperCase()}
        </div>
        <select
          value={activeUser}
          onChange={(e) => onUserChange(e.target.value)}
          style={styles.select}
          aria-label="Switch active user"
        >
          {USERS.map((u) => (
            <option key={u} value={u}>
              {u.charAt(0).toUpperCase() + u.slice(1)}
            </option>
          ))}
        </select>
      </div>
    </header>
  );
}

const styles = {
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 24px',
    height: 56,
    background: '#1e1e2e',
    borderBottom: '1px solid #2e2e3e',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  brand: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
  },
  logo: {
    fontSize: 22,
  },
  title: {
    fontSize: 18,
    fontWeight: 700,
    color: '#e2e8f0',
    letterSpacing: '-0.3px',
  },
  userSwitcher: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
  },
  switcherLabel: {
    fontSize: 13,
    color: '#94a3b8',
  },
  avatarCircle: (user) => ({
    width: 30,
    height: 30,
    borderRadius: '50%',
    background: AVATAR_COLORS[user] || '#6366f1',
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 13,
    fontWeight: 700,
  }),
  select: {
    background: '#2e2e3e',
    color: '#e2e8f0',
    border: '1px solid #3e3e5e',
    borderRadius: 6,
    padding: '4px 8px',
    fontSize: 13,
    cursor: 'pointer',
    outline: 'none',
  },
};
