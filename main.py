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
    
#Everytime at start. Loadthe subscription from the database and start the job.
def init(app):
    with connection.cursor() as cursor:
        sql = "SELECT * FROM `user_subscription`"
        cursor.execute(sql)
        result = cursor.fetchall()
        for row in result:
            chat_id = row['related_user']
            target_route = row['target_route']
            job_name = f'{chat_id}_{target_route}'
            app.job_queue.run_repeating(loadDenshaJob, 200, first=None, last=None, name=job_name, chat_id=chat_id, data=target_route)
    connection.commit()

#Init Function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('こんにちは！\n'
                                    'このボットは、JR東日本の遅延情報を提供します。\n'
                                    '以下のコマンドを使用してください。\n'
                                    '/route [route_name] : ルートの遅延情報を表示します。\n'
                                    '/subscribe [route_name] : ルートの遅延情報を監視し、遅延情報を通知します。\n'
                                    '/unsubscribe [route_name] : ルートの遅延情報の監視を解除します。\n'
                                    '/unsubscribe_all : 全てのルートの遅延情報の監視を解除します。\n')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('このボットは、JR東日本の遅延情報を提供します。\n'
                                    '以下のコマンドを使用してください。\n'
                                    '/route [route_name] : ルートの遅延情報を表示します。\n'
                                    '/subscribe [route_name] : ルートの遅延情報を監視し、遅延情報を通知します。\n'
                                    '/unsubscribe [route_name] : ルートの遅延情報の監視を解除します。\n'
                                    '/unsubscribe_all : 全てのルートの遅延情報の監視を解除します。\n')

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
    route_name = job.data
    route_info = api.load_densha_info(api_url, route_name)
    route_status = route_info['results'][0]['route_status'][0]
    route_message = route_info['results'][0]['route_status'][1]
    
    if(route_status != '通常'):
        with connection.cursor() as cursor:
            #Check last message to avoid dulicate notifaction.
            last_message_sql = "SELECT * FROM `user_subscription` WHERE related_user = %s and target_route = %s"
            cursor.execute(last_message_sql, (job.chat_id, route_name))
            last_message = cursor.fetchone()['last_message']
            #If last message is not the same as the current message, send the message.
            if last_message != route_message:  
                sql = "UPDATE `user_subscription` SET `last_message` = %s WHERE related_user = %s and target_route = %s"
                cursor.execute(sql, (route_message, job.chat_id, route_name))
                connection.commit()
                await context.bot.send_message(job.chat_id, text=f"{route_message}")
                        
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    try:
        user_input = update.message.text.split(' ')
        target_route = user_input[1]
        job_name = f'{chat_id}_{target_route}'
        
        # Save the subscription to the database
        with connection.cursor() as cursor:
            sql = "INSERT INTO `user_subscription` (`related_user`, `target_route`, `created_at`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (chat_id, target_route, time.time()))
        connection.commit()    
        
        context.job_queue.run_repeating(loadDenshaJob, 200, first=None, last=None, name=job_name, chat_id=chat_id, data=target_route)    
        await update.effective_message.reply_text(f'{target_route}の遲延状況を每10分ごとに監視します。')
        
    except (IndexError, ValueError):
        await update.message.reply_text('ルート名を入力してください。')

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    try:
        user_input = update.message.text.split(' ')
        target_route = user_input[1]
        
        # Remove the subscription to the database
        with connection.cursor() as cursor:
            sql = "DELETE FROM `user_subscription` WHERE related_user = %s and target_route = %s"
            cursor.execute(sql, (chat_id, target_route))
        connection.commit()
        
        job_name = f'{chat_id}_{target_route}'
        current_jobs = context.job_queue.get_jobs_by_name(job_name)
        
        for job in current_jobs:
            job.schedule_removal()
    
        await update.effective_message.reply_text(f'{target_route}の監視を解除しました。')
        
    except (IndexError, ValueError):
        await update.message.reply_text('ルート名を入力してください。')
        
async def unsubscribe_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    try:

        # Remove the subscription from the database
        with connection.cursor() as cursor:
            load_subscription_sql = "SELECT * FROM `user_subscription`"
            cursor.execute(load_subscription_sql)
            result = cursor.fetchall()
            for row in result:
                target_route = row['target_route']
                job_name = f'{chat_id}_{target_route}'
                delete_subscription_sql = "DELETE FROM `user_subscription` WHERE related_user = %s"
                cursor.execute(delete_subscription_sql, (chat_id))
                
                # Remove all job from the job queue
                job_name = f'{chat_id}_{target_route}'
                current_jobs = context.job_queue.get_jobs_by_name(job_name)
                for job in current_jobs:
                    job.schedule_removal()
        connection.commit()          
        await update.effective_message.reply_text(f'全での監視を解除しました。')
        
    except (IndexError, ValueError):
        await update.message.reply_text('ルート名を入力してください。')
        
app = ApplicationBuilder().token(telegram_token).build()

app.add_handler(CommandHandler('help', help))
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('route', routeInfo))
app.add_handler(CommandHandler('subscribe', subscribe))
app.add_handler(CommandHandler('unsubscribe', unsubscribe))
app.add_handler(CommandHandler('unsubscribe_all', unsubscribe_all))

init(app)

app.run_polling()
