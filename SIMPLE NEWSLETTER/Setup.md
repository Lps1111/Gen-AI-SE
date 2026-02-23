# Simple Newsletter Workflow — Setup Guide

## Your Flow (4 Nodes)

```
Slack Trigger  →  Basic LLM  →  Gmail Send  →  Slack Notify
(message in)     (newsletter)    (email out)    (confirmation)
```

---

## Import the Workflow

1. Open n8n → **Workflows** → click **"⋮"** (top-right) → **Import from File**
2. Select `simple_newsletter_workflow.json`
3. All 4 nodes will appear connected on the canvas
4. **Do NOT activate yet** — configure each node first

---

## Node 1: Slack Trigger

**What it does:** Listens for new messages in your Slack channel.

### Create the Slack App (one-time setup)

1. Go to **https://api.slack.com/apps** → **Create New App** → **From scratch**
2. Name: `Newsletter Bot` → Select your workspace → **Create App**
3. Go to **OAuth & Permissions** → scroll to **Bot Token Scopes** → add these:

   | Scope | Purpose |
   |-------|---------|
   | `channels:history` | Read channel messages |
   | `channels:read` | See channel list |
   | `chat:write` | Post notifications |

4. Scroll up → **Install to Workspace** → **Allow**
5. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

### Add Slack Credential in n8n

1. In n8n → **Credentials** → **Add Credential** → search **"Slack OAuth2 API"**
2. Fill in:
   - **Client ID** — from Slack App → Basic Information → App Credentials
   - **Client Secret** — same location
   - **Access Token** — paste the `xoxb-` token
3. n8n shows an **OAuth Redirect URL** — copy it
4. Go back to Slack App → **OAuth & Permissions** → **Redirect URLs** → **Add** → paste it → **Save URLs**
5. Back in n8n → click **Sign in with Slack** → Authorize → **Save**

### Enable Event Subscriptions

> ⚠️ **CRITICAL ORDER: n8n must be listening BEFORE you paste the URL into Slack**

1. **In n8n:** Configure the Slack Trigger node with your credential
2. **In n8n:** Save the workflow → Toggle **Active** ON (top-right switch)
3. **In n8n:** Click the Slack Trigger node → copy the **Production Webhook URL**
4. **In Slack App:** Go to **Event Subscriptions** → Toggle **Enable Events** ON
5. **Paste** the production URL into **Request URL** → wait for green **Verified ✓**
6. Under **Subscribe to bot events** → **Add Bot User Event** → type and select:
   - `message.channels`
7. Click **Save Changes**
8. If you see a yellow "reinstall" banner at top → click it and approve

### Invite the Bot to Your Channel

1. In Slack, go to your newsletter channel (e.g., `#newsletter-content`)
2. Type: `/invite @Newsletter Bot`

### Get Channel ID

1. Right-click channel name → **View channel details**
2. Scroll to bottom → copy the **Channel ID** (e.g., `C04ABC123XY`)

### Configure the Node

1. Double-click **Slack Trigger** node in n8n
2. Set:
   - **Credential:** Your Slack OAuth2 credential
   - **Trigger On:** New Message
   - **Channel:** Paste your Channel ID

---

## Node 2: Basic LLM - Generate Newsletter

**What it does:** Takes the raw Slack message and transforms it into polished HTML newsletter content using OpenAI.

### Get OpenAI API Key

1. Go to **https://platform.openai.com/api-keys**
2. Click **Create new secret key** → name it `n8n` → **Create**
3. Copy the key (starts with `sk-`)

### Add OpenAI Credential in n8n

1. In n8n → **Credentials** → **Add Credential** → search **"OpenAI API"**
2. Paste your API key → **Save**

### Configure the Node

1. Double-click **Basic LLM - Generate Newsletter** node
2. Set:

   | Setting | Value |
   |---------|-------|
   | **Credential** | Your OpenAI credential |
   | **Model** | `gpt-4o-mini` (cheap & fast) or `gpt-4o` (better quality) |
   | **System Message** | Already pre-filled — tells the AI to write newsletter HTML |
   | **User Message** | Already pre-filled — passes `{{ $json.text }}` from Slack |

### Customize the AI Style (Optional)

Edit the **System Message** to change the newsletter tone:
- Professional: `"Write in a formal, corporate tone"`
- Casual: `"Write in a friendly, conversational tone with emoji"`
- Brief: `"Keep it under 150 words with bullet points only"`

