# 🔑 Setup API Keys - Quick Guide

**Time Required:** 5 minutes  
**Status:** ✅ `.env` file created in `backend/.env`

---

## Step 1: Get Your Anthropic API Key (2 minutes)

### Visit Anthropic Console:
**URL:** https://console.anthropic.com/settings/keys

### Steps:
1. **Sign up or log in** to Anthropic Console
2. Click **"API Keys"** in the left sidebar
3. Click **"Create Key"** button
4. Give it a name: `UDC Polaris Development`
5. **Copy the key** - it starts with `sk-ant-...`

**⚠️ Important:** Copy it now - you won't see it again!

---

## Step 2: Add Key to .env File (1 minute)

### Open the .env file:
```bash
# Windows
notepad backend\.env

# Or use any text editor
```

### Find this line (line 11):
```bash
ANTHROPIC_API_KEY=
```

### Paste your key:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

### Save and close!

---

## Step 3: Verify Setup (1 minute)

### Check the file exists:
```bash
# Should show the file
ls backend\.env
```

### Verify key is set (don't show full key):
```bash
cd backend
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ API Key loaded!' if os.getenv('ANTHROPIC_API_KEY') else '❌ API Key missing!')"
```

---

## ✅ You're Ready!

**Your `.env` file is now configured at:**
```
D:\udc\backend\.env
```

**What's in it:**
- ✅ Anthropic API key slot (add your key)
- ✅ OpenAI fallback slot (optional)
- ✅ All configuration settings
- ✅ Development defaults
- ✅ Professional structure

---

## 🔒 Security Notes

### ✅ Safe:
- `.env` file is in `.gitignore` - won't be committed
- Local to your machine only
- Each team member has their own

### ⚠️ Never:
- Commit `.env` to Git
- Share your API key publicly
- Store keys in code
- Upload to GitHub

---

## 🚀 Next Steps

Now that your API key is configured:

### Option 1: Test Dr. Omar (Recommended)
```bash
cd D:\udc
python test_dr_omar.py
```

### Option 2: Start FastAPI Server
```bash
cd D:\udc\backend
uvicorn app.main:app --reload
```

### Option 3: Interactive Python Test
```bash
cd D:\udc\backend
python
>>> from app.agents.dr_omar import dr_omar
>>> result = dr_omar.answer_question("What is our debt-to-equity ratio?")
>>> print(result['answer'])
```

---

## 💰 Cost Tracking

**Your API key will be charged:**
- ~QAR 0.25-0.45 per question
- ~QAR 35-45 per 100 questions
- Well within budget!

**Monitor usage:**
- Anthropic Console: https://console.anthropic.com/settings/usage
- Check regularly to avoid surprises

---

## 🔄 If You Need to Change Keys

### Update the key:
1. Edit `backend/.env`
2. Replace `ANTHROPIC_API_KEY=...` with new key
3. No need to restart (for test script)
4. Restart FastAPI server if running

### Rotate keys regularly:
- Security best practice: Rotate every 90 days
- Before sharing access with new team members
- If key is accidentally exposed

---

## ❓ Troubleshooting

### Error: "Module not found: dotenv"
**Solution:**
```bash
cd backend
pip install python-dotenv
```

### Error: "API key not found"
**Check:**
1. File exists: `backend\.env`
2. Key is on line 11
3. No spaces around `=`
4. Key starts with `sk-ant-`

### Error: "Invalid API key"
**Solution:**
1. Generate new key from Anthropic Console
2. Make sure you copied entire key
3. Check for extra spaces

---

## ✅ Verification Checklist

Before testing Dr. Omar:

- [ ] `.env` file exists in `backend/` directory
- [ ] Anthropic API key added (starts with `sk-ant-`)
- [ ] File is in `.gitignore` (won't be committed)
- [ ] Key copied correctly (no extra spaces)
- [ ] You have Anthropic Console access

---

## 🎯 You're Ready to Test Dr. Omar!

```bash
cd D:\udc
python test_dr_omar.py
```

**Expected result:** Dr. Omar answers your questions with data-backed analysis!

---

**Created:** October 31, 2025  
**Status:** ✅ `.env` file ready for your API key

