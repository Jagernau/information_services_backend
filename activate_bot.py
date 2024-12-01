import requests
import config
TOKEN = config.TOKEN
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
