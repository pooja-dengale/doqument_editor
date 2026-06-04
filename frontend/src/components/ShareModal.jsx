/**
 * ShareModal — lets a document owner grant/revoke access to other users.
 *
 * Props:
 *   document   – the full document object (needs .shares and .owner_username)
 *   activeUser – the currently logged-in user (must equal owner to see this)
 *   allUsers   – full user list fetched from /api/users/
 *   onShare    – (username, permission) => Promise
 *   onRevoke   – (username) => Promise
 *   onClose    – () => void
 */
import { useState } from 'react';

const PERMISSION_LABELS = { view: 'Can view', edit: 'Can edit' };

export default function ShareModal({ document, activeUser, allUsers, onShare, onRevoke, onClose }) {
  const [selectedUser, setSelectedUser] = useState('');
  const [permission, setPermission] = useState('view');
  const [sharing, setSharing] = useState(false);
  const [revoking, setRevoking] = useState(null); // username being revoked
  const [localError, setLocalError] = useState('');

  // Users that can be added: everyone except owner and already-shared
  const sharedUsernames = (document.shares || []).map((s) => s.shared_with_username);
  const available = allUsers.filter(
    (u) => u.username !== activeUser && !sharedUsernames.includes(u.username)
  );

  const handleShare = async () => {
    if (!selectedUser) return;
    setSharing(true);
    setLocalError('');
    try {
      await onShare(selectedUser, permission);
      setSelectedUser('');
      setPermission('view');
    } catch (e) {
      setLocalError(e?.response?.data?.detail || 'Failed to share document.');
    } finally {
      setSharing(false);
    }
  };

  const handleRevoke = async (username) => {
    setRevoking(username);
    setLocalError('');
    try {
      await onRevoke(username);
    } catch (e) {
      setLocalError(e?.response?.data?.detail || 'Failed to revoke access.');
    } finally {
      setRevoking(null);
    }
  };

  return (
    // Backdrop
    <div style={styles.backdrop} onClick={onClose} role="dialog" aria-modal="true" aria-label="Share document">
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>

        {/* Header */}
        <div style={styles.modalHeader}>
          <div>
            <h2 style={styles.modalTitle}>Share document</h2>
            <p style={styles.modalSubtitle}>{document.title || 'Untitled'}</p>
          </div>
          <button onClick={onClose} style={styles.closeBtn} aria-label="Close modal">✕</button>
        </div>

        {/* Add new share */}
        <div style={styles.addSection}>
          <p style={styles.sectionLabel}>Add people</p>
          {available.length === 0 ? (
            <p style={styles.noUsers}>All users already have access.</p>
          ) : (
            <div style={styles.addRow}>
              <select
                value={selectedUser}
                onChange={(e) => setSelectedUser(e.target.value)}
                style={styles.select}
                aria-label="Select user to share with"
              >
                <option value="">— Select a user —</option>
                {available.map((u) => (
                  <option key={u.id} value={u.username}>
                    {u.username.charAt(0).toUpperCase() + u.username.slice(1)}
                  </option>
                ))}
              </select>

              <select
                value={permission}
                onChange={(e) => setPermission(e.target.value)}
                style={{ ...styles.select, width: 120 }}
                aria-label="Permission level"
              >
                <option value="view">Can view</option>
                <option value="edit">Can edit</option>
              </select>

              <button
                onClick={handleShare}
                disabled={!selectedUser || sharing}
                style={styles.shareBtn(!selectedUser || sharing)}
                aria-label="Share with selected user"
              >
                {sharing ? 'Sharing…' : 'Share'}
              </button>
            </div>
          )}
        </div>

        {localError && <p style={styles.errorText}>⚠ {localError}</p>}

        {/* Existing shares */}
        <div style={styles.sharesSection}>
          <p style={styles.sectionLabel}>People with access</p>

          {/* Owner row */}
          <div style={styles.shareRow}>
            <div style={styles.avatar(0)}>{document.owner_username?.[0]?.toUpperCase()}</div>
            <div style={styles.shareInfo}>
              <span style={styles.shareUsername}>
                {document.owner_username}
                <span style={styles.ownerTag}> (you)</span>
              </span>
              <span style={styles.sharePermLabel}>Owner</span>
            </div>
          </div>

          {(document.shares || []).length === 0 ? (
            <p style={styles.noShares}>Not shared with anyone yet.</p>
          ) : (
            (document.shares || []).map((share, i) => (
              <div key={share.id} style={styles.shareRow}>
                <div style={styles.avatar(i + 1)}>
                  {share.shared_with_username?.[0]?.toUpperCase()}
                </div>
                <div style={styles.shareInfo}>
                  <span style={styles.shareUsername}>{share.shared_with_username}</span>
                  <span style={styles.sharePermLabel}>{PERMISSION_LABELS[share.permission]}</span>
                </div>
                <button
                  onClick={() => handleRevoke(share.shared_with_username)}
                  disabled={revoking === share.shared_with_username}
                  style={styles.revokeBtn}
                  aria-label={`Revoke ${share.shared_with_username}'s access`}
                >
                  {revoking === share.shared_with_username ? '…' : 'Revoke'}
                </button>
              </div>
            ))
          )}
        </div>

      </div>
    </div>
  );
}

