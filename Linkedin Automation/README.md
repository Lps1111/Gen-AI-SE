# 🚀 NIFTY50 LinkedIn Automation — N8N Workflow

> Automatically post the **Evolution Story** of every NIFTY 50 company on LinkedIn — daily, hands-free, with AI-generated content and images.

![N8N](https://img.shields.io/badge/N8N-Workflow-orange)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991)
![Gemini](https://img.shields.io/badge/Gemini-Image%20Generation-green)
![LinkedIn](https://img.shields.io/badge/LinkedIn-Auto%20Post-0A66C2)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-Tracker-34A853)

---

## 📖 What This Does

This N8N workflow automatically posts **2-part evolution stories** of all 50 NIFTY companies to LinkedIn every day.

```
Day 1  → TCS Part 1 (Founding Story)
Day 2  → TCS Part 2 (Modern Era)
Day 3  → Reliance Part 1
Day 4  → Reliance Part 2
...and so on for all 50 companies
```

**Total: 100 posts | ~3.3 months | ₹0 manual effort**

---

## 🏗️ Architecture

```
[Schedule Trigger - 9AM Daily]
          ↓
[Google Sheets - Read All Rows]
          ↓
[Filter - Skip done + today's posts]
          ↓
[Limit - 1 company only]
          ↓
[IF - Company exists?]
          ↓
[Set Node - Extract data + build AI prompt]
          ↓
[Basic LLM Chain + OpenAI GPT-4o]
          ↓
[Gemini 2.0 Flash - Generate Image]
          ↓
[LinkedIn Node - Post text + image]
          ↓
[Google Sheets - Update status]
          ↓
[Google Sheets - Append to log]
```

---

## 🔧 Tech Stack

| Tool | Purpose |
|---|---|
| **N8N** | Workflow orchestration |
| **OpenAI GPT-4o** | LinkedIn post content generation |
| **Gemini 2.0 Flash** | Corporate illustration generation |
| **Google Sheets** | Progress tracker & post log |
| **LinkedIn API** | Auto-publishing posts with images |

---

## 📋 Prerequisites

Before setting up, you need:

- [ ] N8N instance (self-hosted or cloud)
- [ ] OpenAI API key (for GPT-4o)
- [ ] Google AI API key (for Gemini image generation)
- [ ] LinkedIn Developer App with `w_member_social` scope
- [ ] Google Sheets OAuth2 credentials
- [ ] Google Sheet set up with correct columns

---

## 🚀 Quick Start

### Step 1 — Clone / Download

```bash
git clone https://github.com/yourusername/nifty50-linkedin-automation.git
```

### Step 2 — Set Up Google Sheets

1. Download `NIFTY50_LinkedIn_Tracker.xlsx`
2. Upload to Google Drive
3. Open with Google Sheets (File → Save as Google Sheets)
4. Copy the Sheet ID from the URL

**Sheet 1: `Company_Master` columns:**
```
row_number | Company_Name | Sector | Founded_Year | Status | Next_Part | Part1_Date | Part2_Date | Last_Posted_Date
```

**Sheet 2: `Post_Log` columns:**
```
Date | Company | Part | Content_Preview | LinkedIn_Post_ID | Status
```

### Step 3 — Import Workflow to N8N

1. Open N8N → New Workflow
2. Click ⋮ menu → Import from File
3. Upload `nifty50_linkedin_workflow_final.json`

### Step 4 — Configure Credentials

Set up these 4 credentials in N8N Settings → Credentials:

#### Google Sheets OAuth2
```
Type: Google Sheets OAuth2 API
Scope: spreadsheets
```

#### OpenAI (GPT-4o)
```
Type: OpenAI API
API Key: sk-YOUR_OPENAI_KEY_HERE
```

#### Google AI (Gemini)
```
Used directly in Node 9 as query parameter
API Key: YOUR_GOOGLE_AI_API_KEY
```

#### LinkedIn OAuth2
```
Type: LinkedIn OAuth2 API
Client ID: YOUR_CLIENT_ID
Client Secret: YOUR_CLIENT_SECRET
Legacy Mode: OFF ← IMPORTANT!
Organization Support: OFF ← IMPORTANT!
```

### Step 5 — Update Placeholders

In the workflow, replace these values:

| Placeholder | Replace With |
|---|---|
| `YOUR_GOOGLE_SHEET_ID_HERE` | Your actual Sheet ID |
| `YOUR_GOOGLE_AI_API_KEY` | Your Gemini API key |

### Step 6 — Test & Activate

1. Run workflow manually once to test
2. Verify LinkedIn post appears
3. Verify Google Sheet updates correctly
4. Enable the Schedule Trigger ✅

---

## 📊 Node Reference

| # | Node | Type | Purpose |
|---|---|---|---|
| 1 | Schedule Trigger | Trigger | Fire daily at 9AM |
| 2 | Get All Rows | Google Sheets | Read Company_Master |
| 3 | Filter | Filter | Skip done + today |
| 4 | Limit | Limit | Allow 1 company only |
| 5 | Has Pending? | IF | Check if row exists |
| 6 | Extract & Build | Set | Build AI prompts |
| 7 | Generate Post | LLM Chain | GPT-4o generates text |
| 8 | OpenAI GPT-4o Model | OpenAI | AI sub-node |
| 9 | Generate Image | Gemini Node | Gemini image generation |
| 10 | Post to LinkedIn | LinkedIn | Publish post + image |
| 11 | Update Status | Google Sheets | Update progress |
| 12 | Append Log | Google Sheets | Log every post |
| 13 | All Done | NoOp | Graceful stop |

---

## 🧠 How Part 1 vs Part 2 Logic Works

```
Google Sheets Column: Next_Part
  Value = 1 → GPT-4o writes PART 1 (founding story)
  Value = 2 → GPT-4o writes PART 2 (modern era)

After posting:
  Part 1 posted → Next_Part changes to 2
  Part 2 posted → Status changes to "done"

Status Flow:
  pending → in_progress → done
```

---

## 💰 Cost Estimate

| Service | Cost Per Post | 100 Posts Total |
|---|---|---|
| OpenAI GPT-4o | ~₹1.50 | ~₹150 |
| Gemini 2.0 Flash | ~₹1.70 | ~₹170 |
| LinkedIn API | Free | Free |
| **Total** | **~₹3.20** | **~₹320** |

---

## 🔌 LinkedIn Setup Guide

1. Go to https://developer.linkedin.com
2. Create App → link to a LinkedIn Page
3. Go to **Products** tab → Request **"Share on LinkedIn"**
4. Go to **Auth** tab → copy Client ID & Secret
5. Add redirect URL: `https://YOUR-N8N-URL/rest/oauth2-credential/callback`
6. In N8N credential → turn **Legacy OFF** + **Organization Support OFF**

---

## ⚠️ Common Issues & Fixes

| Error | Cause | Fix |
|---|---|---|
| `unauthorized_scope_error r_emailaddress` | Legacy mode ON | Turn OFF Legacy in credential |
| `unauthorized_scope_error w_organization_social` | Organization Support ON | Turn OFF in credential |
| Sheet not showing in dropdown | File is .xlsx not Google Sheets | File → Save as Google Sheets |
| All 50 companies posting at once | No Limit node | Add Limit node → Max 1 item |
| Wrong row being updated | row_number matches header row | Use Company_Name as matching column |
| Gemini quota exceeded | Too many test runs | Wait 24hrs or enable billing |

---

```
---

## 🤖 AI Prompts Used

### Part 1 Prompt
```
You are a professional LinkedIn content writer specializing in Indian 
corporate history. Write a LinkedIn post (Part 1 of 2) about the 
evolution of [COMPANY] in the [SECTOR] sector, founded in [YEAR].
Cover: founding story, early struggles, founder vision, first major 
milestone. Under 1200 characters. End with a cliffhanger teasing 
Part 2. Use 2-3 emojis. Output only post text.
```

### Part 2 Prompt
```
You are a professional LinkedIn content writer specializing in Indian 
corporate history. Write a LinkedIn post (Part 2 of 2) about [COMPANY].
Cover: post-2000 transformation, journey to NIFTY 50, top 3 lessons 
for entrepreneurs. Mention Part 1 covered the founding era. Under 1200 
characters. End with a thought-provoking question. Use 2-3 emojis. 
Output only post text.
```

---

## 📅 NIFTY 50 Companies Included

All 50 companies pre-loaded with sector and founding year:

TCS • Reliance Industries • HDFC Bank • Infosys • ICICI Bank • Hindustan Unilever • ITC • State Bank of India • Bharti Airtel • Kotak Mahindra Bank • Larsen & Toubro • Axis Bank • Asian Paints • Bajaj Finance • Maruti Suzuki • Sun Pharmaceutical • Titan Company • Wipro • HCL Technologies • Nestle India • UltraTech Cement • Power Grid • NTPC • ONGC • Tata Motors • Adani Ports • Mahindra & Mahindra • Tata Steel • HDFC Life • SBI Life • Bajaj Finserv • Bajaj Auto • JSW Steel • Grasim Industries • Cipla • Dr Reddys • Divis Labs • Eicher Motors • Hindalco • IndusInd Bank • Tech Mahindra • Apollo Hospitals • Tata Consumer • Coal India • BPCL • Hero MotoCorp • Shriram Finance • LTIMindtree • BEL • Britannia

---

## 🔮 Future Enhancements

- [ ] Add web search before GPT-4o for better factual accuracy
- [ ] Add error notification via Telegram/Slack
- [ ] Add hashtag optimization node
- [ ] Support for company pages in addition to personal profiles
- [ ] Analytics tracking node (impressions, likes, comments)
- [ ] Extend to cover NSE 500 companies

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Contributing

Pull requests welcome! If you find a bug or want to add a feature:
1. Fork the repo
2. Create your feature branch
3. Commit your changes
4. Open a Pull Request

---

## ⭐ If This Helped You

Give this repo a ⭐ and share the LinkedIn post!

Built with ❤️ using N8N + OpenAI GPT-4o + Gemini + LinkedIn API
