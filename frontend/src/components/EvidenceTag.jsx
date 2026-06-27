/**
 * Evidence tag — collapsible evidence badge with source attribution.
 */
export default function EvidenceTag({ item }) {
  const confidenceColor =
    item.confidence >= 0.9 ? 'var(--success)' :
    item.confidence >= 0.7 ? 'var(--accent)' :
    'var(--warning)';

  return (
    <details class="evidence-tag">
      <summary>
        <span style={{ marginRight: '6px' }}>
          {item.source === 'dhis2' ? '📊' : item.source === 'tavily' ? '🌐' : '🔬'}
        </span>
        {item.claim?.slice(0, 80)}{item.claim?.length > 80 ? '…' : ''}
        <span style={{
          marginLeft: '8px',
          fontSize: '0.7rem',
          color: confidenceColor,
        }}>
          {(item.confidence * 100).toFixed(0)}%
        </span>
      </summary>
      <p>{item.claim}</p>
      {item.source_detail && (
        <p class="source-url">{item.source_detail}</p>
      )}
    </details>
  );
}
