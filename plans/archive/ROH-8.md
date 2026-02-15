# Plan: Update color scheme: darker background with pastel accents

**Issue:** [ROH-8](https://linear.app/rohanr/issue/ROH-8/update-color-scheme-darker-background-with-pastel-accents)
**Priority:** High
**Status:** Complete

---

## Summary

Update the app's dark mode color scheme to use a near-black background with light gray text and soft pastel accent colors for charts and interactive elements. This involves updating CSS variables in App.css and chart colors in YearOverYearChart.tsx.

## Task List

- 🟢 **Update CSS variables in App.css** — Change background, text, and accent colors
  - 🟢 Update background colors to near-black palette
  - 🟢 Update text colors to light gray scale
  - 🟢 Update accent color to pastel alternative
  - 🟢 Update semantic colors (danger, success, warning) to pastel versions
  - 🟢 Update border colors to match new palette
- 🟢 **Update chart colors** — Apply pastel palette to Recharts
  - 🟢 Update COLORS constant in YearOverYearChart.tsx
  - 🟢 Update hardcoded tooltip/grid colors to use new palette
- 🟢 **Verify all components** — Check visual consistency
  - 🟢 Test chatbot panel colors
  - 🟢 Test settings panel colors
  - 🟢 Test all widgets and buttons
- 🟢 **Run tests** — Ensure no regressions

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### CSS Variables (`app/src/App.css`)

Current → New color mapping:

| Variable | Current | New |
|----------|---------|-----|
| `--bg-primary` | `#0f1219` | `#09090b` (near-black) |
| `--bg-secondary` | `#161b26` | `#0f0f11` |
| `--bg-surface` | `#1e2433` | `#18181b` |
| `--bg-hover` | `#252d3d` | `#27272a` |
| `--border` | `#2a2f3e` | `#3f3f46` |
| `--border-subtle` | `#1f2637` | `#27272a` |
| `--text-primary` | `#f1f3f5` | `#fafafa` |
| `--text-secondary` | `#9ca3af` | `#a1a1aa` |
| `--text-muted` | `#6b7280` | `#71717a` |
| `--accent` | `#818cf8` | `#a5b4fc` (pastel lavender) |
| `--accent-hover` | `#6366f1` | `#818cf8` |
| `--danger` | `#f87171` | `#fca5a5` (pastel coral) |
| `--success` | `#4ade80` | `#86efac` (pastel mint) |
| `--warning` | `#fbbf24` | `#fcd34d` (pastel amber) |

### Chart Colors (`app/src/widgets/YearOverYearChart.tsx`)

| Metric | Current | New (Pastel) |
|--------|---------|--------------|
| Income | `#818cf8` (indigo) | `#a5b4fc` (pastel lavender) |
| Tax | `#f87171` (red) | `#fca5a5` (pastel coral) |
| Refund | `#4ade80` (green) | `#86efac` (pastel mint) |
| Amount Owed | `#fbbf24` (amber) | `#fcd34d` (pastel peach) |

Also update hardcoded colors in tooltip styling:
- `backgroundColor: "#1e2433"` → `"#18181b"`
- `border: "1px solid #313a4f"` → `"1px solid #3f3f46"`
- CartesianGrid stroke: `#2a2f3e` → `#3f3f46`

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src/App.css` | Update all CSS color variables in `:root` |
| Modify | `app/src/widgets/YearOverYearChart.tsx` | Update COLORS constant and tooltip styles |

## Risks & Considerations

- **Accessibility:** Pastel colors on dark backgrounds must maintain sufficient contrast (WCAG AA minimum 4.5:1 for text). The proposed light grays (#fafafa, #a1a1aa) on near-black (#09090b) exceed this requirement.

- **Hardcoded colors:** The YearOverYearChart has some inline color values that won't automatically update with CSS variables. These must be manually updated.

## Dependencies

None - this is a standalone visual update.

## Verification

1. **Visual inspection:**
   - Launch app with `npm run tauri dev`
   - Check all screens: empty state, with returns, chatbot open, settings open
   - Verify chart colors are pastel and readable

2. **Run tests:**
   ```bash
   cd app && npm test
   ```

3. **Contrast check:**
   - Primary text on background: #fafafa on #09090b = 19.5:1 (excellent)
   - Secondary text on background: #a1a1aa on #09090b = 9.5:1 (excellent)
