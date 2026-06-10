from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import *
from config import BOT_USERNAME
import asyncio

async def check_user_joined_all(bot, user_id):
    """Check karo user ne sab channels join kiye hain ya nahi"""
    channels = get_all_channels()
    if not channels:
        return True, []

    not_joined = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch["channel_id"], user_id=user_id)
            if member.status in ["left", "kicked", "banned"]:
                not_joined.append(ch)
        except Exception:
            not_joined.append(ch)

    return len(not_joined) == 0, not_joined

async def get_main_menu_keyboard():
    """Main menu buttons"""
    keyboard = [
        [
            InlineKeyboardButton("👥 Referral Link", callback_data="referral"),
            InlineKeyboardButton("💰 My Points", callback_data="my_points"),
        ],
        [
            InlineKeyboardButton("👛 My Wallet", callback_data="wallet"),
            InlineKeyboardButton("🎁 Redeem", callback_data="redeem"),
        ],
        [
            InlineKeyboardButton("📊 My Stats", callback_data="my_stats"),
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
        ],
        [
            InlineKeyboardButton("📜 History", callback_data="history"),
            InlineKeyboardButton("ℹ️ Help", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Ban check
    if is_banned(user_id):
        await update.message.reply_text(
            "❌ *Aapka account ban kar diya gaya hai!*\n\nAdmin se contact karein.",
            parse_mode="Markdown"
        )
        return

    # Referral check - /start ke saath referral id aai hai
    referred_by = None
    if context.args:
        try:
            ref_id = int(context.args[0])
            if ref_id != user_id and is_user_exists(ref_id):
                referred_by = ref_id
                context.user_data["referred_by"] = ref_id
        except (ValueError, TypeError):
            pass

    # User add karo DB mein
    if not is_user_exists(user_id):
        add_user(user_id, user.username or "", user.full_name or "", referred_by)
    
    # Channels check karo
    channels = get_all_channels()
    
    if not channels:
        # Koi channel nahi hai - seedha main menu
        if not is_verified(user_id):
            set_verified(user_id)
        await show_main_menu(update, context)
        return

    # Force join check
    all_joined, not_joined = await check_user_joined_all(context.bot, user_id)
    
    if all_joined and is_verified(user_id):
        await show_main_menu(update, context)
        return
    
    # Join required message
    keyboard = []
    for ch in channels:
        keyboard.append([InlineKeyboardButton(f"📢 {ch['channel_name']}", url=ch["channel_link"])])
    keyboard.append([InlineKeyboardButton("✅ Maine Join Kar Liya - Verify Karo", callback_data="verify")])

    text = (
        f"🙏 *{user.first_name} Ji, Swagat Hai!*\n\n"
        f"{'🌟 Aapko ek dost ne refer kiya hai!' if referred_by else ''}\n\n"
        f"⚠️ *Bot use karne ke liye pehle in channels ko join karna zaroori hai:*\n\n"
        + "\n".join([f"➤ {ch['channel_name']}" for ch in channels])
        + "\n\n✅ *Sab join karne ke baad 'Verify' button dabao*"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Checking...")
    
    user = query.from_user
    user_id = user.id

    if is_banned(user_id):
        await query.edit_message_text("❌ Aapka account ban hai!")
        return

    all_joined, not_joined = await check_user_joined_all(context.bot, user_id)

    if not all_joined:
        keyboard = []
        for ch in not_joined:
            keyboard.append([InlineKeyboardButton(f"📢 {ch['channel_name']}", url=ch["channel_link"])])
        keyboard.append([InlineKeyboardButton("✅ Ab Verify Karo", callback_data="verify")])
        
        await query.edit_message_text(
            f"❌ *Aapne abhi tak {len(not_joined)} channel(s) join nahi kiye!*\n\n"
            f"Neeche wale channels join karo:\n"
            + "\n".join([f"➤ {ch['channel_name']}" for ch in not_joined])
            + "\n\n🔄 Join karne ke baad dobara Verify karo.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Pehli baar verify ho raha hai
    first_time = not is_verified(user_id)
    set_verified(user_id)

    # Referral process
    if first_time:
        user_data = get_user(user_id)
        ref_id = user_data["referred_by"] if user_data else None
        
        # context se bhi check karo
        if not ref_id:
            ref_id = context.user_data.get("referred_by")

        if ref_id and ref_id != user_id and not has_been_referred(user_id):
            points_per_ref = int(get_setting("points_per_referral", "10"))
            success = add_referral(ref_id, user_id, points_per_ref)
            if success:
                add_points(ref_id, points_per_ref, f"Referral bonus - User {user_id}")
                # Referrer ko notify karo
                try:
                    ref_user = get_user(ref_id)
                    ref_name = ref_user["full_name"] if ref_user else "Unknown"
                    await context.bot.send_message(
                        chat_id=ref_id,
                        text=(
                            f"🎉 *Wah! Naya Referral Mila!*\n\n"
                            f"👤 *{user.full_name}* aapke link se join kiya!\n"
                            f"💰 *+{points_per_ref} Points* aapke wallet mein add ho gaye!\n\n"
                            f"📊 Total Points dekhne ke liye /start dabao"
                        ),
                        parse_mode="Markdown"
                    )
                except Exception:
                    pass

    # Main menu dikhao
    await query.edit_message_text(
        "✅ *Verification Successful!*\n\n🎊 Ab aap bot use kar sakte hain!",
        parse_mode="Markdown"
    )
    await asyncio.sleep(0.5)
    
    keyboard = await get_main_menu_keyboard()
    await context.bot.send_message(
        chat_id=user_id,
        text=(
            f"🏠 *Main Menu*\n\n"
            f"👋 Swagat hai *{user.first_name}* ji!\n\n"
            f"Neeche se koi option choose karo:"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    user = update.effective_user
    keyboard = await get_main_menu_keyboard()
    text = (
        f"🏠 *Main Menu*\n\n"
        f"👋 Swagat hai *{user.first_name}* ji!\n\n"
        f"Neeche se koi option choose karo:"
    )
    if edit and update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)
