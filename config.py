from os import environ as envi
from dotenv import load_dotenv

load_dotenv()


TOKEN=envi.get('TOKEN')
CHAT_ID=envi.get('CHAT_ID')
DB_HOST=envi.get('DB_HOST')
MYSQL_USER=envi.get('MYSQL_USER')
MYSQL_DB_NAME=envi.get('MYSQL_DB_NAME')
MYSQL_PASSWORD=envi.get('MYSQL_PASSWORD')
MYSQL_PORT=envi.get('MYSQL_PORT')

connection_mysql = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{DB_HOST}:{MYSQL_PORT}/{MYSQL_DB_NAME}"


GLONASS_BASED_ADRESS=envi.get('GLONASS_BASED_ADRESS')
GLONASS_LOGIN=envi.get('GLONASS_LOGIN')
GLONASS_PASS=envi.get('GLONASS_PASS')
