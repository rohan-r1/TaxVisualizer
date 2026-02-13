# Plan: Bug: Chatbot response appears briefly then disappears

**Issue:** [ROH-12](https://linear.app/rohanr/issue/ROH-12/bug-chatbot-response-appears-briefly-then-disappears)
**Priority:** Urgent
**Status:** Complete

---

## Context

Users are experiencing a critical bug where chatbot responses appear momentarily during streaming, then vanish once streaming completes. This makes the chatbot unusable. The bug has been in the codebase since the initial chatbot implementation and involves a subtle React closure/state timing issue.

## Summary

The bug is caused by two issues working together: (1) a stale closure capturing an empty `streamingContent` value, and (2) a race condition in a useEffect that was meant to fix this. The fix is to use a `useRef` to track the accumulated content alongside the state, ensuring we always have access to the current value when adding the final message.

## Technical Approach

### Why This Approach

The core problem is that React state updates are asynchronous, and closures capture values at function creation time. When `handleSendMessage` runs:

```
1. streamingContent = "" (closure captures this)
2. Streaming starts, setStreamingContent accumulates chunks
3. Streaming ends, but streamingContent in the closure is still ""
4. We add a message with content: "" (empty!)
```

Using a `useRef` solves this because refs are mutable and always give us the current value:

```
1. streamingRef.current = ""
2. Streaming starts, we update BOTH state and ref
3. Streaming ends, streamingRef.current has the full content
4. We add a message with content: streamingRef.current (correct!)
```

### Alternatives Considered

| Approach | Pros | Cons | Why Not |
|----------|------|------|---------|
| **Pass content via callback return** | Clean, no extra ref | Requires changing claude.ts API | More invasive change, affects other code |
| **Accumulate in local variable** | Simple | Variable resets each render | Won't work with async/await |
| **Use functional setState** | React-idiomatic | Complex nesting, harder to read | Overcomplicates the code |

The `useRef` approach is the right balance: minimal change, easy to understand, and follows a common React pattern for accessing current values in closures.

## Task List

- 🟢 **Fix streaming content capture** — Use ref to track content
  - 🟢 Add `streamingContentRef` alongside existing state
  - 🟢 Update both ref and state when chunks arrive
  - 🟢 Use ref value when adding final message
- 🟢 **Remove duplicate/broken code** — Clean up the workaround
  - 🟢 Remove the broken useEffect (lines 120-134)
  - 🟢 Keep only the correct message-adding logic in handleSendMessage
- 🟢 **Run tests** — Ensure no regressions (96 tests passing)

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### ChatbotPanel.tsx — Adding a ref to track streaming content

**Current state (broken):**
```tsx
const [streamingContent, setStreamingContent] = useState("");

// In sendChatMessage callback:
(chunk) => {
  setStreamingContent((prev) => prev + chunk);  // Updates state
}

// After streaming completes:
setMessages((prev) => [
  ...prev,
  { content: streamingContent, ... }  // BUG: stale closure, always ""
]);
```

**After this change:**
```tsx
const [streamingContent, setStreamingContent] = useState("");
const streamingContentRef = useRef("");  // NEW: tracks current value

// In sendChatMessage callback:
(chunk) => {
  streamingContentRef.current += chunk;           // Update ref (synchronous)
  setStreamingContent(streamingContentRef.current); // Update state (for rendering)
}

// After streaming completes:
setMessages((prev) => [
  ...prev,
  { content: streamingContentRef.current, ... }  // FIXED: always current value
]);

// In finally block:
streamingContentRef.current = "";  // Reset ref
setStreamingContent("");           // Reset state
```

**Why:** The ref gives us a "box" that always contains the current value, regardless of when the closure was created. State is still used for rendering the streaming preview.

### Remove the broken useEffect

**Current state:**
```tsx
// Fix: capture streaming content before clearing
useEffect(() => {
  if (!isLoading && streamingContent) {
    setMessages((prev) => [...prev, { content: streamingContent, ... }]);
    setStreamingContent("");
  }
}, [isLoading, streamingContent]);
```

**After this change:**
```tsx
// REMOVED - no longer needed since handleSendMessage now works correctly
```

**Why:** This useEffect was a workaround that doesn't reliably work due to React's batched state updates. With the ref fix, we don't need it.

## Implementation Details

### Key Code Changes

**ChatbotPanel.tsx — Updated state and ref:**
```tsx
const [streamingContent, setStreamingContent] = useState("");
const streamingContentRef = useRef("");
```

**ChatbotPanel.tsx — Updated streaming callback:**
```tsx
await sendChatMessage(
  content,
  taxContext,
  messages,
  (chunk) => {
    streamingContentRef.current += chunk;
    setStreamingContent(streamingContentRef.current);
  }
);
```

**ChatbotPanel.tsx — Updated message adding (after await):**
```tsx
// After streaming completes, add the full message using REF (not state)
setMessages((prev) => [
  ...prev,
  {
    id: crypto.randomUUID(),
    role: "assistant",
    content: streamingContentRef.current,  // Use ref, not closure
    timestamp: new Date(),
  },
]);
```

**ChatbotPanel.tsx — Updated finally block:**
```tsx
finally {
  setIsLoading(false);
  streamingContentRef.current = "";  // Reset ref
  setStreamingContent("");           // Reset state
}
```

### Data Flow

```
User sends message
    ↓
setIsLoading(true), reset streamingContent & ref
    ↓
API streams chunks → callback updates BOTH ref and state
    ↓
Streaming preview renders using state (lines 213-221)
    ↓
API completes → add message using REF value (always current)
    ↓
Finally: reset ref and state, setIsLoading(false)
    ↓
Message persists in messages array ✓
```

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src/components/Chatbot/ChatbotPanel.tsx` | Add ref, fix streaming logic, remove broken useEffect |

## Testing Strategy

### What to Test
- **Message persistence** — Send a message, verify response stays visible
- **Multiple messages** — Send several messages, all should persist
- **Error handling** — API errors should still show error message
- **Streaming preview** — Text should appear progressively during streaming

### How to Verify
1. Launch app with `npm run tauri dev`
2. Open chatbot, send a message
3. Watch response stream in
4. Verify response remains after streaming completes
5. Send another message, verify both messages are visible
6. Close/reopen chatbot, verify messages persist (within session)

```bash
cd app && npm test
```

## Risks & Considerations

- **Test updates:**
  - *Impact:* None expected — the tests don't directly test streaming behavior
  - *Mitigation:* Run full test suite to confirm

- **State/ref synchronization:**
  - *Impact:* If we forget to update both, UI could desync
  - *Mitigation:* Update both in the same callback, always reset both together

## Performance Implications

None. Adding a ref has zero performance cost. The fix actually removes a useEffect, slightly reducing overhead.

## Dependencies

None — this is a self-contained bug fix in ChatbotPanel.tsx.

## Open Questions

None — the bug and fix are well-understood.

---

*This plan was created by your CTO assistant. Review the approach and ask questions before we proceed to implementation.*
