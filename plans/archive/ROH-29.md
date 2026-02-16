# Plan: Collapsible sidebar with hover-to-expand behavior

**Issue:** [ROH-29](https://linear.app/rohanr/issue/ROH-29/collapsible-sidebar-with-hover-to-expand-behavior)
**Priority:** High
**Status:** Complete

---

## Context

The left sidebar (returns list) currently occupies a fixed 260px width. Once tax returns are uploaded, users rarely need the full filename and filing status visible at all times — they primarily need to know which years they have uploaded. This 260px permanently reduces space available for the chatbot and dashboard widgets.

The goal is to make the sidebar collapse to a narrow width by default (showing just year badges), then smoothly expand to full width when the user hovers over it.

## Summary

Add CSS-driven collapse/expand behavior to the sidebar using hover state. The collapsed state shows only year badges (~64px wide), while hover expands to full 260px. Smooth CSS transitions handle both directions. The ReturnsList component gets conditional styling to hide/show text elements based on sidebar state.

## Technical Approach

### Why This Approach

**Pure CSS solution with `:hover`** — No JavaScript state management needed. CSS transitions handle the animation automatically. The browser natively tracks hover state, making this simpler and more performant than adding React state.

The key insight: we don't need React to know if the sidebar is expanded. CSS can handle both the width change AND the visibility of text elements through a single `:hover` selector cascade.

### Alternatives Considered

| Approach | Pros | Cons | Why Not |
|----------|------|------|---------|
| **React state + onClick toggle** | Explicit control, persists across hover | More code, needs state management | Over-engineered for hover-only UX |
| **CSS :hover with JS fallback** | Handles touch devices | Added complexity | Desktop-first app, can add later |
| **Resize handle (draggable)** | User-controlled width | Complex to implement, accessibility issues | User requested hover behavior |

The pure CSS approach is simplest, matches the request exactly, and aligns with existing transition patterns in the codebase (0.12s-0.15s ease timing).

## Task List

- 🟢 **Update sidebar CSS for collapse/expand** — Add hover-triggered width transition
  - 🟢 Change default width from 260px to 64px
  - 🟢 Add `:hover` state that expands to 260px
  - 🟢 Add smooth transition (0.2s ease) for width changes
  - 🟢 Handle overflow for collapsed content
- 🟢 **Update ReturnsList styling** — Show/hide elements based on sidebar state
  - 🟢 Hide filename and status in collapsed state
  - 🟢 Show only year badge when collapsed
  - 🟢 Fade in text elements on expand
- 🟢 **Update UploadButton for collapsed state** — Compact icon-only version
  - 🟢 Hide text, show "+" icon only when collapsed
  - 🟢 Full text visible on expand
- 🟢 **Update section header** — Hide "Uploaded Returns" text when collapsed
- 🟢 **Test transitions** — Verify smooth animation in both directions

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### 1. Sidebar Width States (App.css)

**Current:**
```css
.app-sidebar {
  width: 260px;
  min-width: 260px;
  /* Always 260px */
}
```

**After:**
```css
.app-sidebar {
  width: 64px;
  min-width: 64px;
  transition: width 0.2s ease, min-width 0.2s ease;
  overflow: hidden;
}

.app-sidebar:hover {
  width: 260px;
  min-width: 260px;
}
```

**Why:** The transition property enables smooth animation. The 64px collapsed width fits year badges (2.75rem ≈ 44px) plus padding.

### 2. Return Item Text Visibility (App.css)

**Current:** All elements always visible

**After:**
```css
/* Hide text elements by default (collapsed) */
.return-filename,
.return-status,
.delete-btn {
  opacity: 0;
  width: 0;
  overflow: hidden;
  transition: opacity 0.15s ease, width 0.15s ease;
}

/* Show on sidebar hover (expanded) */
.app-sidebar:hover .return-filename,
.app-sidebar:hover .return-status {
  opacity: 1;
  width: auto;
}

.app-sidebar:hover .return-item:hover .delete-btn {
  opacity: 1;
}
```

**Why:** Using opacity + width allows text to fade in/out smoothly while the sidebar expands. The delete button remains hover-gated even when expanded.

### 3. Upload Button Collapsed State

**Current:** Full text "Upload Tax Return"

**After:** Show just "+" when collapsed, full text on hover.

```css
.app-sidebar .upload-btn {
  white-space: nowrap;
  overflow: hidden;
  transition: width 0.2s ease;
}

/* Collapsed: icon only */
.app-sidebar .upload-btn span {
  opacity: 0;
  transition: opacity 0.15s ease;
}

/* Expanded: show text */
.app-sidebar:hover .upload-btn span {
  opacity: 1;
}
```

This requires a small JSX change to wrap the text in a span while keeping the "+" visible.

### 4. Section Header

```css
.returns-list h3 {
  white-space: nowrap;
  overflow: hidden;
  opacity: 0;
  transition: opacity 0.15s ease;
}

.app-sidebar:hover .returns-list h3 {
  opacity: 1;
}
```

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src/App.css` | Add collapsed/expanded width states, transitions |
| Modify | `app/src/components/UploadButton.tsx` | Wrap text in span for separate visibility control |

## Testing Strategy

### What to Test

1. **Collapse animation** — Sidebar smoothly shrinks when mouse leaves
2. **Expand animation** — Sidebar smoothly grows when mouse enters
3. **Year badges visible** — Years remain readable in collapsed state
4. **Text fade in** — Filename/status fade in smoothly during expand
5. **Upload button** — Shows "+" when collapsed, full text when expanded
6. **No layout jank** — Main content area adjusts smoothly

### How to Verify

```bash
cd app && npm run dev
```

1. Load app with tax returns uploaded
2. Move mouse away from sidebar — should collapse to ~64px showing only years
3. Hover over sidebar — should expand to 260px with smooth animation
4. Verify text fades in during expansion
5. Click upload button in collapsed state — should still work
6. Resize window — verify responsive behavior still works

```bash
cd app && npm test
```

## Risks & Considerations

- **Touch devices**: Pure CSS hover won't work on tablets. Acceptable for this desktop-first app; can add tap-to-toggle later if needed.
  - *Mitigation*: The sidebar will just stay at default width on touch devices.

- **Transition timing**: If expand/collapse feels too fast or slow, may need tuning.
  - *Mitigation*: Use 0.2s as starting point (matches existing patterns), adjust based on feel.

- **Content reflow**: Chatbot and dashboard width changes as sidebar expands.
  - *Mitigation*: Flex layout already handles this; smooth sidebar transition means smooth content adjustment.

## Open Questions

None — the design is straightforward CSS-only implementation.

---

*This plan was created by your CTO assistant. Review the approach and ask questions before we proceed to implementation.*
