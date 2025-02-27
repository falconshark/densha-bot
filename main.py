import os
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import lib.api as api

dotenv_path = Path('./.env')
load_dotenv(dotenv_path=dotenv_path)
telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
api_url = os.getenv('API_URL')

print('Telegram ロボットが現在実行中です。')

#Show route status by input route name.
async def routeInfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.split(' ')
    if len(user_input) < 2:
        await update.message.reply_text('ルート名を入力してください。')
        return
    route_name = user_input[1]
    route_info = api.load_densha_info(api_url, route_name)
    route_status = route_info['results'][0]['route_status']
    if(route_status == '通常'):
        message = f'{route_name}は通常運転です'
    else:
        message = f'{route_name}は遅延しています'
        
    await update.message.reply_text(f'{message}')

#Register Chat ID   
async def routeInfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.split(' ')
    if len(user_input) < 2:
        await update.message.reply_text('ルート名を入力してください。')
        return
    route_name = user_input[1]
    route_info = api.load_densha_info(api_url, route_name)
    route_status = route_info['results'][0]['route_status']
    if(route_status == '通常'):
        message = f'{route_name}は通常運転です'
    else:
        message = f'{route_name}は遅延しています'
        
    await update.message.reply_text(f'{message}')

app = ApplicationBuilder().token(telegram_token).build()

app.add_handler(CommandHandler("route", routeInfo))

app.run_polling()
