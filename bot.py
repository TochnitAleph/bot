#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
import logging
import datetime
import requests
import json

filekey = open('key', 'r')
key = filekey.readline().rstrip()

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename = u'/var/tmp/telega.log')
updater = Updater(token=key)
dispatcher = updater.dispatcher


def timeCommand(bot, update):
    message = update.message.text.split(' ')
    try:
        response = str(datetime.datetime.fromtimestamp(float(message[1])))
    except:
        response = 'Error in UNIX time'
    bot.send_message(chat_id=update.message.chat_id, text=response)


def helpCommand(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='/time POSIX to convert date\n/weather town print weather in town\n/price currency print price of currency')



def sayhi(bot, job):
    r = requests.get("https://api.coinmarketcap.com/v1/ticker/bitcoin")
    answer = "Bitcoin price is {price} USD".format(price = json.loads(r.text)[0]["price_usd"])
    job.context.message.reply_text(answer)


def time(bot, update, job_queue):
    if update.message.text.split(' ')[1] == 'bitcoin': 
        job = job_queue.run_repeating(sayhi, 3, context=update)
    else:
        bot.send_message(chat_id=update.message.chat_id, text='nope') 

def start(bot, update):
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')


def alarm(bot, job):
    """Send the alarm message."""
    bot.send_message(job.context, text='Beep!')


def set_timer(bot, update, args, job_queue, chat_data):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue
        job = job_queue.run_once(alarm, due, context=chat_id)
        chat_data['job'] = job

        update.message.reply_text('Timer successfully set!')

    except (ValueError, IndexError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(bot, update, chat_data):
    """Remove the job if the user changed their mind."""
    if 'job' not in chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Timer successfully unset!')



def price(bot, update):
    url = 'https://api.coinmarketcap.com/v1/ticker/'
    answer = "Error in currency"
    currency = 'bitcoin'
    try:
        currency = update.message.text.split(' ')[1]
    except:
        pass
    r = requests.get(url+'/'+currency.lower())
    if r.status_code == 200: 
        response = json.loads(r.text)
        answer = "{currency} price is {price} USD".format(currency = currency, price = response[0]["price_usd"])
        bot.send_message(chat_id=update.message.chat_id, text=answer)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=answer)    

start_write_handler = CommandHandler('h', helpCommand)
time_write_handler = CommandHandler('time', timeCommand)
price_handler =  CommandHandler('price', price)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", start))
dispatcher.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
dispatcher.add_handler(CommandHandler("unset", unset, pass_chat_data=True))
dispatcher.add_handler(start_write_handler)
dispatcher.add_handler(time_write_handler)
dispatcher.add_handler(price_handler)
updater.start_webhook(listen='127.0.0.1', port=5000, url_path=key)
updater.idle()
