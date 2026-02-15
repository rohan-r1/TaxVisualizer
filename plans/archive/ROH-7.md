# Plan: Redesign chatbot as bottom-anchored full-width panel

**Issue:** [ROH-7](https://linear.app/rohanr/issue/ROH-7/redesign-chatbot-as-bottom-anchored-full-width-panel)
**Priority:** High
**Status:** Complete

---

## Summary

Redesign the chatbot from a floating bottom-right panel to a full-width panel anchored to the bottom of the window. The panel should be ~20% of viewport height with min/max constraints, while the main content area above remains scrollable. This requires changes to the app layout structure and chatbot CSS.

## Task List

- 🟢 **Restructure app layout for bottom panel** — Modify App.tsx layout to accommodate fixed bottom panel
  - 🟢 Wrap main content in a container that respects chatbot height
  - 🟢 Add conditional class for when chatbot is open
  - 🟢 Move toggle button to header area
- 🟢 **Update chatbot panel CSS** — Change from floating to anchored layout
  - 🟢 Remove fixed positioning, use flex layout instead
  - 🟢 Set height to ~20vh with min/max constraints
  - 🟢 Make panel full-width
  - 🟢 Update animation for slide-up from bottom
  - 🟢 Add top border/shadow for visual separation
- 🟢 **Update toggle button styling** — Reposition and restyle
  - 🟢 Move from floating circle to header button
  - 🟢 Match header button styling
- 🟢 **Adjust internal chatbot layout** — Optimize for wider, shorter panel
  - 🟢 Adjust messages area height
  - 🟢 Consider side-by-side layout for input (optional)
- 🟢 **Run tests** — Ensure no regressions

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### App Layout (`app/src/App.tsx`)

Current structure:
```
.app (flex column)
├── header
├── error-banner
├── main (flex row, flex: 1)
│   ├── sidebar
│   └── content
├── chatbot-toggle (fixed)
└── chatbot-panel (fixed, conditional)
```

New structure:
```
.app (flex column, 100vh)
├── header (with toggle button)
├── error-banner
├── .app-body (flex: 1, overflow: hidden)
│   └── main (flex row, overflow-y: auto)
│       ├── sidebar
│       └── content
└── chatbot-panel (conditional, ~20vh)
```

### CSS Changes (`app/src/App.css`)

**Remove/modify:**
- `.chatbot-toggle` — Remove floating positioning, move to header
- `.chatbot-panel` — Change from `position: fixed` to flex child

**Add:**
- `.app-body` — New wrapper for scrollable content area
- `.app.chatbot-open .app-body` — Reduce height when chatbot open
- `.chatbot-panel` new styles — Full width, height: 20vh, min/max constraints

### Height Calculations

- Panel height: `20vh` (20% of viewport)
- Min height: `150px` (ensures usability on small screens)
- Max height: `300px` (prevents taking too much space on large screens)
- Content area: `calc(100vh - header - chatbot)` when open

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src/App.tsx` | Restructure layout, move toggle to header |
| Modify | `app/src/App.css` | Update chatbot and layout styles |

## Risks & Considerations

- **Responsive behavior:** The 20vh height may be too small on mobile. Min-height constraint (150px) mitigates this.

- **Content reflow:** When chatbot opens/closes, content area height changes. Using CSS transitions ensures smooth experience.

- **Message history visibility:** Shorter panel means fewer visible messages. The scrollable messages area handles this, but UX may feel different.

## Dependencies

None — standalone layout change.

## Verification

1. **Visual check:**
   - Chatbot spans full width at bottom
   - Main content scrolls independently
   - Smooth open/close animation
   - Toggle button visible in header

2. **Interaction test:**
   - Open chatbot → content area shrinks
   - Close chatbot → content area expands
   - Scroll content while chatbot is open
   - Send messages, verify layout holds

3. **Run tests:**
   ```bash
   cd app && npm test
   ```
