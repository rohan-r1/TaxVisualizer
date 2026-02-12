# Setup Guide

## Prerequisites

- Node.js 18+
- Rust & Cargo ([Tauri prerequisites](https://tauri.app/v2/guides/getting-started/prerequisites))
- Claude Code CLI

## Quick Start

```bash
# Clone
git clone https://github.com/rohan-r1/TaxVisualizer.git
cd TaxVisualizer

# Install dependencies
cd app && npm install

# Run the app
npm run tauri dev

# Run tests
npm test
```

## Environment Variables

Set these for Linear integration (used by `/plan`, `/execute`, `/create-issue` commands):

```bash
export LINEAR_API_KEY="lin_api_xxxx"
export LINEAR_TEAM_ID="3e9a7d7f-73b5-4c2d-99ac-58d861ac976a"
```

The Claude API key for the chatbot is configured via the in-app Settings panel.

## Custom Slash Commands

Available when running Claude Code from this directory:

| Command | Description |
|---------|-------------|
| `/create-issue` | Create a Linear issue |
| `/plan ROH-XX` | Create execution plan for an issue |
| `/execute` | Execute the current plan |
