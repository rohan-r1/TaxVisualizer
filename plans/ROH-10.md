# Plan: Chatbot: always-visible input that expands on focus

**Issue:** [ROH-10](https://linear.app/rohanr/issue/ROH-10/chatbot-always-visible-input-that-expands-on-focus)
**Priority:** High
**Status:** Complete

---

## Context

Currently, the chatbot is completely hidden until the user clicks the "Chat" button in the header. This is a common pattern, but it creates friction — users have to actively seek out the chat feature rather than being invited to use it.

The goal is to make the chatbot more discoverable by always showing the input bar at the bottom of the content area. When the user clicks or focuses the input, the full panel expands to show the message history. This is similar to how Intercom and other modern chat widgets work — the entry point is always visible, but it doesn't take up space until engaged.

## Summary

Transform the chatbot from a fully hidden/shown toggle to a two-state component: **collapsed** (input-only bar always visible) and **expanded** (full panel with messages). The "Chat" header button will be removed since the input is always visible. State management moves from `App.tsx` into `ChatbotPanel.tsx`.

## Technical Approach

### Why This Approach

We're moving the `isExpanded` state *into* the `ChatbotPanel` component rather than keeping it in `App.tsx`. Here's why:

1. **Encapsulation** — The expanded/collapsed state is purely a UI concern of the chatbot itself. App doesn't need to know or care whether the chatbot is expanded.

2. **Simpler App.tsx** — We remove `chatbotOpen` state, the setter, the header button, and the conditional rendering. App just renders `<ChatbotPanel />` unconditionally.

3. **Self-contained component** — ChatbotPanel becomes fully self-managing. This makes it easier to reuse or test in isolation.

The trade-off is that if we ever need to programmatically expand/collapse the chatbot from *outside* (e.g., a keyboard shortcut), we'd need to add that capability. But for now, user-initiated expand/collapse is sufficient.

### Alternatives Considered

| Approach | Pros | Cons | Why Not |
|----------|------|------|---------|
| **Keep state in App.tsx** | Allows external control (shortcuts, other buttons) | App.tsx stays more complex; tighter coupling | Adds complexity we don't need yet |
| **CSS-only collapse** | No state changes, pure styling | Can't show/hide message history smoothly; accessibility issues | Doesn't give us the behavior we want |
| **Separate CollapsedInput component** | Clean separation of concerns | More files, more coordination between components | Over-engineering for this use case |

The chosen approach (state inside ChatbotPanel) is the simplest path that gets us the UX we want.

## Task List

- 🟢 **Add collapsed/expanded state to ChatbotPanel** — Support two visual modes
  - 🟢 Add `isExpanded` state (default: false)
  - 🟢 Render collapsed view (input + settings/minimize icons)
  - 🟢 Render expanded view (current full panel)
  - 🟢 Handle focus on input to expand
- 🟢 **Update App.tsx layout** — Always show chatbot, remove header button
  - 🟢 Remove `chatbotOpen` state and header Chat button
  - 🟢 Always render `ChatbotPanel` in content wrapper
  - 🟢 Remove `onClose` prop (panel manages itself)
- 🟢 **Add CSS for collapsed state** — Style the input-only bar
  - 🟢 Collapsed: single-row with input, settings icon, minimize icon
  - 🟢 Add expand animation
- 🟢 **Update ChatbotInput placeholder** — New text per spec
  - 🟢 Change to "Ask me anything about your tax returns!"
- 🟢 **Run tests** — Ensure no regressions (95 tests passing)

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### ChatbotPanel.tsx — Adding Dual-Mode Rendering

**Current state:**
```tsx
// ChatbotPanel always renders the full panel
// Visibility is controlled by App.tsx's conditional rendering
export function ChatbotPanel({ onClose, ... }: ChatbotPanelProps) {
  return (
    <div className="chatbot-panel">
      <div className="chatbot-header">...</div>
      <div className="chatbot-messages">...</div>
      <ChatbotInput ... />
    </div>
  );
}
```

**After this change:**
```tsx
// ChatbotPanel manages its own expanded/collapsed state
export function ChatbotPanel({ ... }: ChatbotPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Collapsed: just input bar with icons
  // Expanded: full panel (header + messages + input)
  return (
    <div className={`chatbot-panel ${isExpanded ? 'chatbot-expanded' : 'chatbot-collapsed'}`}>
      {isExpanded ? (
        // Full panel view
        <>
          <div className="chatbot-header">...</div>
          <div className="chatbot-messages">...</div>
          <ChatbotInput ... />
        </>
      ) : (
        // Collapsed input bar
        <div className="chatbot-input-bar">
          <input onFocus={() => setIsExpanded(true)} ... />
          <button onClick={onOpenSettings}>⚙️</button>
        </div>
      )}
    </div>
  );
}
```

**Why:** This keeps all chatbot UI logic in one place. The component decides how to render itself based on its internal state, rather than relying on parent to show/hide it.

### App.tsx — Simplifying the Layout

**Current state:**
```tsx
function App() {
  const [chatbotOpen, setChatbotOpen] = useState(false);

  return (
    <div className={`app ${chatbotOpen ? "chatbot-open" : ""}`}>
      <header>
        <button onClick={() => setChatbotOpen(!chatbotOpen)}>Chat</button>
      </header>
      ...
      {chatbotOpen && <ChatbotPanel onClose={() => setChatbotOpen(false)} />}
    </div>
  );
}
```

**After this change:**
```tsx
function App() {
  // No chatbotOpen state needed

  return (
    <div className="app">
      <header>
        {/* No Chat button */}
      </header>
      ...
      <ChatbotPanel /* always rendered, no onClose */ />
    </div>
  );
}
```

**Why:** App.tsx no longer needs to know about chatbot visibility. It just renders the chatbot, and the chatbot handles its own expand/collapse. This makes App.tsx simpler and the chatbot more self-contained.

### App.css — Collapsed State Styling

We need styles for two states:

**Collapsed (input bar only):**
```css
.chatbot-panel.chatbot-collapsed {
  height: auto;           /* Only as tall as content */
  min-height: unset;      /* Remove min-height constraint */
}

.chatbot-collapsed .chatbot-input-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--bg-surface);
  border-radius: 8px;
}
```

**Expanded (full panel with animation):**
```css
.chatbot-panel.chatbot-expanded {
  height: 20vh;           /* Same as current */
  animation: chatbotExpand 0.2s ease-out;
}

@keyframes chatbotExpand {
  from { height: 48px; opacity: 0.9; }
  to { height: 20vh; opacity: 1; }
}
```

**Why:** The collapsed state needs to be compact but still visually connected to the app. The animation helps users understand the state change — the panel "grows" from the input bar rather than appearing abruptly.

## Implementation Details

### Key Code Changes

**ChatbotPanel.tsx — New props interface:**
```tsx
export interface ChatbotPanelProps {
  returns: TaxReturn[];
  fields: Record<number, ExtractedField[]>;
  summaries: ReturnSummary[];
  onOpenSettings: () => void;
  // Note: onClose is REMOVED — panel manages itself
}
```

**ChatbotPanel.tsx — State and handlers:**
```tsx
export function ChatbotPanel({ returns, fields, summaries, onOpenSettings }: ChatbotPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  // ... existing state ...

  const handleInputFocus = () => setIsExpanded(true);
  const handleMinimize = () => setIsExpanded(false);

  // ... rest of component
}
```

### Data Flow

```
User clicks input → handleInputFocus() → setIsExpanded(true) → Re-render as expanded
User clicks minimize → handleMinimize() → setIsExpanded(false) → Re-render as collapsed
```

Messages persist across expand/collapse since they're stored in the component's state. The chatbot doesn't unmount — it just changes how it renders.

### New Props/Interfaces

The `ChatbotPanelProps` interface changes:

```tsx
// BEFORE
interface ChatbotPanelProps {
  returns: TaxReturn[];
  fields: Record<number, ExtractedField[]>;
  summaries: ReturnSummary[];
  onClose: () => void;        // ← REMOVED
  onOpenSettings: () => void;
}

// AFTER
interface ChatbotPanelProps {
  returns: TaxReturn[];
  fields: Record<number, ExtractedField[]>;
  summaries: ReturnSummary[];
  onOpenSettings: () => void;
  // onClose is gone — component manages its own collapse
}
```

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src/components/Chatbot/ChatbotPanel.tsx` | Add `isExpanded` state, dual-mode rendering, remove `onClose` prop |
| Modify | `app/src/components/Chatbot/ChatbotInput.tsx` | Update placeholder text |
| Modify | `app/src/App.tsx` | Remove `chatbotOpen` state, header Chat button, `onClose` prop; always render ChatbotPanel |
| Modify | `app/src/App.css` | Add `.chatbot-collapsed` and `.chatbot-expanded` styles, remove `.header-chat-btn` styles |

## Testing Strategy

### What to Test
- **Collapsed → Expanded transition** — Clicking/focusing input should expand the panel
- **Expanded → Collapsed transition** — Clicking minimize should collapse back to input bar
- **Message persistence** — Messages should remain after collapsing and re-expanding
- **Settings access in collapsed state** — Settings icon should work in collapsed view
- **Streaming still works** — API responses should still stream correctly in expanded view

### How to Verify
1. Launch app with `npm run tauri dev`
2. Verify input bar is visible at bottom immediately (no need to click anything)
3. Click the input → panel should expand with smooth animation
4. Send a message → verify response streams correctly
5. Click minimize → panel collapses, messages are preserved
6. Click input again → panel expands, previous messages still there
7. In collapsed state, click settings → settings panel opens

```bash
cd app && npm test
```

## Risks & Considerations

- **Test updates:**
  - *Impact:* Tests that check for `chatbotOpen` state or the header Chat button will fail
  - *Mitigation:* Update tests to reflect new behavior — check for `.chatbot-collapsed`/`.chatbot-expanded` classes instead

- **Animation performance:**
  - *Impact:* Height animation on slower devices might feel janky
  - *Mitigation:* Use `will-change: height` or switch to `transform`-based animation if needed

- **Keyboard accessibility:**
  - *Impact:* Tab navigation flow changes when input is always visible
  - *Mitigation:* Test tab order; ensure focus states are clear; input should be reachable naturally in tab flow

- **Mobile responsiveness:**
  - *Impact:* Collapsed input bar might need different sizing on small screens
  - *Mitigation:* Test on mobile viewport; may need media queries for padding/font-size

## Performance Implications

Minimal impact. The chatbot component is now always mounted (rather than conditionally rendered), but in collapsed state it renders very few DOM elements. The expand animation uses CSS keyframes which are GPU-accelerated. No additional API calls or data loading.

## Dependencies

None — this builds on the existing chatbot implementation from ROH-5.

## Open Questions

None currently — requirements are clear from the issue description.

---

*This plan was created by your CTO assistant. Review the approach and ask questions before we proceed to implementation.*
