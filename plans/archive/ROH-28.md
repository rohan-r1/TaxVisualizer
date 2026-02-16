# Plan: Redesign chatbot to full-height left panel layout

**Issue:** [ROH-28](https://linear.app/rohanr/issue/ROH-28/redesign-chatbot-to-full-height-left-panel-layout)
**Priority:** High
**Status:** Complete

---

## Context

The chatbot is currently a bottom-anchored panel that expands from 48px (collapsed input bar) to max 280px (expanded). While functional, this creates usability problems:

- **Limited reading space**: 280px max height means long responses require extensive scrolling
- **Poor screen utilization**: The majority of screen real estate goes to widgets/charts, even when actively chatting
- **Friction from collapse/expand**: Users must click to expand, and clicking outside collapses the panel

The goal is to test a new layout inspired by Claude Desktop: chatbot takes the full left half of the content area with a small input at the bottom and generous space for conversation above.

## Summary

Restructure the app layout so the chatbot panel sits alongside (not below) the dashboard. The chatbot will span the full height of the content area, with messages filling most of the space and input anchored at the bottom. Widgets/charts display on the right side. The collapse/expand behavior will be removed entirely.

## Technical Approach

### Why This Approach

The current bottom-anchored layout treats the chatbot as secondary UI. The new side-by-side layout treats chatbot and dashboard as equal peers. This:

1. **Maximizes conversation space** - Full height instead of 280px max
2. **Simplifies code** - Removes collapse/expand state management
3. **Matches user expectations** - Similar to Claude Desktop, ChatGPT, and other chat UIs
4. **Improves discoverability** - Always-visible panel invites interaction

### Alternatives Considered

| Approach | Pros | Cons | Why Not |
|----------|------|------|---------|
| **Resizable splitter** | Maximum flexibility | Complex implementation, accessibility concerns | Over-engineered for MVP |
| **Toggle button to hide** | User can reclaim space | Adds state complexity, hides core feature | Chatbot is a primary feature |
| **Keep bottom panel, make taller** | Minimal changes | Still awkward for long conversations | Doesn't solve the core problem |

The chosen approach (always-visible 50/50 split) is simpler and provides a dramatically better UX with moderate code changes.

## Task List

- 🟢 **Restructure App.tsx layout** — Move ChatbotPanel to be a sibling of app-content
  - 🟢 Remove `.app-content-wrapper` div
  - 🟢 Place ChatbotPanel before Dashboard in flex row
  - 🟢 Update comment to reflect new layout
- 🟢 **Rewrite chatbot CSS** — Full-height panel styling
  - 🟢 Replace `.chatbot-panel` styles for 50% width, full height
  - 🟢 Delete `.chatbot-collapsed` and `.chatbot-expanded` styles
  - 🟢 Delete collapse/expand animations
  - 🟢 Update `.chatbot-messages` for more generous padding
  - 🟢 Add responsive breakpoint for narrow screens
- 🟢 **Simplify ChatbotPanel component** — Remove collapse/expand logic
  - 🟢 Remove `isExpanded` state
  - 🟢 Remove `collapsedInputRef` and click-outside handling
  - 🟢 Remove collapsed view conditional return
  - 🟢 Remove minimize button from header
- 🟢 **Update tests** — Adjust for new component structure
  - 🟢 Remove tests for collapse/expand behavior
  - 🟢 Add tests for new always-visible layout
- 🟢 **Manual testing** — Verify at various screen sizes (148 tests passing)

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### 1. Layout Structure (App.tsx)

The current layout nests the chatbot below the dashboard:

**Current:**
```
.app-main (flex row)
├── .app-sidebar (260px)
└── .app-content-wrapper (flex column)
    ├── .app-content (Dashboard - flex: 1)
    └── .chatbot-panel (bottom, 48-280px)
```

**After:**
```
.app-main (flex row)
├── .app-sidebar (260px)
├── .chatbot-panel (50% of remaining, full height)
└── .app-content (50% of remaining, widgets)
```

The wrapper div is removed, and chatbot becomes a direct child of `.app-main`, positioned before the content area.

### 2. CSS Restructuring (App.css)

**Delete these styles entirely:**
- `.app-content-wrapper` (lines 99-105)
- `.chatbot-collapsed` and related styles (lines 389-435)
- `.chatbot-bar-btn` (lines 438-454)
- `@keyframes chatbotCollapse` and `chatbotExpand` (lines 397-408, 464-473)

**Replace `.chatbot-panel` with:**
```css
.chatbot-panel {
  width: 50%;
  min-width: 320px;
  max-width: 600px;
  background: var(--bg-surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}
```

**Add responsive breakpoint:**
```css
@media (max-width: 1023px) {
  .app-main {
    flex-direction: column;
  }

  .chatbot-panel {
    width: 100%;
    max-width: none;
    height: 50vh;
    min-height: 300px;
    border-right: none;
    border-bottom: 1px solid var(--border);
    order: 2;
  }

  .app-content {
    order: 1;
    flex: 1;
    min-height: 300px;
  }
}
```

### 3. Component Simplification (ChatbotPanel.tsx)

**Remove these elements:**
- `isExpanded` state (line 26)
- `collapsedInputRef` (line 32)
- `panelRef` (line 33)
- Click-outside effect (lines 46-64)
- `handleCollapsedSubmit` function (lines 128-136)
- Collapsed view return block (lines 138-163)
- Minimize button (lines 181-189)

**Simplified structure:**
```tsx
export function ChatbotPanel({ ... }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  // ... (no isExpanded, no panelRef, no collapsedInputRef)

  return (
    <div className="chatbot-panel">
      <div className="chatbot-header">
        <h3>Tax Assistant</h3>
        <button onClick={onOpenSettings}>Settings</button>
      </div>
      <div className="chatbot-messages">...</div>
      <ChatbotInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
```

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src/App.tsx` | Remove wrapper div, reorder children |
| Modify | `app/src/App.css` | Rewrite chatbot section, add responsive styles |
| Modify | `app/src/components/Chatbot/ChatbotPanel.tsx` | Remove collapse/expand logic |
| Modify | `app/src/components/Chatbot/__tests__/ChatbotPanel.test.tsx` | Update tests for new structure |

## Testing Strategy

### What to Test

1. **Layout at various widths:**
   - 1440px+ (wide desktop): 50/50 split, both panels visible
   - 1024-1439px (narrow desktop): Still side-by-side
   - Below 1024px: Stacked vertically (content on top, chatbot below)

2. **Chat functionality:**
   - Messages send correctly
   - Streaming responses display in real-time
   - Auto-scroll to new messages works
   - Settings button opens settings panel

3. **Interaction:**
   - Input focuses correctly
   - Enter sends, Shift+Enter adds newline
   - Long messages wrap properly

### How to Verify

```bash
cd app && npm run dev
```

1. Open at full width - verify chatbot on left, widgets on right
2. Resize window narrower - verify responsive behavior at 1024px breakpoint
3. Send a message - verify streaming works
4. Check settings button works

```bash
cd app && npm test
```

All tests should pass after updating ChatbotPanel tests.

## Risks & Considerations

- **Dashboard visibility reduced**: Users now see dashboard at 50% width. Widgets should still be readable, but may need future adjustments for complex charts.
  - *Mitigation*: Widgets are already responsive; 50% of ~1200px is still 600px+ which is adequate.

- **Mobile/tablet experience**: Below 1024px, the layout stacks. Chatbot takes 50vh which may feel cramped.
  - *Mitigation*: 50vh with 300px minimum is reasonable. Can adjust based on user feedback.

- **Test updates required**: Existing ChatbotPanel tests check collapse/expand behavior.
  - *Mitigation*: Update tests as part of this work; tests are well-structured and changes are straightforward.

## Open Questions

None - the design is well-defined. Implementation can proceed.

---

*This plan was created by your CTO assistant. Review the approach and ask questions before we proceed to implementation.*
