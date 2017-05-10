# -*- coding: utf-8 -*-
"""
Created on Mon May  1 20:01:47 2017

@author: Andr
"""

import feedparser
import json
try:
    import urllib2
except:
    pass
import urllib
import datetime
from flask import make_response
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'fox': 'http://feeds.foxnews.com/foxnews/latest',
    'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication':'bbc', 'city': 'London,UK', 'currency_from':'GBP', 'currency_to':'USD'}
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=cb932829eacb6a0e9ee4f38bfbf112ed"
CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=27d8b8b00e8147bd914df34c75901c8d"

def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]

@app.route("/")
def home():
    # get customised headlines, based on user input or default
    publication = get_value_with_fallback("publication")
    articles = get_news(publication)
    
    # get customised weather based on user input or default
    city = get_value_with_fallback("city")
    weather = get_weather (city)
    
    # get customised currency based on user input or default
    currency_from = get_value_with_fallback("currency_from")
    currency_to = get_value_with_fallback("currency_to")
    rate, currencies = get_rate(currency_from, currency_to)
    
    # save cookies and return template
    response = make_response(render_template("home.html",
                                             articles=articles,
                                             weather=weather,
                                             currency_from=currency_from,
                                             currency_to=currency_to,
                                             rate=rate,
                                             currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response
    
def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']

def get_weather(query):
    try:
        query = urllib.quote(query)
    except:
        query = urllib.parse.quote(query)
    url = WEATHER_URL.format(query)
    try:
        data = urllib2.urlopen(url).read()
    except:
        data = urllib.request.urlopen(url).read()
    try:
        parsed = json.loads(data)
    except:
        parsed = json.loads(data.decode("utf-8"))
    weather = None
    if parsed.get('weather'):
        weather = {'description':parsed['weather'][0]['description'],
                   'temperature':parsed['main']['temp'],
                   'city':parsed['name'],
                   'country': parsed['sys']['country']
                   }
    return weather
    
def get_rate(frm, to):
    try:
        all_currency = urllib2.urlopen(CURRENCY_URL).read()
    except:
        all_currency = urllib.request.urlopen(CURRENCY_URL).read()
    try:
        parsed = json.loads(all_currency).get('rates')
    except:
        parsed = json.loads(all_currency.decode("utf-8")).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate / frm_rate, parsed.keys())

if __name__ == '__main__':
    app.run(port=5000, debug=True)