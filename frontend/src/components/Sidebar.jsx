/**
 * Sidebar — conversation history list with new-chat, delete, and mobile toggle.
 */
import { useState, useCallback } from 'preact/hooks';

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffSec = Math.floor((now - then) / 1000);
  if (diffSec < 60) return 'Just now';
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  if (diffSec < 604800) return `${Math.floor(diffSec / 86400)}d ago`;
  return new Date(dateStr).toLocaleDateString();
}

export default function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
  isOpen,
  onToggle,
}) {
  const [hoveredId, setHoveredId] = useState(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);

  const handleDelete = useCallback((e, id) => {
    e.stopPropagation();
    if (confirmDeleteId === id) {
      onDelete(id);
      setConfirmDeleteId(null);
    } else {
      setConfirmDeleteId(id);
      // Auto-reset after 3s
      setTimeout(() => setConfirmDeleteId(null), 3000);
    }
  }, [confirmDeleteId, onDelete]);

  return (
    <>
      {/* Mobile overlay backdrop */}
      {isOpen && (
        <div class="sidebar-backdrop" onClick={onToggle} />
      )}

      <aside class={`sidebar ${isOpen ? 'sidebar--open' : ''}`}>
        <div class="sidebar-header">
          <div class="sidebar-brand">
            <span class="sidebar-logo">◈</span>
            <span class="sidebar-title">DHIS2 AI</span>
          </div>
          <button
            class="sidebar-close-btn"
            onClick={onToggle}
            title="Close sidebar"
            aria-label="Close sidebar"
          >
            ✕
          </button>
        </div>

        <button class="sidebar-new-btn" onClick={onNew}>
          <span class="sidebar-new-icon">+</span>
          New chat
        </button>

        <nav class="sidebar-list" aria-label="Conversation history">
          {conversations.length === 0 && (
            <p class="sidebar-empty">No conversations yet</p>
          )}
          {conversations.map((conv) => (
            <button
              key={conv.id}
              class={`sidebar-item ${conv.id === activeId ? 'sidebar-item--active' : ''}`}
              onClick={() => onSelect(conv.id)}
              onMouseEnter={() => setHoveredId(conv.id)}
              onMouseLeave={() => { setHoveredId(null); setConfirmDeleteId(null); }}
              title={conv.title}
            >
              <span class="sidebar-item-icon">💬</span>
              <span class="sidebar-item-text">
                <span class="sidebar-item-title">{conv.title}</span>
                <span class="sidebar-item-time">{timeAgo(conv.updated_at)}</span>
              </span>
              {(hoveredId === conv.id || conv.id === activeId) && (
                <button
                  class={`sidebar-item-delete ${confirmDeleteId === conv.id ? 'sidebar-item-delete--confirm' : ''}`}
                  onClick={(e) => handleDelete(e, conv.id)}
                  title={confirmDeleteId === conv.id ? 'Click again to confirm' : 'Delete conversation'}
                  aria-label="Delete conversation"
                >
                  {confirmDeleteId === conv.id ? '✓' : '🗑'}
                </button>
              )}
            </button>
          ))}
        </nav>
      </aside>
    </>
  );
}
