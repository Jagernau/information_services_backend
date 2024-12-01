from os.path import join
import data_base.mysql_models as models
from data_base.bd_conectors import MysqlDatabase
from sqlalchemy import func, or_, and_
from sqlalchemy import case


