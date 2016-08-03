import telebot
import constants
import requests
import datetime as dt

bot = telebot.TeleBot(constants.Token)
dtoday = dt.datetime.today()
curdate = dtoday.strftime("%Y-%m-%d")
curdatedisplay = dtoday.strftime("%d %B")
day = dt.timedelta(days=1)
week = dt.timedelta(days=7)
month = dt.timedelta(days=30)
curdict = ['145', '292']  # Currency IDs


def getrates(cur_id, date1, date2):
    return requests.get("http://www.nbrb.by/API/ExRates/Rates/Dynamics/%s?startDate=%s&endDate=%s " % (cur_id, date1, date2))


def genmsgrow(cur_id, dict):
    if cur_id == "145":
        flag = u'\U0001F1FA\U0001F1F8' + ' USD'
    elif cur_id == "292":
        flag = u'\U0001F1EA\U0001F1FA' + ' EUR'
    else:
        flag = "--- ---"
    minrate = dict[0]['Cur_OfficialRate']
    maxrate = dict[len(dict)-1]['Cur_OfficialRate']
    delta = maxrate-minrate
    deltaper = (maxrate / minrate * 100) - 100
    if maxrate == minrate:
        direction = "\u2194"
    elif maxrate > minrate:
        direction = "\u2197"
    else:
        direction = "\u2198"

    msg = flag + " - " + str(maxrate) + " " + direction + " " + "%.4f" % delta + " (" + "%.2f" % deltaper + "%)"
    return msg


def genmsg(date1, date2, curdict1, displaydate, period):
    msg = ""
    for cur_id in curdict1:
        rawdata = getrates(cur_id, date1, date2)
        data = rawdata.json()
        if len(data) > 0:
            msg = msg + "\n" + genmsgrow(cur_id, data)
    title = "Официальные курсы НБРБ на %s:" % displaydate
    footer = "период: %s" % period
    msg = title + msg + "\n" + footer
    return msg


@bot.message_handler(commands=['get', 'start'])
def handle_text(message):
    datefrom = (dtoday - day).strftime("%Y-%m-%d")
    bot.send_message(message.chat.id, genmsg(datefrom, curdate, curdict, curdatedisplay, "1 день"))


@bot.message_handler(commands=['getweek'])
def handle_text(message):
    datefrom = (dtoday - week).strftime("%Y-%m-%d")
    bot.send_message(message.chat.id, genmsg(datefrom, curdate, curdict, curdatedisplay, "7 дней"))


@bot.message_handler(commands=['getmonth'])
def handle_text(message):
    datefrom = (dtoday - month).strftime("%Y-%m-%d")
    bot.send_message(message.chat.id, genmsg(datefrom, curdate, curdict, curdatedisplay, "30 дней"))


@bot.message_handler(commands=['help'])
def handle_text(message):
    bot.send_message(message.chat.id, constants.Description)


bot.polling(none_stop=True, interval=0)
