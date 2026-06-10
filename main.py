import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters
)
from database.db import init_db
from handlers.start import start_command, verify_callback, show_main_menu
from handlers.user import (
    referral_callback, my_points_callback, wallet_callback, history_callback,
    redeem_callback, redeem_select_callback, handle_upi_input,
    stats_callback, leaderboard_callback, help_callback
)
from handlers.admin import (
    admin_command, adm_channels_callback, adm_add_channel_callback,
    adm_remove_channel_callback, adm_settings_callback, adm_set_points_callback,
    adm_redeems_callback, adm_view_request_callback, admin_approve_callback,
    admin_reject_callback, adm_users_callback, adm_broadcast_callback,
    adm_stats_callback, adm_admins_callback, handle_admin_input,
    adm_ban_callback, adm_unban_callback, adm_addpts_callback, adm_delch_callback
)
from config import BOT_TOKEN

async def handle_text(update, context):
    if await handle_admin_input(update, context): return
    await handle_upi_input(update, context)

async def main_menu_callback(update, context):
    await update.callback_query.answer()
    await show_main_menu(update, context, edit=True)

def main():
    init_db()
    print("🚀 Bot start ho raha hai...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("panel", admin_command))
    app.add_handler(CallbackQueryHandler(verify_callback, pattern="^verify$"))
    app.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(referral_callback, pattern="^referral$"))
    app.add_handler(CallbackQueryHandler(my_points_callback, pattern="^my_points$"))
    app.add_handler(CallbackQueryHandler(wallet_callback, pattern="^wallet$"))
    app.add_handler(CallbackQueryHandler(history_callback, pattern="^history$"))
    app.add_handler(CallbackQueryHandler(redeem_callback, pattern="^redeem$"))
    app.add_handler(CallbackQueryHandler(redeem_select_callback, pattern="^redeem_\\d+_"))
    app.add_handler(CallbackQueryHandler(stats_callback, pattern="^my_stats$"))
    app.add_handler(CallbackQueryHandler(leaderboard_callback, pattern="^leaderboard$"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help$"))
    app.add_handler(CallbackQueryHandler(admin_command, pattern="^adm_back$"))
    app.add_handler(CallbackQueryHandler(adm_channels_callback, pattern="^adm_channels$"))
    app.add_handler(CallbackQueryHandler(adm_add_channel_callback, pattern="^adm_add_channel$"))
    app.add_handler(CallbackQueryHandler(adm_remove_channel_callback, pattern="^adm_remove_channel$"))
    app.add_handler(CallbackQueryHandler(adm_settings_callback, pattern="^adm_settings$"))
    app.add_handler(CallbackQueryHandler(adm_set_points_callback, pattern="^adm_set_points$"))
    app.add_handler(CallbackQueryHandler(adm_redeems_callback, pattern="^adm_redeems$"))
    app.add_handler(CallbackQueryHandler(adm_view_request_callback, pattern="^adm_viewreq_"))
    app.add_handler(CallbackQueryHandler(admin_approve_callback, pattern="^admin_approve_"))
    app.add_handler(CallbackQueryHandler(admin_reject_callback, pattern="^admin_reject_"))
    app.add_handler(CallbackQueryHandler(adm_users_callback, pattern="^adm_users$"))
    app.add_handler(CallbackQueryHandler(adm_broadcast_callback, pattern="^adm_broadcast$"))
    app.add_handler(CallbackQueryHandler(adm_stats_callback, pattern="^adm_stats$"))
    app.add_handler(CallbackQueryHandler(adm_admins_callback, pattern="^adm_admins$"))
    app.add_handler(CallbackQueryHandler(adm_ban_callback, pattern="^adm_ban_"))
    app.add_handler(CallbackQueryHandler(adm_unban_callback, pattern="^adm_unban_"))
    app.add_handler(CallbackQueryHandler(adm_addpts_callback, pattern="^adm_addpts_"))
    app.add_handler(CallbackQueryHandler(adm_delch_callback, pattern="^adm_delch_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("✅ Bot ready! Polling chal raha hai...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