### Testing

- Click **Test step** (you'll need test data from the Slack Trigger first)
- Output should have `message.content` containing HTML

---

## Node 3: Gmail - Send Newsletter

**What it does:** Sends the AI-generated newsletter via your Gmail account.

### Add Gmail Credential in n8n

1. Go to **https://console.cloud.google.com/**
2. Create a project (or select existing) → enable the **Gmail API**:
   - **APIs & Services** → **Library** → search "Gmail API" → **Enable**
3. Create OAuth2 credentials:
   - **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
   - Application type: **Web application**
   - Name: `n8n Newsletter`
   - **Authorized redirect URIs:** Add your n8n OAuth callback URL:
     - n8n Cloud: `https://app.n8n.cloud/rest/oauth2-credential/callback`
     - Self-hosted: `https://your-n8n-domain/rest/oauth2-credential/callback`
   - Click **Create** → copy **Client ID** and **Client Secret**
4. Set up **OAuth consent screen** (if not done):
   - **APIs & Services** → **OAuth consent screen**
   - User type: **External** (or Internal if Google Workspace)
   - App name: `n8n Newsletter`
   - Add your email as a test user
   - Save
5. In n8n → **Credentials** → **Add Credential** → search **"Gmail OAuth2 API"**
6. Paste Client ID and Client Secret → click **Sign in with Google** → authorize → **Save**

### Configure the Node

1. Double-click **Gmail - Send Newsletter** node
2. Set:

   | Setting | Value |
   |---------|-------|
   | **Credential** | Your Gmail OAuth2 credential |
   | **To** | Recipient emails (comma-separated), e.g. `alice@example.com, bob@example.com` |
   | **Subject** | Already set to: `📰 Newsletter - {{ new Date().toLocaleDateString() }}` |
   | **Email Type** | HTML |
   | **Message** | Already set to: `{{ $json.message.content }}` (the AI output) |

### For Multiple Recipients

Enter comma-separated emails in the **To** field:
```
subscriber1@gmail.com, subscriber2@company.com, team@startup.com
```

Or use BCC to hide recipients from each other:
- Set **To** as your own email
- In **Options** → add **BCC** → paste the subscriber list

### Gmail Sending Limits

- Regular Gmail: ~500 emails/day
- Google Workspace: ~2,000 emails/day

---

## Node 4: Slack - Notify Success

**What it does:** Posts a confirmation message to a Slack channel after the email is sent.

### Configure the Node

1. Double-click **Slack - Notify Success** node
2. Set:

   | Setting | Value |
   |---------|-------|
   | **Credential** | Same Slack OAuth2 credential from Node 1 |
   | **Resource** | Message |
   | **Operation** | Post |
   | **Channel** | Your notification channel ID (can be same or different channel) |
   | **Text** | Already pre-filled with success message |

### Customize the Notification Message

Edit the **Text** field. Example:
```
✅ Newsletter sent successfully!
📧 Recipients: team@company.com
🕐 Sent at: {{ new Date().toLocaleString() }}
```

Slack formatting:
- `*bold*` for bold
- `_italic_` for italic
- `<@USER_ID>` to mention someone
- `<#CHANNEL_ID>` to link a channel

---

## Activate & Test

1. **Save** the workflow (Ctrl+S)
2. Toggle **Active** to ON
3. Go to your Slack channel and post a message:

```
Hey team! This week we launched our new dashboard, fixed 12 bugs,
and onboarded 3 new clients. Next week focus is on mobile app release.
```

4. Watch it flow:
   - ✅ Slack Trigger catches the message
   - ✅ LLM transforms it into a polished newsletter
   - ✅ Gmail sends it to your recipients
   - ✅ Slack notification confirms delivery

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Slack Trigger doesn't fire | Bot must be invited to the channel: `/invite @Newsletter Bot` |
| "challenge" error in Event Subscriptions | Workflow must be **Active** BEFORE pasting URL into Slack |
| OpenAI returns error | Check API key and billing at platform.openai.com |
| Gmail auth fails | Make sure Gmail API is enabled in Google Cloud Console |
| Gmail "less secure app" error | You must use OAuth2, not app passwords — follow the Google Cloud setup above |
| Notification not posting | Bot must be invited to the notification channel too |
| Email goes to spam | Normal for first sends — ask recipients to mark as "Not Spam" |
