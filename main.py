import os
import logging
from pathlib import Path
import time
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import pymysql.cursors
import lib.api as api

dotenv_path = Path('./.env')
load_dotenv(dotenv_path=dotenv_path)
telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
api_url = os.getenv('API_URL')

connection = pymysql.connect(host=os.getenv('MYSQL_HOST'),
                             user=os.getenv('MYSQL_USER'),
                             password=os.getenv('MYSQL_PASSWORD'),
                             database=os.getenv('MYSQL_DATABASE'),
                             cursorclass=pymysql.cursors.DictCursor)

print('Telegram ロボットが現在実行中です。')
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    dispatcher.add_error_handler(error)

#Show route status by input route name.
async def routeInfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.split(' ')
    if len(user_input) < 2:
        await update.message.reply_text('ルート名を入力してください。')
        return
    route_name = user_input[1]
    route_info = api.load_densha_info(api_url, route_name)
    route_status = route_info['results'][0]['route_status'][0]
    route_message = route_info['results'][0]['route_status'][1]
    if(route_status == '通常'):
        message = f'{route_name}は通常運転です.'
    else:
        message = f'{route_message}'
        
    await update.message.reply_text(f'{message}')
    
async def loadDenshaJob(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    try:
        user_input = update.message.text.split(' ')
        target_route = user_input[1]
        
        # Save the subscription to the database
        with connection.cursor() as cursor:
            sql = "INSERT INTO `user_subscription` (`related_user`, `target_route`, `created_at`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (chat_id, target_route, time.time()))
        connection.commit()    
        
        context.job_queue.run_repeating(loadDenshaJob, 600, first=None, last=None, name=None, chat_id=chat_id, data=target_route)    
        await update.effective_message.reply_text(f'{target_route}の遲延状況を每10分ごとに通知します。')
        
    except (IndexError, ValueError):
        await update.message.reply_text('ルート名を入力してください。')

app = ApplicationBuilder().token(telegram_token).build()

app.add_handler(CommandHandler('route', routeInfo))
app.add_handler(CommandHandler('subscribe', subscribe))

app.run_polling()
