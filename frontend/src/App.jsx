/**
 * App.jsx — root component and state manager.
 *
 * Phase 3 additions:
 *   - handleImportFile: reads text from FileReader, wraps it in <p> tags,
 *     creates a new document, and opens it in the editor.
 *   - handleShare / handleRevoke: call the sharing API, then refresh the
 *     active document so the ShareModal stays in sync.
 *   - allUsers: fetched once and passed to EditorPane → ShareModal.
 */
import { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import EditorPane from './components/EditorPane';
import {
  setActiveUser,
  getDocuments,
  getDocument,
  createDocument,
  updateDocument,
  shareDocument,
  revokeShare,
  getUsers,
} from './api';

const DEFAULT_USER = 'alice';

export default function App() {
  const [activeUser, setActiveUserState] = useState(DEFAULT_USER);
  const [documents, setDocuments]         = useState([]);
  const [activeDoc, setActiveDoc]         = useState(null);
  const [allUsers, setAllUsers]           = useState([]);
  const [docsLoading, setDocsLoading]     = useState(false);
  const [saving, setSaving]               = useState(false);
  const [saveStatus, setSaveStatus]       = useState(null); // 'saved' | 'error' | null
  const [error, setError]                 = useState(null);

  // Initialise API token on mount
  useEffect(() => {
    setActiveUser(DEFAULT_USER);
    // Fetch the user list once — it doesn't change during a session
    getUsers().then((r) => setAllUsers(r.data)).catch(() => {});
  }, []);

  // Fetch documents whenever active user changes
  const fetchDocuments = useCallback(async () => {
    setDocsLoading(true);
    setError(null);
    try {
      const res = await getDocuments();
      setDocuments(res.data);
    } catch {
      setError('Failed to load documents. Is the Django server running?');
    } finally {
      setDocsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
    setActiveDoc(null);
    setSaveStatus(null);
  }, [activeUser, fetchDocuments]);

  // ── User switch ──────────────────────────────────────────────────────────
  const handleUserChange = (username) => {
    setActiveUser(username);
    setActiveUserState(username);
  };

  // ── Select document ──────────────────────────────────────────────────────
  const handleSelectDoc = async (docSummary) => {
    setSaveStatus(null);
    try {
      const res = await getDocument(docSummary.id);
      setActiveDoc(res.data);
    } catch {
      setError('Failed to load document.');
    }
  };

  // ── Create new blank document ────────────────────────────────────────────
  const handleNewDoc = async () => {
    try {
      const res = await createDocument({ title: 'Untitled Document', content: '' });
      const newDoc = res.data;
      setDocuments((prev) => [newDoc, ...prev]);
      setActiveDoc(newDoc);
      setSaveStatus(null);
    } catch {
      setError('Failed to create document.');
    }
  };

  // ── Import file (.txt / .md) ─────────────────────────────────────────────
  // FileReader runs in the browser; we receive plain text here.
  // Wrap plain-text lines in <p> so Quill renders them correctly.
  const handleImportFile = async ({ title, text }) => {
    // Convert plain-text newlines to Quill-friendly HTML paragraphs
    const content = text
      .split('\n')
      .map((line) => `<p>${line || '<br>'}</p>`)
      .join('');

    try {
      const res = await createDocument({ title, content });
      const newDoc = res.data;
      setDocuments((prev) => [newDoc, ...prev]);
      setActiveDoc(newDoc);
      setSaveStatus(null);
    } catch {
      setError('Failed to import file.');
    }
  };

  // ── Save document ────────────────────────────────────────────────────────
  const handleSave = async (id, { title, content }) => {
    setSaving(true);
    setSaveStatus(null);
    try {
      const res = await updateDocument(id, { title, content });
      const updated = res.data;
      setDocuments((prev) =>
        prev.map((d) =>
          d.id === id ? { ...d, title: updated.title, updated_at: updated.updated_at } : d
        )
      );
      setActiveDoc(updated);
      setSaveStatus('saved');
    } catch {
      setSaveStatus('error');
    } finally {
      setSaving(false);
      setTimeout(() => setSaveStatus(null), 3000);
    }
  };

  // ── Share document ───────────────────────────────────────────────────────
  const handleShare = async (docId, username, permission) => {
    await shareDocument(docId, username, permission);
    // Refresh the active doc so the ShareModal and footer chip reflect the new share
    const res = await getDocument(docId);
    setActiveDoc(res.data);
    // Also refresh the sidebar list (shared-with-me section of the other user)
    setDocuments((prev) =>
      prev.map((d) => (d.id === docId ? { ...d, shares: res.data.shares } : d))
    );
  };

  // ── Revoke share ─────────────────────────────────────────────────────────
  const handleRevoke = async (docId, username) => {
    await revokeShare(docId, username);
    const res = await getDocument(docId);
    setActiveDoc(res.data);
    setDocuments((prev) =>
      prev.map((d) => (d.id === docId ? { ...d, shares: res.data.shares } : d))
    );
  };

  return (
    <div style={styles.root}>
      <Header activeUser={activeUser} onUserChange={handleUserChange} />

      <div style={styles.body}>
        <Sidebar
          documents={documents}
          activeDocId={activeDoc?.id}
          onSelectDoc={handleSelectDoc}
          onNewDoc={handleNewDoc}
          onImportFile={handleImportFile}
          loading={docsLoading}
          activeUser={activeUser}
        />

        {error ? (
          <div style={styles.errorBanner}>
            <span>⚠️ {error}</span>
            <button onClick={() => setError(null)} style={styles.dismissBtn}>Dismiss</button>
          </div>
        ) : (
          <EditorPane
            document={activeDoc}
            onSave={handleSave}
            onShare={handleShare}
            onRevoke={handleRevoke}
            saving={saving}
            saveStatus={saveStatus}
            activeUser={activeUser}
            allUsers={allUsers}
          />
        )}
      </div>
    </div>
  );
}

const styles = {
  root: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif",
    background: '#1a1a2e',
    color: '#e2e8f0',
  },
  body: {
    display: 'flex',
    flex: 1,
    overflow: 'hidden',
  },
  errorBanner: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 16,
    color: '#f87171',
    fontSize: 14,
  },
  dismissBtn: {
    background: '#2e2e4e',
    color: '#e2e8f0',
    border: 'none',
    borderRadius: 6,
    padding: '6px 16px',
    cursor: 'pointer',
    fontSize: 13,
  },
};
