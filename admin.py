from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import *
from config import ADMIN_IDS
import asyncio

def admin_only(func):
    """Admin check decorator"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("❌ Aap admin nahi hain!", show_alert=True)
            else:
                await update.message.reply_text("❌ *Yeh command sirf admins ke liye hai!*", parse_mode="Markdown")
            return
        return await func(update, context)
    return wrapper

# ============================================================
# ADMIN PANEL MAIN
# ============================================================

@admin_only
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📢 Channels", callback_data="adm_channels"),
            InlineKeyboardButton("👥 Users", callback_data="adm_users"),
        ],
        [
            InlineKeyboardButton("🎁 Redeems", callback_data="adm_redeems"),
            InlineKeyboardButton("⚙️ Settings", callback_data="adm_settings"),
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="adm_stats"),
            InlineKeyboardButton("📣 Broadcast", callback_data="adm_broadcast"),
        ],
        [
            InlineKeyboardButton("👑 Admins", callback_data="adm_admins"),
        ],
    ]
    
    stats = get_admin_stats()
    text = (
        f"🔐 *Admin Panel*\n\n"
        f"📊 *Quick Stats:*\n"
        f"├ 👥 Total Users: *{stats['total_users']}*\n"
        f"├ ✅ Verified: *{stats['verified_users']}*\n"
        f"├ 🔗 Referrals: *{stats['total_referrals']}*\n"
        f"├ ⏳ Pending Redeems: *{stats['pending_redeems']}*\n"
        f"├ 💰 Total Paid: *₹{stats['total_paid']:.2f}*\n"
        f"└ 📢 Active Channels: *{stats['active_channels']}*\n\n"
        f"Kya karna chahte hain?"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# CHANNELS MANAGEMENT
# ============================================================

@admin_only
async def adm_channels_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    channels = get_all_channels()
    text = f"📢 *Channels Management*\n\nTotal Channels: *{len(channels)}*\n\n"
    
    if channels:
        for ch in channels:
            text += f"➤ *{ch['channel_name']}*\n   ID: `{ch['channel_id']}`\n\n"
    else:
        text += "Abhi koi channel add nahi kiya!"

    keyboard = [
        [InlineKeyboardButton("➕ Channel Add Karo", callback_data="adm_add_channel")],
        [InlineKeyboardButton("➖ Channel Remove Karo", callback_data="adm_remove_channel")],
        [InlineKeyboardButton("🔙 Back", callback_data="adm_back")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

@admin_only
async def adm_add_channel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["adm_action"] = "add_channel"
    
    text = (
        f"📢 *Channel Add Karo*\n\n"
        f"Neeche format mein bhejo:\n\n"
        f"`CHANNEL_ID|Channel Naam|https://t.me/channellink`\n\n"
        f"Example:\n`-1001234567890|Mera Channel|https://t.me/merachannel`\n\n"
        f"⚠️ Bot ko channel ka admin banana mat bhoolo!"
    )
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="adm_channels")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

@admin_only
async def adm_remove_channel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    channels = get_all_channels()
    if not channels:
        await query.answer("Koi channel nahi hai!", show_alert=True)
        return
    
    keyboard = []
    for ch in channels:
        keyboard.append([InlineKeyboardButton(f"❌ {ch['channel_name']}", callback_data=f"adm_delch_{ch['channel_id']}")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="adm_channels")])
    
    await query.edit_message_text("🗑️ *Kaunsa channel remove karna hai?*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# SETTINGS
# ============================================================

@admin_only
async def adm_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    pts = get_setting("points_per_referral", "10")
    min_redeem = get_setting("min_redeem_points", "100")
    
    text = (
        f"⚙️ *Bot Settings*\n\n"
        f"💰 Points per Referral: *{pts}*\n"
        f"🎁 Min Redeem Points: *{min_redeem}*\n\n"
        f"Kya change karna chahte hain?"
    )
    
    keyboard = [
        [InlineKeyboardButton(f"💰 Points Change ({pts})", callback_data="adm_set_points")],
        [InlineKeyboardButton(f"🎁 Min Redeem ({min_redeem})", callback_data="adm_set_minredeem")],
        [InlineKeyboardButton("🔙 Back", callback_data="adm_back")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

@admin_only
async def adm_set_points_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["adm_action"] = "set_points"
    
    current = get_setting("points_per_referral", "10")
    text = f"💰 *Points per Referral Change Karo*\n\nCurrent value: *{current}*\n\nNaya number bhejo (sirf number):"
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="adm_settings")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# REDEEM MANAGEMENT
# ============================================================

@admin_only
async def adm_redeems_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    pending = get_pending_redeems()
    text = f"🎁 *Redeem Requests*\n\nPending: *{len(pending)}*\n\n"
    
    keyboard = []
    if pending:
        for req in pending[:5]:
            name = req["full_name"] or req["username"] or f"User{req['user_id']}"
            keyboard.append([InlineKeyboardButton(
                f"#{req['id']} | {name[:15]} | ₹{req['amount']}",
                callback_data=f"adm_viewreq_{req['id']}"
            )])
    else:
        text += "✅ Koi pending request nahi hai!"
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="adm_back")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

@admin_only
async def adm_view_request_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    req_id = int(query.data.split("_")[2])
    req = get_redeem_by_id(req_id)
    
    if not req:
        await query.answer("Request nahi mili!", show_alert=True)
        return
    
    text = (
        f"📋 *Redeem Request #{req_id}*\n\n"
        f"👤 User ID: `{req['user_id']}`\n"
        f"💰 Points: *{req['points_used']}*\n"
        f"💵 Amount: *₹{req['amount']}*\n"
        f"📲 UPI: `{req['payment_details']}`\n"
        f"📅 Date: {req['requested_at'][:10]}\n"
        f"⏳ Status: *{req['status'].upper()}*"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_{req_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{req_id}"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="adm_redeems")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_approve_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.answer("❌ Admin nahi hain aap!", show_alert=True)
        return
    
    await query.answer("✅ Approving...")
    req_id = int(query.data.split("_")[2])
    req = process_redeem(req_id, "approved", f"Approved by admin {user_id}")
    
    if req:
        # User ko notify karo
        try:
            await context.bot.send_message(
                chat_id=req["user_id"],
                text=(
                    f"🎉 *Aapki Redeem Request Approve Ho Gayi!*\n\n"
                    f"🆔 Request: #{req_id}\n"
                    f"💵 Amount: *₹{req['amount']}*\n"
                    f"📲 UPI: `{req['payment_details']}`\n\n"
                    f"💸 Payment jald aapke UPI par aayegi!\n"
                    f"Dhanyawad! 🙏"
                ),
                parse_mode="Markdown"
            )
        except Exception:
            pass
        
        await query.edit_message_text(
            f"✅ *Request #{req_id} Approved!*\n\n₹{req['amount']} user ko milenge.",
            parse_mode="Markdown"
        )

async def admin_reject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.answer("❌ Admin nahi hain aap!", show_alert=True)
        return
    
    await query.answer("❌ Rejecting...")
    req_id = int(query.data.split("_")[2])
    req = get_redeem_by_id(req_id)
    
    if req and req["status"] == "pending":
        process_redeem(req_id, "rejected", f"Rejected by admin {user_id}")
        # Points wapas karo
        add_points(req["user_id"], req["points_used"], f"Redeem rejected - Points refund #{req_id}")
        
        try:
            await context.bot.send_message(
                chat_id=req["user_id"],
                text=(
                    f"❌ *Aapki Redeem Request Reject Ho Gayi!*\n\n"
                    f"🆔 Request: #{req_id}\n"
                    f"💰 *{req['points_used']} Points* aapke wallet mein wapas add ho gaye!\n\n"
                    f"Kisi problem ke liye admin se contact karein."
                ),
                parse_mode="Markdown"
            )
        except Exception:
            pass
        
        await query.edit_message_text(
            f"❌ *Request #{req_id} Rejected!*\n\nPoints user ko refund kar diye gaye.",
            parse_mode="Markdown"
        )

# ============================================================
# USERS MANAGEMENT
# ============================================================

@admin_only
async def adm_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["adm_action"] = "search_user"
    
    text = (
        f"👥 *Users Management*\n\n"
        f"User ka Telegram ID bhejo:\n\n"
        f"*Actions available:*\n"
        f"• Ban/Unban user\n"
        f"• Add/Remove points\n"
        f"• View user stats"
    )
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="adm_back")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# BROADCAST
# ============================================================

@admin_only
async def adm_broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["adm_action"] = "broadcast"
    
    text = (
        f"📣 *Broadcast Message*\n\n"
        f"Woh message bhejo jo sab users ko bhejna hai.\n\n"
        f"⚠️ HTML formatting use kar sakte hain."
    )
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="adm_back")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# STATS
# ============================================================

@admin_only
async def adm_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    stats = get_admin_stats()
    leaders = get_leaderboard(3)
    
    top_text = ""
    for i, l in enumerate(leaders):
        medals = ["🥇", "🥈", "🥉"]
        name = l["full_name"] or "User"
        top_text += f"{medals[i]} {name[:15]}: {l['lifetime_points'] or 0} pts\n"
    
    text = (
        f"📊 *Bot Statistics*\n\n"
        f"👥 Total Users: *{stats['total_users']}*\n"
        f"✅ Verified Users: *{stats['verified_users']}*\n"
        f"🔗 Total Referrals: *{stats['total_referrals']}*\n"
        f"⏳ Pending Redeems: *{stats['pending_redeems']}*\n"
        f"💰 Total Paid: *₹{stats['total_paid']:.2f}*\n"
        f"📢 Active Channels: *{stats['active_channels']}*\n\n"
        f"🏆 *Top 3 Users:*\n{top_text}"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="adm_back")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# ADMINS MANAGEMENT
# ============================================================

@admin_only
async def adm_admins_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    db_admins = get_all_admins()
    all_admins = list(set(ADMIN_IDS + db_admins))
    
    text = f"👑 *Admin Management*\n\nTotal Admins: *{len(all_admins)}*\n\n"
    text += "\n".join([f"• `{aid}`" for aid in all_admins])
    
    keyboard = [
        [InlineKeyboardButton("➕ Admin Add", callback_data="adm_addadmin")],
        [InlineKeyboardButton("➖ Admin Remove", callback_data="adm_removeadmin")],
        [InlineKeyboardButton("🔙 Back", callback_data="adm_back")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# ADMIN TEXT INPUT HANDLER
# ============================================================

async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin se text input handle karo"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return False
    
    action = context.user_data.get("adm_action")
    if not action:
        return False
    
    text = update.message.text.strip()
    
    if action == "add_channel":
        try:
            parts = text.split("|")
            ch_id = parts[0].strip()
            ch_name = parts[1].strip()
            ch_link = parts[2].strip()
            success = add_channel(ch_id, ch_name, ch_link)
            if success:
                await update.message.reply_text(f"✅ *Channel '{ch_name}' add ho gaya!*", parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Channel pehle se exist karta hai!")
        except Exception:
            await update.message.reply_text("❌ Format galat hai!\n\nSahi format:\n`CHANNEL_ID|Naam|Link`", parse_mode="Markdown")
        context.user_data.pop("adm_action", None)
        return True

    elif action == "set_points":
        try:
            points = int(text)
            set_setting("points_per_referral", str(points))
            await update.message.reply_text(f"✅ *Points per referral set: {points}*", parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("❌ Sirf number dalo!")
        context.user_data.pop("adm_action", None)
        return True

    elif action == "broadcast":
        users = get_all_user_ids()
        sent, failed = 0, 0
        await update.message.reply_text(f"📣 Broadcasting to {len(users)} users...")
        for uid in users:
            try:
                await context.bot.send_message(uid, text, parse_mode="HTML")
                sent += 1
                await asyncio.sleep(0.05)  # Rate limit avoid
            except Exception:
                failed += 1
        await update.message.reply_text(f"✅ Broadcast complete!\n✅ Sent: {sent}\n❌ Failed: {failed}")
        context.user_data.pop("adm_action", None)
        return True

    elif action == "search_user":
        try:
            target_id = int(text)
            target_user = get_user(target_id)
            if not target_user:
                await update.message.reply_text("❌ User nahi mila!")
                context.user_data.pop("adm_action", None)
                return True
            
            pts = get_points(target_id)
            refs = get_referral_count(target_id)
            banned = "🔴 Banned" if target_user["is_banned"] else "🟢 Active"
            
            text_out = (
                f"👤 *User Info*\n\n"
                f"ID: `{target_id}`\n"
                f"Naam: {target_user['full_name']}\n"
                f"Username: @{target_user['username'] or 'N/A'}\n"
                f"Status: {banned}\n"
                f"Points: {pts['total']}\n"
                f"Referrals: {refs}\n"
                f"Joined: {target_user['joined_at'][:10]}"
            )
            
            ban_btn = "🔓 Unban" if target_user["is_banned"] else "🔨 Ban"
            ban_cb = f"adm_unban_{target_id}" if target_user["is_banned"] else f"adm_ban_{target_id}"
            
            keyboard = [
                [
                    InlineKeyboardButton(ban_btn, callback_data=ban_cb),
                    InlineKeyboardButton("➕ Points Add", callback_data=f"adm_addpts_{target_id}"),
                ],
            ]
            await update.message.reply_text(text_out, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except ValueError:
            await update.message.reply_text("❌ Valid User ID dalo (numbers only)")
        context.user_data.pop("adm_action", None)
        return True

    elif action and action.startswith("addpts_"):
        target_id = int(action.split("_")[1])
        try:
            pts_add = int(text)
            add_points(target_id, pts_add, f"Admin added {pts_add} pts")
            await update.message.reply_text(f"✅ *{pts_add} points user {target_id} ko add ho gaye!*", parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("❌ Number dalo!")
        context.user_data.pop("adm_action", None)
        return True
    
    return False

# ============================================================
# BAN/UNBAN/POINTS CALLBACKS
# ============================================================

async def adm_ban_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌ Admin nahi hain!", show_alert=True)
        return
    target_id = int(query.data.split("_")[2])
    ban_user(target_id)
    await query.answer(f"✅ User {target_id} banned!", show_alert=True)
    await query.edit_message_text(f"🔨 *User `{target_id}` ban ho gaya!*", parse_mode="Markdown")

async def adm_unban_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌ Admin nahi hain!", show_alert=True)
        return
    target_id = int(query.data.split("_")[2])
    unban_user(target_id)
    await query.answer(f"✅ User {target_id} unbanned!", show_alert=True)
    await query.edit_message_text(f"🔓 *User `{target_id}` unban ho gaya!*", parse_mode="Markdown")

async def adm_addpts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌ Admin nahi hain!", show_alert=True)
        return
    target_id = int(query.data.split("_")[2])
    context.user_data["adm_action"] = f"addpts_{target_id}"
    await query.edit_message_text(f"💰 *User `{target_id}` ko kitne points add karne hain?*\n\nNumber bhejo:", parse_mode="Markdown")

async def adm_delch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌ Admin nahi hain!", show_alert=True)
        return
    parts = query.data.split("_")
    ch_id = "_".join(parts[2:])
    remove_channel(ch_id)
    await query.answer("✅ Channel remove ho gaya!", show_alert=True)
    await adm_channels_callback(update, context)
