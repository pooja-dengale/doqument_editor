/**
 * Sidebar — document list with two clearly separated sections:
 *   • "My Documents"   — documents owned by the active user
 *   • "Shared with Me" — documents another user shared with the active user
 *
 * Also hosts the "Import File" button (.txt / .md).
 * File content is read entirely in the browser via FileReader;
 * no binary data is ever sent to the backend.
 */
import { useRef } from 'react';

function DocItem({ doc, isActive, activeUser, onSelect }) {
  const isOwned = doc.owner_username === activeUser;
  const shareEntry = doc.shares?.find((s) => s.shared_with_username === activeUser);
  const permLabel = shareEntry?.permission || 'view';

  return (
    <li
      onClick={() => onSelect(doc)}
      style={styles.listItem(isActive)}
      title={isOwned ? 'Owned by you' : `Shared by ${doc.owner_username} · ${permLabel}`}
    >
      <span style={styles.docIcon}>{isOwned ? '📄' : '🔗'}</span>
      <div style={styles.docMeta}>
        <span style={styles.docTitle(isActive)}>{doc.title || 'Untitled'}</span>
        {!isOwned && (
          <span style={styles.permBadge(permLabel)}>{permLabel}</span>
        )}
      </div>
    </li>
  );
}

export default function Sidebar({
  documents,
  activeDocId,
  onSelectDoc,
  onNewDoc,
  onImportFile,
  loading,
  activeUser,
}) {
  const fileInputRef = useRef(null);

  const myDocs = documents.filter((d) => d.owner_username === activeUser);
  const sharedDocs = documents.filter((d) => d.owner_username !== activeUser);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      // Strip .txt / .md extension for a clean default title
      const title = file.name.replace(/\.(txt|md)$/i, '');
      onImportFile({ title, text });
    };
    reader.readAsText(file);
    // Reset so the same file can be re-imported
    e.target.value = '';
  };

  return (
    <aside style={styles.sidebar}>
      {/* Top action row */}
      <div style={styles.sidebarHeader}>
        <span style={styles.sidebarTitle}>Documents</span>
        <div style={styles.actionRow}>
          {/* Hidden file input — triggered by the Import button */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md"
            style={{ display: 'none' }}
            onChange={handleFileChange}
            aria-hidden="true"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            style={styles.importBtn}
            title="Import .txt or .md file"
            aria-label="Import file"
          >
            ↑ Import
          </button>
          <button
            onClick={onNewDoc}
            style={styles.newBtn}
            title="Create a new document"
            aria-label="New document"
          >
            + New
          </button>
        </div>
      </div>

      {loading ? (
        <p style={styles.hint}>Loading…</p>
      ) : (
        <div style={styles.scrollArea}>

          {/* ── My Documents ── */}
          <p style={styles.groupLabel}>My Documents</p>
          {myDocs.length === 0 ? (
            <p style={styles.hint}>No documents yet.</p>
          ) : (
            <ul style={styles.list}>
              {myDocs.map((doc) => (
                <DocItem
                  key={doc.id}
                  doc={doc}
                  isActive={doc.id === activeDocId}
                  activeUser={activeUser}
                  onSelect={onSelectDoc}
                />
              ))}
            </ul>
          )}

          {/* ── Shared with Me ── */}
          <p style={{ ...styles.groupLabel, marginTop: 12 }}>Shared with Me</p>
          {sharedDocs.length === 0 ? (
            <p style={styles.hint}>Nothing shared yet.</p>
          ) : (
            <ul style={styles.list}>
              {sharedDocs.map((doc) => (
                <DocItem
                  key={doc.id}
                  doc={doc}
                  isActive={doc.id === activeDocId}
                  activeUser={activeUser}
                  onSelect={onSelectDoc}
                />
              ))}
            </ul>
          )}

        </div>
      )}
    </aside>
  );
}

const styles = {
  sidebar: {
    width: 240,
    minWidth: 240,
    background: '#16162a',
    borderRight: '1px solid #2e2e3e',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },
  sidebarHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '14px 16px 10px',
    borderBottom: '1px solid #2e2e3e',
    gap: 8,
  },
  sidebarTitle: {
    fontSize: 12,
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    color: '#64748b',
    whiteSpace: 'nowrap',
  },
  actionRow: {
    display: 'flex',
    gap: 6,
  },
  importBtn: {
    background: '#1e293b',
    color: '#94a3b8',
    border: '1px solid #3e3e5e',
    borderRadius: 6,
    padding: '4px 8px',
    fontSize: 11,
    fontWeight: 600,
    cursor: 'pointer',
    whiteSpace: 'nowrap',
  },
  newBtn: {
    background: '#6366f1',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    padding: '4px 10px',
    fontSize: 12,
    fontWeight: 600,
    cursor: 'pointer',
  },
  scrollArea: {
    flex: 1,
    overflowY: 'auto',
    padding: '8px 0 16px',
  },
  groupLabel: {
    fontSize: 10,
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.1em',
    color: '#334155',
    padding: '8px 16px 4px',
    margin: 0,
  },
  list: {
    listStyle: 'none',
    margin: 0,
    padding: 0,
  },
  listItem: (isActive) => ({
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    padding: '7px 16px',
    cursor: 'pointer',
    background: isActive ? '#2e2e4e' : 'transparent',
    borderLeft: isActive ? '3px solid #6366f1' : '3px solid transparent',
    transition: 'background 0.12s',
  }),
  docIcon: {
    fontSize: 13,
    flexShrink: 0,
  },
  docMeta: {
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
    overflow: 'hidden',
  },
  docTitle: (isActive) => ({
    fontSize: 13,
    color: isActive ? '#e2e8f0' : '#94a3b8',
    fontWeight: isActive ? 600 : 400,
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  }),
  permBadge: (perm) => ({
    fontSize: 10,
    color: perm === 'edit' ? '#34d399' : '#f59e0b',
    background: perm === 'edit' ? '#052e16' : '#292215',
    borderRadius: 3,
    padding: '1px 4px',
    alignSelf: 'flex-start',
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
    fontWeight: 600,
  }),
  hint: {
    fontSize: 12,
    color: '#334155',
    padding: '4px 16px',
    margin: 0,
  },
};