// Cycle through a small palette for avatar colours
const AVATAR_PALETTE = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#3b82f6'];

const styles = {
  backdrop: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.65)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modal: {
    background: '#1e1e3a',
    border: '1px solid #2e2e4e',
    borderRadius: 12,
    width: 480,
    maxWidth: '95vw',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    gap: 20,
    boxShadow: '0 24px 48px rgba(0,0,0,0.5)',
  },
  modalHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  modalTitle: {
    fontSize: 17,
    fontWeight: 700,
    color: '#e2e8f0',
    margin: 0,
  },
  modalSubtitle: {
    fontSize: 12,
    color: '#64748b',
    marginTop: 3,
  },
  closeBtn: {
    background: 'transparent',
    border: 'none',
    color: '#64748b',
    fontSize: 16,
    cursor: 'pointer',
    padding: '2px 6px',
    borderRadius: 4,
  },
  sectionLabel: {
    fontSize: 11,
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    color: '#64748b',
    marginBottom: 10,
  },
  addSection: {
    borderTop: '1px solid #2e2e4e',
    paddingTop: 16,
  },
  addRow: {
    display: 'flex',
    gap: 8,
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  select: {
    flex: 1,
    minWidth: 140,
    background: '#16162a',
    color: '#e2e8f0',
    border: '1px solid #3e3e5e',
    borderRadius: 6,
    padding: '7px 10px',
    fontSize: 13,
    outline: 'none',
    cursor: 'pointer',
  },
  shareBtn: (disabled) => ({
    background: disabled ? '#2e2e4e' : '#6366f1',
    color: disabled ? '#475569' : '#fff',
    border: 'none',
    borderRadius: 6,
    padding: '7px 18px',
    fontSize: 13,
    fontWeight: 600,
    cursor: disabled ? 'not-allowed' : 'pointer',
    whiteSpace: 'nowrap',
  }),
  sharesSection: {
    borderTop: '1px solid #2e2e4e',
    paddingTop: 16,
  },
  shareRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '8px 0',
    borderBottom: '1px solid #16162a',
  },
  avatar: (i) => ({
    width: 32,
    height: 32,
    borderRadius: '50%',
    background: AVATAR_PALETTE[i % AVATAR_PALETTE.length],
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 13,
    fontWeight: 700,
    flexShrink: 0,
  }),
  shareInfo: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
  },
  shareUsername: {
    fontSize: 13,
    color: '#e2e8f0',
    fontWeight: 500,
  },
  ownerTag: {
    fontSize: 11,
    color: '#64748b',
    fontWeight: 400,
  },
  sharePermLabel: {
    fontSize: 11,
    color: '#64748b',
  },
  revokeBtn: {
    background: 'transparent',
    border: '1px solid #3e3e5e',
    color: '#f87171',
    borderRadius: 5,
    padding: '4px 10px',
    fontSize: 12,
    cursor: 'pointer',
  },
  noUsers: {
    fontSize: 12,
    color: '#475569',
    margin: 0,
  },
  noShares: {
    fontSize: 12,
    color: '#475569',
    margin: '8px 0 0',
  },
  errorText: {
    fontSize: 12,
    color: '#f87171',
    margin: 0,
  },
};
