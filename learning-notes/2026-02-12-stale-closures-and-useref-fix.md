# Stale Closures in React (and Why useRef Fixes Them)

**Date:** 2026-02-12
**Context:** ROH-12 bug fix — chatbot responses disappearing after streaming
**Category:** Code Pattern

---

## The Quick Answer

A "stale closure" happens when a function remembers old values from when it was created, even though those values have since changed. In our chatbot, the streaming callback updated state, but the function still saw the *original* empty string. We fixed it with `useRef` because refs are like a shared notebook — everyone always sees the current page, not a photocopy from earlier.

## The Full Explanation

### What It Is

**Closure:** When you create a function inside another function, the inner function "captures" variables from its surroundings. It's like taking a snapshot of the room and carrying it with you.

```javascript
function outer() {
  let count = 0;                    // Variable in outer scope

  function inner() {
    console.log(count);             // Inner "closes over" count
  }

  count = 5;
  inner();  // Prints 5 — inner sees the current value
}
```

**Stale Closure:** The problem arises with *async* operations. If you capture a value, then something changes it *after* you've already started running, you're stuck with the old value.

```javascript
function ChatComponent() {
  const [content, setContent] = useState("");  // Starts empty

  async function handleSend() {
    // 👆 At this moment, content = "" — function captures this

    await streamFromAPI((chunk) => {
      setContent(prev => prev + chunk);  // Updates state to "Hello world"
    });

    // 👇 But content is STILL "" in this function's view!
    saveMessage(content);  // Saves empty string 😱
  }
}
```

### Why It Exists

Closures aren't a bug — they're a fundamental JavaScript feature that makes many patterns possible (callbacks, event handlers, data privacy). The "stale" problem specifically happens because:

1. **React state is immutable** — `setContent` doesn't change `content`, it schedules a *new* value for the next render
2. **Async functions span multiple renders** — your function started in render #1, but by the time it finishes, you're on render #5
3. **The function only knows about render #1** — it has a "snapshot" from when it was created

### How It Works

Let's trace through what happened in our chatbot bug:

```
Timeline of one message send:
─────────────────────────────────────────────────────────────────

Render #1: streamingContent = ""
    │
    ▼
handleSendMessage() starts
    │  👆 Function captures streamingContent = ""
    │
    ▼
API streaming begins...
    │
    ├─▶ chunk "Hello" arrives → setStreamingContent("Hello")
    │       (triggers Render #2, but handleSendMessage still running)
    │
    ├─▶ chunk " world" arrives → setStreamingContent("Hello world")
    │       (triggers Render #3)
    │
    ▼
API streaming completes
    │
    ▼
setMessages([...prev, { content: streamingContent }])
    │  👆 But streamingContent is STILL "" in this closure!
    │
    ▼
Message saved with empty content 💥
```

**The race condition** made it worse: we added a `useEffect` to "catch" the content when loading finished, but `setIsLoading(false)` and `setStreamingContent("")` were batched together by React, so the effect often saw empty content too.

### When You'll See This Again

Watch out for stale closures when you have:

- **Async functions** that read state after an `await`
- **setTimeout/setInterval** callbacks reading state
- **Event listeners** added in useEffect that reference state
- **Callbacks passed to libraries** (streaming APIs, websockets, animation libraries)

## Code Example

**The bug (stale closure):**
```tsx
const [content, setContent] = useState("");

async function handleSend() {
  // ❌ content is captured here as ""

  await streamAPI((chunk) => {
    setContent(prev => prev + chunk);
  });

  // ❌ content is still "" — stale!
  saveMessage(content);
}
```

**The fix (useRef):**
```tsx
const [content, setContent] = useState("");
const contentRef = useRef("");  // 👈 Add a ref

async function handleSend() {
  await streamAPI((chunk) => {
    contentRef.current += chunk;        // ✅ Update ref (always current)
    setContent(contentRef.current);     // ✅ Update state (for rendering)
  });

  // ✅ contentRef.current has the real value!
  saveMessage(contentRef.current);
}
```

**Why this works:** `contentRef` is an object (`{ current: "" }`). The function captures a reference to *the object*, not the value inside. When we update `contentRef.current`, we're changing what's inside the box — and everyone holding a reference to that box sees the change.

Think of it like:
- **State:** Taking a photo of a whiteboard — your photo doesn't update when someone writes more
- **Ref:** Having the actual whiteboard in the room — you always see what's currently written

## Related Concepts

- **useRef** — React hook that creates a mutable "box" that persists across renders
- **Closure** — A function that remembers variables from where it was defined
- **React batching** — React groups multiple state updates together for performance
- **Race condition** — When the outcome depends on timing/order of operations
- **Functional updates** — Using `setState(prev => ...)` to always get the latest state

## Additional Gotcha: Functional Updates and Refs

Even with `useRef`, there's another subtle trap. Consider this code:

```typescript
setMessages((prev) => [
  ...prev,
  { content: streamingContentRef.current }  // ⚠️ Still problematic!
]);

// In finally block:
streamingContentRef.current = "";  // Clears the ref
```

**The problem:** React's functional updates don't execute immediately. When you pass `streamingContentRef.current` inside the arrow function, React captures a reference to the ref *object*, but doesn't read `.current` until it processes the state update. If the `finally` block runs first (which it does!), the ref is already empty when React reads it.

**The fix:** Capture to a local variable first:

```typescript
const finalContent = streamingContentRef.current;  // ✅ Capture NOW

setMessages((prev) => [
  ...prev,
  { content: finalContent }  // ✅ Uses captured value
]);
```

Local variables are captured by value at arrow function creation time, not dereferenced later like `.current`.

## Key Takeaway

When async code needs to read a value that might change during execution, use a `useRef` alongside state. State is for *rendering*, refs are for *reading the current value*. And when passing ref values to React state updates, capture them to local variables first to avoid timing issues with functional updates.

---

*Learning note from your CTO assistant*
