# Plan: Add fixed-position chatbot for tax return Q&A

**Issue:** [ROH-5](https://linear.app/rohanr/issue/ROH-5/add-fixed-position-chatbot-for-tax-return-qanda)
**Priority:** High
**Status:** Complete

---

## Summary

Add an intelligent chatbot to the TaxVisualizer application that answers questions about uploaded tax returns. The chatbot will be fixed-positioned at the bottom-right corner, stay visible while scrolling, support minimize/expand with smooth animations, and integrate with an LLM API to provide context-aware answers using the user's tax data.

## Task List

- 🟢 **Create Chatbot UI components** — Build the visual chatbot interface
  - 🟢 ChatbotPanel — Main container with header, messages area, and input
  - 🟢 ChatbotMessage — Individual message bubble (user vs assistant styling)
  - 🟢 ChatbotInput — Text input with send button
  - 🟢 Barrel export (`index.ts`)
- 🟢 **Integrate chatbot into App** — Wire up chatbot to main application
  - 🟢 Add `chatbotOpen` state to App.tsx
  - 🟢 Add floating toggle button (bottom-right)
  - 🟢 Render ChatbotPanel with tax data props
- 🟢 **Add chatbot styling** — CSS for positioning, theme, animations
  - 🟢 Fixed positioning styles (bottom-right, z-index)
  - 🟢 Dark theme styling (surfaces, borders, text)
  - 🟢 Message bubble styles (user vs assistant)
  - 🟢 Minimize/expand animations (`@keyframes`, transitions)
- 🟢 **Create useChatbot hook** — Manage chat state and API interaction
  - 🟢 Messages array state management
  - 🟢 Loading/streaming state
  - 🟢 sendMessage function with error handling
- 🟢 **Build Claude API integration** — Connect to LLM with streaming
  - 🟢 Create `services/claude.ts` API client
  - 🟢 Implement streaming response handling
  - 🟢 Ephemeral calls (no data retention)
- 🟢 **Build tax context serializer** — Format data for LLM context
  - 🟢 Serialize summaries (always included)
  - 🟢 Serialize relevant fields (filtered by query)
  - 🟢 Create system prompt with tax data context
- 🟢 **Create Settings panel** — API key configuration
  - 🟢 SettingsPanel UI component
  - 🟢 useSettings hook with Tauri secure storage
  - 🟢 Settings button/gear icon in chatbot header
- 🟢 **Write unit tests** — Test components and hooks
  - 🟢 ChatbotPanel render tests
  - 🟢 useChatbot hook tests
  - 🟢 Message styling tests

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### Frontend Components (`app/src/components/`)
- Create `Chatbot/` directory with `ChatbotPanel.tsx`, `ChatbotMessage.tsx`, `ChatbotInput.tsx`
- ChatbotPanel receives tax data via props (`returns`, `fields`, `summaries`)
- Fixed position at bottom-right, independent of main layout flow

### App State (`app/src/App.tsx`)
- Add `chatbotOpen: boolean` state
- Add floating toggle button (bottom-right corner)
- Pass tax data to ChatbotPanel component
- Render ChatbotPanel outside main content flow (after `</main>`)

### Custom Hook (`app/src/hooks/`)
- Create new `hooks/` directory
- `useChatbot.ts` hook manages: messages array, loading state, sendMessage function
- Handles LLM API calls with error handling

### Styling (`app/src/App.css`)
- Add `.chatbot-toggle` button styles (fixed, bottom-right, circular, accent color)
- Add `.chatbot-panel` container (fixed position, z-index: 101, dark surface)
- Add `.chatbot-header`, `.chatbot-messages`, `.chatbot-input` sections
- Add `.chatbot-message.user` and `.chatbot-message.assistant` bubble styles
- Add `@keyframes slideUp` for open animation
- Add minimize transition (`transform`, `opacity`)

### LLM Integration
- Create `app/src/services/chatbot.ts` for API abstraction
- Serialize tax context: summaries (always), filtered fields (on demand)
- Ephemeral API calls (no data retention per privacy requirements)

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Create | `app/src/components/Chatbot/ChatbotPanel.tsx` | Main chatbot container |
| Create | `app/src/components/Chatbot/ChatbotMessage.tsx` | Message bubble component |
| Create | `app/src/components/Chatbot/ChatbotInput.tsx` | Input form with send |
| Create | `app/src/components/Chatbot/index.ts` | Barrel export |
| Create | `app/src/components/Settings/SettingsPanel.tsx` | API key configuration UI |
| Create | `app/src/components/Settings/index.ts` | Barrel export |
| Create | `app/src/hooks/useChatbot.ts` | Chat state, streaming, API hook |
| Create | `app/src/hooks/useSettings.ts` | Settings state & Tauri storage |
| Create | `app/src/services/claude.ts` | Claude API integration with streaming |
| Create | `app/src/services/taxContext.ts` | Tax data serialization for LLM |
| Modify | `app/src/App.tsx` | Add chatbot state, toggle button, render ChatbotPanel |
| Modify | `app/src/App.css` | Add chatbot and settings styles |
| Create | `app/src/components/Chatbot/__tests__/ChatbotPanel.test.tsx` | Unit tests |

## Risks & Considerations

- **LLM API Key Management:** User provides their own Claude API key.
  - *Mitigation:* Settings panel with secure Tauri storage; clear instructions for obtaining key

- **Context Window Limits:** Large tax returns with many fields may exceed LLM context limits.
  - *Mitigation:* Prioritize summaries; include detailed fields only when query requires them

- **API Latency:** LLM responses take 1-3 seconds; need good loading UX.
  - *Mitigation:* Show typing indicator, stream responses if API supports it

- **Privacy Compliance:** Must ensure ephemeral usage as per privacy principles.
  - *Mitigation:* Use APIs with no-retention policies; document clearly; no logging of tax data

- **Z-Index Conflicts:** Chatbot must float above all content without breaking existing layouts.
  - *Mitigation:* Use z-index 100-101 (currently unused in app)

## Dependencies

- Claude API (Anthropic) for LLM integration
- User provides their own API key via settings panel

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM Provider | Claude API | High quality, good instruction-following |
| API Key Setup | Settings panel in app | User-friendly, stored securely in Tauri |
| Response Style | Streaming | More responsive feel, words appear as generated |
| Context Strategy | Summaries always; fields filtered by relevance | Balance context size with detail |

## Verification

1. **Manual testing:**
   - Open app with uploaded returns
   - Click chatbot toggle → panel opens with animation
   - Type question about tax data → receive accurate response
   - Click minimize → panel collapses with animation
   - Scroll main content → chatbot stays fixed in position

2. **Unit tests:**
   - ChatbotPanel renders correctly
   - useChatbot hook manages state properly
   - Messages display with correct styling
   - Input submits and clears

3. **Run test suite:**
   ```bash
   cd app && npm test
   ```
