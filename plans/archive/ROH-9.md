# Plan: Update color scheme to match Cron.com aesthetic

**Issue:** [ROH-9](https://linear.app/rohanr/issue/ROH-9/update-color-scheme-to-match-croncom-aesthetic)
**Priority:** High
**Status:** Complete

---

## Context

The current color scheme uses pastel accents (lavender, mint, coral) on a near-black zinc palette. The user wants to update this to match the Cron.com aesthetic: warm dark brown/black backgrounds with vibrant orange-red and amber accents for a more energetic, bold look.

## Summary

Update the app's dark mode color scheme to match Cron.com's visual style. This involves changing the cold zinc blacks to warm brown-blacks, and replacing pastel accents with vibrant orange tones. The primary accent becomes orange-red (#ff4700), with amber (#ffaa00) as a secondary highlight.

## Task List

- 🟢 **Update CSS variables in App.css** — Change all color variables to Cron.com palette
  - 🟢 Update background colors from zinc blacks to warm brown-blacks
  - 🟢 Update accent colors from pastel lavender to vibrant orange
  - 🟢 Update semantic colors (danger stays coral-ish, success/warning adjust)
  - 🟢 Update border colors to warm tones
- 🟢 **Update chart colors in YearOverYearChart.tsx** — Apply new palette
  - 🟢 Update COLORS constant to use orange/amber accents
  - 🟢 Update hardcoded tooltip and grid colors
- 🟢 **Run tests** — Ensure no regressions (93 tests passed)

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### CSS Variables (`app/src/App.css`)

| Variable | Current (Pastel) | New (Cron.com) |
|----------|------------------|----------------|
| `--bg-primary` | `#09090b` (zinc) | `#0f0d0a` (warm black) |
| `--bg-secondary` | `#0f0f11` | `#161412` |
| `--bg-surface` | `#18181b` | `#1e1c18` |
| `--bg-hover` | `#27272a` | `#2a2622` |
| `--border` | `#3f3f46` | `#3d3831` |
| `--border-subtle` | `#27272a` | `#2a2622` |
| `--text-primary` | `#fafafa` | `#ffffff` |
| `--text-secondary` | `#a1a1aa` | `#cccccc` |
| `--text-muted` | `#71717a` | `#888880` |
| `--accent` | `#a5b4fc` (lavender) | `#ff4700` (orange-red) |
| `--accent-hover` | `#818cf8` | `#ff5c1a` |
| `--danger` | `#fca5a5` | `#ff6b6b` (coral red) |
| `--danger-bg` | `rgba(252,165,165,0.1)` | `rgba(255,107,107,0.1)` |
| `--success` | `#86efac` | `#4ade80` (green, keep visible) |
| `--warning` | `#fcd34d` | `#ffaa00` (amber) |
| `--warning-bg` | `rgba(252,211,77,0.1)` | `rgba(255,170,0,0.1)` |

### Chart Colors (`app/src/widgets/YearOverYearChart.tsx`)

| Metric | Current | New (Cron.com) |
|--------|---------|----------------|
| income | `#a5b4fc` | `#ff4700` (orange-red) |
| tax | `#fca5a5` | `#ff6b6b` (coral) |
| refund | `#86efac` | `#4ade80` (green) |
| owed | `#fcd34d` | `#ffaa00` (amber) |

Also update inline colors:
- CartesianGrid stroke: `#3f3f46` → `#3d3831`
- XAxis/YAxis stroke: `#71717a` → `#888880`
- Tick fill: `#a1a1aa` → `#cccccc`
- Tooltip background: `#18181b` → `#1e1c18`
- Tooltip border: `#3f3f46` → `#3d3831`

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src/App.css` | Update all CSS color variables (lines 1-18) |
| Modify | `app/src/widgets/YearOverYearChart.tsx` | Update COLORS constant and inline styles |

## Risks & Considerations

- **Accessibility:** The orange-red accent (#ff4700) on warm black (#0f0d0a) maintains good contrast (7.5:1). Text colors remain high contrast.

- **User message bubbles:** Currently use `--accent` for user messages. Orange-red will be more vibrant than pastel lavender — this is intentional for the Cron.com look.

- **Year highlights in sidebar:** The `.return-year` class uses `--accent` — will now be orange instead of lavender.

## Dependencies

None — standalone visual update.

## Verification

1. **Visual inspection:**
   - Launch app with `npm run tauri dev`
   - Verify warm brown-black backgrounds throughout
   - Verify orange-red accents on buttons, links, active states
   - Check chart renders with new color palette
   - Open chatbot, send a message — verify orange user bubbles

2. **Run tests:**
   ```bash
   cd app && npm test
   ```

3. **Key screens to check:**
   - Empty state (no returns)
   - With multiple returns uploaded
   - Chatbot open
   - Settings panel open
