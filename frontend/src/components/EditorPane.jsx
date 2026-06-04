/**
 * EditorPane — rich-text document editor.
 *
 * Phase 3 additions:
 *   - "Share" button (owner-only) that opens the ShareModal.
 *   - Permission enforcement: view-only users see a read-only editor
 *     and a disabled Save button; the backend also enforces this server-side.
 */
import { useState, useEffect, useRef } from 'react';
import ReactQuill from 'react-quill-new';
import 'react-quill-new/dist/quill.snow.css';
import ShareModal from './ShareModal';

const TOOLBAR_OPTIONS = [
  [{ header: [1, 2, false] }],
  ['bold', 'italic', 'underline'],
  [{ list: 'ordered' }, { list: 'bullet' }],
  ['clean'],
];

export default function EditorPane({
  document,
  onSave,
  onShare,
  onRevoke,
  onDocumentUpdated,
  saving,
  saveStatus,
  activeUser,
  allUsers,
}) {
  const [title, setTitle]         = useState('');
  const [content, setContent]     = useState('');
  const [dirty, setDirty]         = useState(false);
  const [showShare, setShowShare] = useState(false);
  const initialLoad               = useRef(true);

  // Reset state whenever a different document is opened
  useEffect(() => {
    if (document) {
      setTitle(document.title || '');
      setContent(document.content || '');
      setDirty(false);
      initialLoad.current = true;
    }
  }, [document?.id]);

  const handleContentChange = (value) => {
    setContent(value);
    if (initialLoad.current) { initialLoad.current = false; return; }
    setDirty(true);
  };

  const handleTitleChange = (e) => {
    setTitle(e.target.value);
    setDirty(true);
  };

  const handleSave = () => {
    onSave(document.id, { title, content });
    setDirty(false);
  };

  // Permission logic (mirrors backend enforcement)
  const isOwner = document?.owner_username === activeUser;
  const shareEntry = document?.shares?.find((s) => s.shared_with_username === activeUser);
  const canEdit = isOwner || shareEntry?.permission === 'edit';

  if (!document) {
    return (
      <div style={styles.empty}>
        <span style={styles.emptyIcon}>📝</span>
        <p style={styles.emptyText}>Select a document or create a new one</p>
      </div>
    );
  }

  return (
    <div style={styles.pane}>

      {/* ── Toolbar row ── */}
      <div style={styles.toolbar}>
        <input
          value={title}
          onChange={handleTitleChange}
          placeholder="Document title…"
          style={styles.titleInput}
          disabled={!canEdit}
          aria-label="Document title"
        />

        <div style={styles.toolbarRight}>
          {/* Save status badge */}
          {saveStatus && (
            <span style={styles.statusBadge(saveStatus)}>
              {saveStatus === 'saved' ? '✓ Saved' : '✗ Save failed'}
            </span>
          )}

          {/* View-only badge for shared viewers */}
          {!canEdit && (
            <span style={styles.readOnlyBadge}>View only</span>
          )}

          {/* Share button — owner only */}
          {isOwner && (
            <button
              onClick={() => setShowShare(true)}
              style={styles.shareBtn}
              aria-label="Share document"
            >
              🔗 Share
            </button>
          )}

          {/* Save button */}
          <button
            onClick={handleSave}
            disabled={saving || !canEdit || !dirty}
            style={styles.saveBtn(saving || !canEdit || !dirty)}
            aria-label="Save document"
          >
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>

      {/* ── Rich-text editor ── */}
      <div style={styles.editorWrapper}>
        <ReactQuill
          theme="snow"
          value={content}
          onChange={handleContentChange}
          readOnly={!canEdit}
          modules={{ toolbar: canEdit ? TOOLBAR_OPTIONS : false }}
          style={styles.quill}
          placeholder="Start writing…"
        />
      </div>

      {/* ── Footer meta ── */}
      <div style={styles.footer}>
        <span style={styles.meta}>
          Owner: <strong>{document.owner_username}</strong>
        </span>
        {(document.shares || []).length > 0 && (
          <span style={styles.meta}>
            Shared with:{' '}
            {document.shares.map((s) => (
              <span key={s.id} style={styles.sharedChip(s.permission)}>
                {s.shared_with_username}
              </span>
            ))}
          </span>
        )}
        {document.updated_at && (
          <span style={styles.meta}>
            Last saved: {new Date(document.updated_at).toLocaleString()}
          </span>
        )}
      </div>

      {/* ── Share modal ── */}
      {showShare && (
        <ShareModal
          document={document}
          activeUser={activeUser}
          allUsers={allUsers}
          onShare={async (username, permission) => {
            await onShare(document.id, username, permission);
          }}
          onRevoke={async (username) => {
            await onRevoke(document.id, username);
          }}
          onClose={() => setShowShare(false)}
        />
      )}
    </div>
  );
}

const styles = {
  pane: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    background: '#1a1a2e',
    overflow: 'hidden',
  },
  toolbar: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '10px 20px',
    borderBottom: '1px solid #2e2e3e',
    background: '#16162a',
  },
  titleInput: {
    flex: 1,
    background: 'transparent',
    border: 'none',
    borderBottom: '1px solid #3e3e5e',
    color: '#e2e8f0',
    fontSize: 18,
    fontWeight: 600,
    padding: '4px 0',
    outline: 'none',
  },
  toolbarRight: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    flexShrink: 0,
  },
  statusBadge: (status) => ({
    fontSize: 12,
    color: status === 'saved' ? '#10b981' : '#f87171',
    fontWeight: 600,
  }),
  readOnlyBadge: {
    fontSize: 11,
    color: '#f59e0b',
    background: '#292215',
    borderRadius: 4,
    padding: '3px 7px',
    fontWeight: 600,
  },
  shareBtn: {
    background: '#1e293b',
    color: '#94a3b8',
    border: '1px solid #3e3e5e',
    borderRadius: 6,
    padding: '6px 14px',
    fontSize: 13,
    fontWeight: 600,
    cursor: 'pointer',
  },
  saveBtn: (disabled) => ({
    background: disabled ? '#2e2e4e' : '#6366f1',
    color: disabled ? '#475569' : '#fff',
    border: 'none',
    borderRadius: 6,
    padding: '6px 18px',
    fontSize: 13,
    fontWeight: 600,
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'background 0.15s',
  }),
  editorWrapper: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },
  quill: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    color: '#e2e8f0',
    fontSize: 15,
    height: '100%',
  },
  footer: {
    display: 'flex',
    gap: 20,
    padding: '8px 20px',
    borderTop: '1px solid #2e2e3e',
    background: '#16162a',
    flexWrap: 'wrap',
    alignItems: 'center',
  },
  meta: {
    fontSize: 11,
    color: '#475569',
    display: 'flex',
    alignItems: 'center',
    gap: 4,
  },
  sharedChip: (perm) => ({
    display: 'inline-block',
    fontSize: 10,
    color: perm === 'edit' ? '#34d399' : '#f59e0b',
    background: perm === 'edit' ? '#052e16' : '#292215',
    borderRadius: 3,
    padding: '1px 5px',
    marginLeft: 2,
    fontWeight: 600,
    textTransform: 'uppercase',
  }),
  empty: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    background: '#1a1a2e',
    color: '#475569',
  },
  emptyIcon: { fontSize: 48, opacity: 0.4 },
  emptyText: { fontSize: 14, margin: 0 },
};
