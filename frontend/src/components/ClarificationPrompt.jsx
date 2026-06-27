/**
 * Clarification prompt — surfaces the agent's disambiguation question.
 */
export default function ClarificationPrompt({ question }) {
  if (!question) return null;

  return (
    <div class="clarification-box" role="alert">
      <strong>⚠ Clarification needed</strong>
      <p style="margin-top:4px">{question}</p>
    </div>
  );
}
