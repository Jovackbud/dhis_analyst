/**
 * SSE stream reader — parses Server-Sent Events from a fetch Response.
 * Handles all 8 event types defined in the spec.
 */

/**
 * Read an SSE stream from a fetch Response and invoke a callback per event.
 *
 * @param {Response} response - Fetch response with SSE body
 * @param {(type: string, data: any) => void} onEvent - Callback per event
 */
export async function readSseStream(response, onEvent) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    let currentEvent = '';
    let currentData = '';

    for (const line of lines) {
      if (line.startsWith('event: ')) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith('data: ')) {
        currentData = line.slice(6);
      } else if (line === '' && currentEvent) {
        // End of SSE block — dispatch
        try {
          const parsed = JSON.parse(currentData);
          onEvent(currentEvent, parsed);
        } catch {
          onEvent(currentEvent, currentData);
        }

        if (currentEvent === 'done') {
          reader.cancel();
          return;
        }

        currentEvent = '';
        currentData = '';
      }
    }
  }
}
