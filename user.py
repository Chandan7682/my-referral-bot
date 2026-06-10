from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import *
from config import BOT_USERNAME, REDEEM_OPTIONS

# ============================================================
# REFERRAL
# ============================================================

async def referral_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    ref_count = get_referral_count(user_id)
    pts = get_points(user_id)
    points_per_ref = int(get_setting("points_per_referral", "10"))

    text = (
        f"👥 *Referral Program*\n\n"
        f"🔗 *Aapka Referral Link:*\n`{ref_link}`\n\n"
        f"📊 *Aapke Stats:*\n"
        f"├ 👥 Total Referrals: *{ref_count}*\n"
        f"├ 💰 Points per Referral: *{points_per_ref}*\n"
        f"└ 🏆 Total Points: *{pts['total']}*\n\n"
        f"💡 *Kaise Kaam Karta Hai:*\n"
        f"1️⃣ Apna link share karo\n"
        f"2️⃣ Dost link par click kare\n"
        f"3️⃣ Woh channels join kare\n"
        f"4️⃣ Verify karne par aapko *+{points_per_ref} Points* milenge!\n\n"
        f"🎯 Jitne zyada referrals, utne zyada points!"
    )

    keyboard = [
        [InlineKeyboardButton("📤 Link Share Karo", switch_inline_query=f"Yeh amazing bot join karo aur paise kamao! {ref_link}")],
        [InlineKeyboardButton("📋 Link Copy Karo", callback_data=f"copy_ref_{user_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# POINTS
# ============================================================

async def my_points_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    pts = get_points(user_id)
    ref_count = get_referral_count(user_id)
    rank = get_user_rank(user_id)
    points_per_ref = int(get_setting("points_per_referral", "10"))

    text = (
        f"💰 *Aapke Points*\n\n"
        f"┌─────────────────────\n"
        f"│ 🟢 Current Points: *{pts['total']}*\n"
        f"│ 🏆 Lifetime Earned: *{pts['lifetime']}*\n"
        f"│ 👥 Total Referrals: *{ref_count}*\n"
        f"│ 📊 Your Rank: *#{rank}*\n"
        f"└─────────────────────\n\n"
        f"💡 Har successful referral = *+{points_per_ref} points*\n\n"
        f"🎁 Points ko rewards mein convert karo!"
    )

    keyboard = [
        [InlineKeyboardButton("🎁 Redeem Points", callback_data="redeem")],
        [InlineKeyboardButton("👛 My Wallet", callback_data="wallet")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# WALLET
# ============================================================

async def wallet_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    pts = get_points(user_id)
    history = get_wallet_history(user_id, 5)
    ref_count = get_referral_count(user_id)
    user_redeems = get_user_redeems(user_id)

    # Approved redeems ka total
    total_redeemed = sum(r["amount"] for r in user_redeems if r["status"] == "approved")
    pending_redeems = sum(r["points_used"] for r in user_redeems if r["status"] == "pending")

    history_text = ""
    if history:
        history_text = "\n\n📜 *Recent Transactions:*\n"
        for h in history:
            emoji = "🟢" if h["type"] == "credit" else "🔴"
            sign = "+" if h["type"] == "credit" else "-"
            date = h["created_at"][:10] if h["created_at"] else ""
            history_text += f"{emoji} {sign}{h['points']} pts | {h['description'][:25]} | {date}\n"

    text = (
        f"👛 *Aapka Wallet*\n\n"
        f"┌─────────────────────\n"
        f"│ 💰 Available Points: *{pts['total']}*\n"
        f"│ 🏆 Total Earned: *{pts['lifetime']}*\n"
        f"│ 👥 Total Referrals: *{ref_count}*\n"
        f"│ 💵 Total Redeemed: *₹{total_redeemed:.2f}*\n"
        f"│ ⏳ Pending Redeem: *{pending_redeems} pts*\n"
        f"└─────────────────────"
        f"{history_text}"
    )

    keyboard = [
        [InlineKeyboardButton("🎁 Redeem Karo", callback_data="redeem")],
        [InlineKeyboardButton("📜 Full History", callback_data="history")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# HISTORY
# ============================================================

async def history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    history = get_wallet_history(user_id, 15)
    
    if not history:
        text = "📜 *Transaction History*\n\nAbhi tak koi transaction nahi hui!"
    else:
        text = "📜 *Transaction History* (Last 15)\n\n"
        for h in history:
            emoji = "🟢" if h["type"] == "credit" else "🔴"
            sign = "+" if h["type"] == "credit" else "-"
            date = h["created_at"][:10] if h["created_at"] else ""
            text += f"{emoji} `{sign}{h['points']} pts` | {h['description'][:30]}\n📅 {date}\n\n"

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="wallet")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# REDEEM
# ============================================================

async def redeem_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    pts = get_points(user_id)
    min_redeem = int(get_setting("min_redeem_points", "100"))

    options_text = "\n".join([f"🎯 *{opt['points']} Points* = *{opt['label']}*" for opt in REDEEM_OPTIONS])

    text = (
        f"🎁 *Redeem Points*\n\n"
        f"💰 Aapke Points: *{pts['total']}*\n"
        f"📊 Minimum Redeem: *{min_redeem} points*\n\n"
        f"💵 *Redeem Options:*\n{options_text}\n\n"
        f"👇 Apna option choose karo:"
    )

    keyboard = []
    for opt in REDEEM_OPTIONS:
        status = "✅" if pts["total"] >= opt["points"] else "🔒"
        keyboard.append([InlineKeyboardButton(
            f"{status} {opt['points']} pts = {opt['label']}",
            callback_data=f"redeem_{opt['points']}_{opt['amount']}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def redeem_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    data = query.data.split("_")
    points_needed = int(data[1])
    amount = float(data[2])

    pts = get_points(user_id)

    if pts["total"] < points_needed:
        await query.answer(f"❌ Points kam hain! Chahiye: {points_needed}, Aapke paas: {pts['total']}", show_alert=True)
        return

    context.user_data["redeem_points"] = points_needed
    context.user_data["redeem_amount"] = amount
    context.user_data["awaiting_upi"] = True

    text = (
        f"💳 *Redeem: {points_needed} Points = ₹{amount}*\n\n"
        f"📝 Apna *UPI ID* ya *Payment Details* bhejo:\n\n"
        f"Example: `yourname@paytm` ya `9876543210@upi`\n\n"
        f"⚠️ Sahi UPI ID dena, galat ID par payment nahi hogi!"
    )

    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="redeem")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_upi_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ne UPI ID bheja"""
    if not context.user_data.get("awaiting_upi"):
        return False

    user_id = update.effective_user.id
    upi_id = update.message.text.strip()
    points = context.user_data.get("redeem_points")
    amount = context.user_data.get("redeem_amount")

    pts = get_points(user_id)
    if pts["total"] < points:
        await update.message.reply_text("❌ Points kam ho gaye! Dobara try karo.")
        context.user_data.clear()
        return True

    # Points deduct karo
    deduct_points(user_id, points, f"Redeem request ₹{amount}")
    
    # Request create karo
    req_id = create_redeem_request(user_id, points, amount, upi_id, "UPI")

    # Admin ko notify karo
    from config import ADMIN_IDS
    user = update.effective_user
    admin_text = (
        f"🔔 *New Redeem Request!*\n\n"
        f"🆔 Request ID: `{req_id}`\n"
        f"👤 User: {user.full_name} (`{user_id}`)\n"
        f"💰 Points: *{points}*\n"
        f"💵 Amount: *₹{amount}*\n"
        f"📲 UPI: `{upi_id}`"
    )
    admin_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_{req_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{req_id}"),
        ]
    ])
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(admin_id, admin_text, parse_mode="Markdown", reply_markup=admin_keyboard)
        except Exception:
            pass

    from handlers.start import get_main_menu_keyboard
    keyboard = await get_main_menu_keyboard()
    await update.message.reply_text(
        f"✅ *Redeem Request Submit Ho Gayi!*\n\n"
        f"🆔 Request ID: `{req_id}`\n"
        f"💰 Points Deducted: *{points}*\n"
        f"💵 Amount: *₹{amount}*\n"
        f"📲 UPI: `{upi_id}`\n\n"
        f"⏳ Admin review karenge aur jald payment karenge!",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    context.user_data.clear()
    return True

# ============================================================
# STATS
# ============================================================

async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = query.from_user

    pts = get_points(user_id)
    ref_count = get_referral_count(user_id)
    rank = get_user_rank(user_id)
    user_data = get_user(user_id)
    user_redeems = get_user_redeems(user_id)
    total_redeemed = sum(r["amount"] for r in user_redeems if r["status"] == "approved")

    joined = user_data["joined_at"][:10] if user_data else "N/A"

    text = (
        f"📊 *Aapki Stats*\n\n"
        f"👤 *Profile:*\n"
        f"├ Naam: *{user.full_name}*\n"
        f"├ Username: @{user.username or 'N/A'}\n"
        f"├ ID: `{user_id}`\n"
        f"└ Joined: {joined}\n\n"
        f"🏆 *Performance:*\n"
        f"├ 💰 Points: *{pts['total']}*\n"
        f"├ 🏅 Lifetime: *{pts['lifetime']}*\n"
        f"├ 👥 Referrals: *{ref_count}*\n"
        f"├ 📊 Rank: *#{rank}*\n"
        f"└ 💵 Total Redeemed: *₹{total_redeemed:.2f}*\n\n"
        f"🎯 Aur referrals karo, rank badhao!"
    )

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# LEADERBOARD
# ============================================================

async def leaderboard_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    leaders = get_leaderboard(10)
    my_rank = get_user_rank(user_id)

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    text = "🏆 *Top 10 Leaderboard*\n\n"
    for i, leader in enumerate(leaders):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        name = leader["full_name"] or leader["username"] or "User"
        pts_val = leader["lifetime_points"] or 0
        refs = leader["referral_count"] or 0
        marker = " 👈 *You*" if leader["user_id"] == user_id else ""
        text += f"{medal} *{name[:15]}*{marker}\n   💰 {pts_val} pts | 👥 {refs} refs\n\n"

    text += f"\n📊 *Aapka Rank: #{my_rank}*"

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# HELP
# ============================================================

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    points_per_ref = int(get_setting("points_per_referral", "10"))

    text = (
        f"ℹ️ *Help & Guide*\n\n"
        f"🤖 *Bot Kaise Kaam Karta Hai:*\n\n"
        f"1️⃣ `/start` - Bot start karo\n"
        f"2️⃣ Sab channels join karo\n"
        f"3️⃣ Verify karo\n"
        f"4️⃣ Apna referral link lo\n"
        f"5️⃣ Share karo aur points kamao!\n\n"
        f"💰 *Points System:*\n"
        f"• Har referral = *{points_per_ref} points*\n"
        f"• Sirf verified users ka count hoga\n"
        f"• Self-referral count nahi hoga\n\n"
        f"🎁 *Redeem:*\n"
        f"• 100 pts = ₹10\n"
        f"• 500 pts = ₹50\n"
        f"• 1000 pts = ₹100\n\n"
        f"❓ *Problems?* Admin se contact karein"
    )

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
