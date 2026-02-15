# Plan: Move upload button to left sidebar (below returns list)

**Issue:** [ROH-11](https://linear.app/rohanr/issue/ROH-11/move-upload-button-to-left-sidebar-below-returns-list)
**Priority:** High
**Status:** Complete

---

## Context

The upload button is currently in the app header. As the app matures, it makes more sense to co-locate the upload action with the returns list in the sidebar. This creates a clearer information hierarchy: the sidebar becomes the "returns management" area (view, upload, delete), while the header remains minimal with just branding.

## Summary

Move the `<UploadButton>` from the header to the sidebar, positioning it below the returns list. Remove the now-empty header actions area. Add sidebar-specific styling for the button.

## Technical Approach

### Why This Approach

Keep the `UploadButton` rendered in `App.tsx` (not inside `ReturnsList`) because:
1. The `handleFileSelected` callback is defined in `App.tsx`
2. The button should appear even when no returns exist (empty state)
3. Keeps component responsibilities clear: `ReturnsList` displays returns, `App.tsx` manages layout

### Alternatives Considered

| Approach | Pros | Cons | Why Not |
|----------|------|------|---------|
| Pass button as prop to ReturnsList | Encapsulates sidebar | Coupling, ReturnsList shouldn't know about uploads | Over-engineering |
| Create new SidebarActions component | Clean separation | Another component for 1 button | Over-engineering |
| **Keep in App.tsx, move to sidebar** | Simple, clear | None | **Chosen** |

## Task List

- 🟢 **Move UploadButton to sidebar** — Relocate from header to sidebar area
  - 🟢 Remove from `.app-header-actions`
  - 🟢 Add after `<ReturnsList>` in `.app-sidebar`
- 🟢 **Clean up header** — Remove empty actions div
- 🟢 **Add sidebar button styling** — Full-width button with spacing
- 🟢 **Update tests** — Ensure tests still pass after layout change

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### App.tsx Layout

**Current:**
```tsx
<header className="app-header">
  <h1>TaxVisualizer</h1>
  <div className="app-header-actions">
    <UploadButton onFileSelected={handleFileSelected} />  {/* HERE */}
  </div>
</header>
...
<aside className="app-sidebar">
  <ReturnsList returns={returns} onDelete={handleDelete} />
</aside>
```

**After:**
```tsx
<header className="app-header">
  <h1>TaxVisualizer</h1>
  {/* Header actions removed - just branding now */}
</header>
...
<aside className="app-sidebar">
  <ReturnsList returns={returns} onDelete={handleDelete} />
  <UploadButton onFileSelected={handleFileSelected} />  {/* MOVED HERE */}
</aside>
```

### CSS Changes

**New sidebar button style:**
```css
/* Sidebar upload button - full width below returns */
.app-sidebar .upload-btn {
  width: 100%;
  margin-top: 1rem;
}
```

**Optional cleanup:**
```css
/* Remove if no longer needed */
.app-header-actions { ... }
```

## Files to Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src/App.tsx` | Move UploadButton from header to sidebar |
| Modify | `app/src/App.css` | Add sidebar-specific button styling |

## Testing Strategy

### What to Test
- Upload button appears in sidebar below returns list
- Upload functionality still works (clicking opens file dialog)
- Header displays only the app title
- Empty state works (button shows even with no returns)

### How to Verify

```bash
# Run existing tests
cd app && npm test

# Manual verification
cd app && npm run tauri dev
# 1. Verify button is in sidebar
# 2. Click button, upload a PDF
# 3. Confirm extraction works
```

## Risks & Considerations

- **Low risk:** This is a simple layout change with no logic modifications
- **Test impact:** App.test.tsx may need adjustment if it queries button location

## Dependencies

None — this is a standalone UI change.

---

*This plan was created by your CTO assistant. Review the approach and ask questions before we proceed to implementation.*
