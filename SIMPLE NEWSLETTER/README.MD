# 📰 Slack Newsletter Automation — n8n Workflow

Automatically generate and send professional newsletters from Slack messages using AI.

---

## Overview

This workflow turns a simple Slack message into a polished email newsletter — fully automated. Post content in a Slack channel, and the system generates a newsletter, emails it to recipients, and confirms delivery back in Slack.

## Workflow

```
Slack Trigger  →  Basic LLM (OpenAI)  →  Gmail Send  →  Slack Notify
```

| Node | Purpose |
|------|---------|
| **Slack Trigger** | Listens for new messages in a designated Slack channel |
| **Basic LLM** | Transforms the raw message into a styled HTML newsletter using OpenAI |
| **Gmail** | Sends the generated newsletter to recipients |
| **Slack Notify** | Posts a confirmation message back to Slack |

## Prerequisites

- [n8n](https://n8n.io/) instance (Cloud or self-hosted)
- Slack workspace with admin access
- OpenAI API key
- Gmail account with OAuth2 configured

## Setup

### 1. Import the Workflow

1. Open n8n → **Workflows** → **⋮** (top-right) → **Import from File**
2. Select `simple_newsletter_workflow.json`
3. All 4 nodes will appear connected on the canvas

### 2. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Add Bot Token Scopes under **OAuth & Permissions**:
   - `channels:history`
   - `channels:read`
   - `chat:write`
3. Install the app to your workspace
4. Copy the **Bot User OAuth Token** (`xoxb-...`)

### 3. Configure n8n Credentials

Add three credentials in n8n (**Settings → Credentials → Add Credential**):

| Credential | What to paste |
|------------|---------------|
| **Slack OAuth2 API** | Client ID, Client Secret, and Bot Token from your Slack App |
| **OpenAI API** | API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| **Gmail OAuth2 API** | Client ID and Client Secret from [Google Cloud Console](https://console.cloud.google.com/) (Gmail API must be enabled) |

### 4. Enable Slack Event Subscriptions

> ⚠️ **Critical:** n8n must be listening BEFORE you paste the URL into Slack.

1. In n8n → Save workflow → toggle **Active ON**
2. Copy the **Production Webhook URL** from the Slack Trigger node
3. In Slack App → **Event Subscriptions** → Enable Events → paste the Production URL
4. Wait for green **Verified ✓**
5. Under **Subscribe to bot events** → add `message.channels`
6. Click **Save Changes**

### 5. Invite the Bot

In your Slack channel, type:
```
/invite @YourBotName
```

### 6. Update Placeholders

Search for `REPLACE_` in the workflow JSON and update:

| Placeholder | Replace with |
|-------------|-------------|
| `REPLACE_WITH_YOUR_CHANNEL_ID` | Your content channel ID (from Slack channel details) |
| `REPLACE_OPENAI_CREDENTIAL_ID` | Your OpenAI credential ID in n8n |
| `REPLACE_GMAIL_CREDENTIAL_ID` | Your Gmail credential ID in n8n |
| `REPLACE_SLACK_CREDENTIAL_ID` | Your Slack credential ID in n8n |
| `REPLACE_WITH_RECIPIENT_EMAILS` | Comma-separated recipient emails |
| `REPLACE_WITH_NOTIFICATION_CHANNEL_ID` | Channel ID where success notifications are posted |

## Usage

1. Go to your designated Slack channel
2. Type your newsletter content as a regular message:
   ```
   Hey team! This week we launched the new dashboard,
   fixed 12 bugs, and onboarded 3 new clients.
   Next week we focus on the mobile app release.
   ```
3. The workflow runs automatically:
   - AI generates a formatted HTML newsletter
   - Gmail sends it to all recipients
   - Slack posts a ✅ confirmation

## Testing

To test without activating production mode:

1. Toggle the workflow **Active OFF**
2. Click the Slack Trigger node → **"Listen for Test Event"**
3. Send a message in Slack
4. n8n captures it → test remaining nodes step by step

> **Note:** You cannot test and run production at the same time. Toggle Active OFF before using "Listen for Test Event".

## Customization

### Change AI Tone

Edit the system prompt in the **Basic LLM** node:

| Style | System prompt change |
|-------|---------------------|
| Formal | `"Write in a formal, corporate tone"` |
| Casual | `"Write in a friendly, conversational tone with emoji"` |
| Brief | `"Keep it under 150 words with bullet points only"` |

### Change the AI Model

In the **Basic LLM** node, swap the model:

| Model | Cost | Quality |
|-------|------|---------|
| `gpt-4o-mini` | Low | Good for most newsletters |
| `gpt-4o` | Medium | Better formatting and writing |

### Multiple Recipients

In the **Gmail** node, enter comma-separated emails:
```
alice@example.com, bob@example.com, team@company.com
```

For privacy, use BCC: set **To** as your own email and add recipients in **Options → BCC**.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Slack Trigger doesn't fire | Invite the bot: `/invite @YourBotName` |
| "challenge" verification fails | Workflow must be **Active** before pasting URL in Slack |
| Can't test — "limitations" error | Toggle **Active OFF** first, then use "Listen for Test Event" |
| OpenAI returns error | Check API key and billing at [platform.openai.com](https://platform.openai.com) |
| Gmail auth fails | Ensure Gmail API is enabled in Google Cloud Console |
| Email goes to spam | Ask recipients to mark as "Not Spam" on first receive |
| Test URL vs Production URL | Test: `webhook-test/...` (temporary). Production: `webhook/...` (permanent) |

## File Structure

```
├── simple_newsletter_workflow.json   # n8n workflow (import this)
├── simple_newsletter_setup_guide.md  # Detailed step-by-step setup
└── README.md                         # This file
```

## License

This workflow is free to use and modify for personal and commercial purposes.
