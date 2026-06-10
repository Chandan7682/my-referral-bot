# 🤖 Telegram Referral Bot - Setup Guide

## 📁 File Structure
```
telegram_bot/
├── main.py              ← Bot start karne ki file
├── config.py            ← Settings
├── requirements.txt     ← Dependencies
├── .env                 ← Your secret tokens (EDIT THIS)
├── database/
│   └── db.py            ← Database operations
└── handlers/
    ├── start.py         ← Force join + verify
    ├── user.py          ← Referral, points, wallet, redeem
    └── admin.py         ← Admin panel
```

---

## 🚀 STEP BY STEP SETUP

### Step 1: Python Install Karo
Python 3.10+ chahiye.
```
https://www.python.org/downloads/
```

### Step 2: Dependencies Install Karo
```bash
pip install -r requirements.txt
```

### Step 3: .env File Edit Karo
`.env` file khole aur yeh changes karo:
```
BOT_TOKEN=Apna_naya_bot_token_yahan_dalo
ADMIN_IDS=6517309435
BOT_USERNAME=YourBotUsername
```
> ⚠️ BOT_USERNAME mein @ mat lagao, sirf username dalo

### Step 4: Bot Ko Channel Admin Banao
Jab bhi koi channel add karna ho:
1. Channel settings → Admins → Add Admin
2. Bot ka username search karo
3. Add kar do

### Step 5: Bot Start Karo
```bash
cd telegram_bot
python main.py
```

---

## 👑 ADMIN COMMANDS

| Command | Kaam |
|---------|------|
| `/admin` ya `/panel` | Admin panel kholna |

### Admin Panel Se Kar Sakte Ho:
- ✅ Channels add/remove (Force Join)
- ✅ Points per referral change
- ✅ Redeem requests approve/reject
- ✅ Users ban/unban
- ✅ Users ko manual points add
- ✅ Broadcast message bhejo
- ✅ Bot stats dekho
- ✅ Multiple admins add karo

---

## 📢 Channel Add Karne Ka Format
Admin Panel → Channels → Add Channel

Format:
```
-1001234567890|Channel Ka Naam|https://t.me/channellink
```

Channel ID nikalne ke liye:
- Bot `@username_to_id_bot` use karo
- Ya channel ko forward karo kisi bot ko

---

## 🎁 Redeem Options (config.py mein change karo)
```python
REDEEM_OPTIONS = [
    {"points": 100, "amount": 10, "label": "₹10"},
    {"points": 500, "amount": 50, "label": "₹50"},
    {"points": 1000, "amount": 100, "label": "₹100"},
]
```

---

## 🌐 FREE HOSTING (Railway)
1. [railway.app](https://railway.app) par account banao
2. New Project → Deploy from GitHub
3. Environment variables mein .env ka content dalo
4. Deploy!

---

## ⚠️ IMPORTANT SECURITY
- Kabhi bhi BOT_TOKEN public mat karo
- .env file ko git mein mat daalo
- BotFather se purana token revoke kar do!

---

## ✨ Extra Features Included
- 👛 Wallet system with history
- 📜 Transaction history
- 🏆 Leaderboard
- 🔔 Real-time notifications
- 🛡️ Anti-fraud system
- 📣 Broadcast to all users
- 💰 Points refund on rejection
