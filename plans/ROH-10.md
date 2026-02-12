# Plan: Chatbot: always-visible input that expands on focus

**Issue:** [ROH-10](https://linear.app/rohanr/issue/ROH-10/chatbot-always-visible-input-that-expands-on-focus)
**Priority:** High
**Status:** Planning

---

## Context

Currently the chatbot is hidden by default and requires clicking a "Chat" button in the header to open it. This adds friction to the chat experience. The user wants the input box to always be visible at the bottom of the content area, providing a more inviting and accessible entry point. Clicking/focusing the input expands the full chatbot panel.

## Summary

Modify the chatbot to show a collapsed input-only bar by default. When the user clicks the input, it expands to the full chatbot panel with header, messages area, and input. The "Chat" button in the header will be removed since the input is always visible.

## Task List

- 🔴 **Add collapsed/expanded state to ChatbotPanel** — Support two visual modes
  - 🔴 Add `isExpanded` state (default: false)
  - 🔴 Render collapsed view (input + settings/minimize icons)
  - 🔴 Render expanded view (current full panel)
  - 🔴 Handle focus on input to expand
- 🔴 **Update App.tsx layout** — Always show chatbot, remove header button
  - 🔴 Remove `chatbotOpen` state and header Chat button
  - 🔴 Always render `ChatbotPanel` in content wrapper
  - 🔴 Pass new props for collapsed/expanded behavior
- 🔴 **Add CSS for collapsed state** — Style the input-only bar
  - 🔴 Collapsed: single-row with input, settings icon, minimize icon
  - 🔴 Add expand animation
- 🔴 **Update ChatbotInput placeholder** — New text per spec
  - 🔴 Change to "Ask me anything about your tax returns!"
- 🔴 **Run tests** — Ensure no regressions

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### ChatbotPanel.tsx

Transform from single expanded view to dual-mode component:

**Collapsed state (default):**
```tsx
<div className="chatbot-panel chatbot-collapsed">
  <form className="chatbot-input-bar">
    <input placeholder="Ask me anything..." onFocus={() => setExpanded(true)} />
    <button onClick={onOpenSettings}>⚙️</button>
  </form>
</div>
```

**Expanded state (on focus):**
```tsx
<div className="chatbot-panel chatbot-expanded">
  <div className="chatbot-header">...</div>
  <div className="chatbot-messages">...</div>
  <ChatbotInput ... />
</div>
```

**State changes:**
- Add `isExpanded` state (boolean)
- `onFocus` on input → `setExpanded(true)`
- Minimize button → `setExpanded(false)`
- Remove `onClose` prop from App.tsx (minimize just collapses, doesn't hide)

### App.tsx

**Remove:**
- `chatbotOpen` state
- `setChatbotOpen` calls
- Header Chat button (`header-chat-btn`)
- `chatbot-open` class on `.app`

**Change:**
- Always render `<ChatbotPanel ... />` (unconditionally)
- Remove `onClose` prop (panel manages its own collapsed/expanded state)

### App.css

**Add collapsed state styles:**
```css
.chatbot-panel.chatbot-collapsed {
  height: auto;
  min-height: unset;
  max-height: unset;
}

.chatbot-collapsed .chatbot-input-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
}
```

**Add expand animation:**
```css
.chatbot-panel.chatbot-expanded {
  animation: chatbotExpand 0.2s ease;
}

@keyframes chatbotExpand {
  from { height: 50px; }
  to { height: 20vh; }
}
```

**Remove:**
- `.header-chat-btn` styles
- `.app.chatbot-open .header-chat-btn` styles

### ChatbotInput.tsx

Change placeholder from `"Ask about your tax returns..."` to `"Ask me anything about your tax returns!"`

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src/components/Chatbot/ChatbotPanel.tsx` | Add collapsed/expanded dual-mode rendering |
| Modify | `app/src/components/Chatbot/ChatbotInput.tsx` | Update placeholder text |
| Modify | `app/src/App.tsx` | Remove header Chat button, always render chatbot |
| Modify | `app/src/App.css` | Add collapsed styles, remove header chat button styles |

## Risks & Considerations

- **Test updates:** Tests that check for `chatbotOpen` state or header Chat button will need updating
- **Animation smoothness:** Height animation from collapsed → expanded may need fine-tuning
- **Keyboard accessibility:** Ensure Tab navigation still works correctly with always-visible input

## Dependencies

None — builds on existing chatbot implementation.

## Verification

1. **Visual inspection:**
   - Launch app → input bar visible at bottom immediately
   - Click input → full panel expands with smooth animation
   - Click minimize → returns to collapsed input-only bar
   - Settings icon opens settings panel

2. **Interaction test:**
   - Type message in collapsed state → panel expands automatically
   - Send message → works normally
   - Close/minimize → returns to collapsed
   - Verify messages persist between expand/collapse

3. **Run tests:**
   ```bash
   cd app && npm test
   ```
