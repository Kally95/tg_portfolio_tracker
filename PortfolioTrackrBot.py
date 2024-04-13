import keys
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
from KucoinDemo import TradeAnalyser, analyse_trades
from utils import *

chat_id_to_notify = None
threshold = 30
notification_sent = {'win': False, 'loss': False}
losing_trades = []
winning_trades = []

async def check_portfolio_performance(context: CallbackContext):
    global notification_sent
    trade_analyser = TradeAnalyser(keys.api_key, keys.api_secret, keys.api_passphrase)
    portfolio_data_list = analyse_trades(trade_analyser)
    losers =  await format_losing_trade_data(portfolio_data_list)
    winners = await track_winning_trades(portfolio_data_list)
    for data in portfolio_data_list:
        if data['win_loss'] > threshold and not notification_sent['win']:
            await context.bot.send_message(chat_id=chat_id_to_notify, text=f"Notification: Your portfolio win percentage has exceeded {threshold}% 🚀🚀🚀. \n \n {winners}")
            notification_sent['win'] = True
            notification_sent['loss'] = False
        if data['win_loss'] < -threshold and not notification_sent['loss']:
            await context.bot.send_message(chat_id=chat_id_to_notify, text=f"Notification: Your portfolio loss percentage has exceeded -{threshold}% 📉📉📉.\n \n {losers}")
            notification_sent['loss'] = True  
            notification_sent['win'] = False 

async def set_percentage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        split_input = update.message.text.split()
        input_as_float = float(split_input[1])

        if input_as_float < 0 or input_as_float > 100:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please choose a threshold between 0 and 100!")
        else:
            global threshold
            threshold = input_as_float
            notification_sent['win'] = False
            notification_sent['loss'] = False
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Threshold of {threshold}% has been set!")
    except IndexError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /set <percentage>")
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The threshold must be a number between -100 and 100.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_id_to_notify
    chat_id_to_notify = update.effective_chat.id
    bot_name = context.bot.username
    user = update.effective_user
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hi {user.name}, I\'m {bot_name}. Please type /help for further assistance on how to use my portfolio tracking services.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_name = context.bot.username
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hi {user.name}, I\'m {bot_name}. I will track your Kucoin portfolio! If you would like an instantaneous report, you can type the following: \'portfolio\' or '/set <number>' to set your portfolio threshold!")

async def portfolio_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "portfolio" in update.message.text.lower():
        trade_analyser = TradeAnalyser(keys.api_key, keys.api_secret, keys.api_passphrase)
        portfolio_data_list = analyse_trades(trade_analyser)
        formatted_messages  = utils.format_trade_data(portfolio_data_list)
        formatted_data = "\n".join(formatted_messages)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=formatted_data)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I'm not quite sure what is you want. Please refer to /help or type in 'portfolio' for a report!")

async def track_losing_trades(portfolio_data_list):
    global losing_trades
    for currency in portfolio_data_list:
        if currency['win_loss'] < -threshold:
            losing_trades.append(currency['symbol'])

async def track_winning_trades(portfolio_data_list):
    global winning_trades
    for currency in portfolio_data_list:
        if currency['win_loss'] > threshold:
            winning_trades.append(currency['symbol'])

if __name__ == '__main__':
    application = ApplicationBuilder().token(keys.tg_bot_token).build()

    application.add_handler(CommandHandler("set", set_percentage))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), portfolio_update))

    application.job_queue.run_repeating(check_portfolio_performance, interval=5, first=0)


    application.run_polling()