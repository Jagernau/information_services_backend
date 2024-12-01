import logging
from time import sleep
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import config
import serv_func

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Ваш токен и chat_id
TOKEN = config.TOKEN
CHAT_ID = config.CHAT_ID

async def send_yest_fuel_flow(context: ContextTypes.DEFAULT_TYPE):
    """
    Присылание отчёта по расходу топлива за вчера
    -- от 00:01 - 23:59
    """
    result = serv_func.get_yest_serv_fuel_flow(config.GLONASS_LOGIN, config.GLONASS_PASS)
    if result != None:
        await context.bot.send_message(chat_id=CHAT_ID, text=result)
    else:
        pass

async def send_yest_fuel_refueling(context: ContextTypes.DEFAULT_TYPE):
    """ 
    Присылание отчёта по сливам и заправкам за вчера
    """
    result = serv_func.get_yest_serv_fuel_up_down(config.GLONASS_LOGIN, config.GLONASS_PASS)
    if result != None:
        await context.bot.send_message(chat_id=CHAT_ID, text=result)
    else:
        pass

async def send_now_fuel_refueling(context: ContextTypes.DEFAULT_TYPE):
    """ 
    Присылание отчёта по сливам и заправкам в прослушку 5 мин
    """
    result = serv_func.get_now_serv_fuel_up_down(config.GLONASS_LOGIN, config.GLONASS_PASS)
    if result != None:
        await context.bot.send_message(chat_id=CHAT_ID, text=result)
    else:
        pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен!")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Настройка планировщика
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_yest_fuel_flow, 'cron', hour=9, minute=00, args=[application])
    scheduler.add_job(send_yest_fuel_refueling, 'cron', hour=13, minute=31, args=[application])
    scheduler.add_job(send_now_fuel_refueling, 'interval', seconds = 300, args=[application])


    scheduler.start()

    # Запуск бота
    application.run_polling()

