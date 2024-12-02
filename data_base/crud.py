import data_base.mysql_models_two as models_two
from data_base.db_conectors import MysqlDatabaseTwo
from sqlalchemy import func, or_, and_

def get_actual_serv_two(data_now):
    """
    Отдаёт логи по объектам за периуд времени
    Добавленные
    """
    db = MysqlDatabaseTwo()
    session = db.session
    result = session.query(models_two.InfoServObj).filter(
            models_two.InfoServObj.subscription_start <= data_now,
            models_two.InfoServObj.subscription_end >= data_now
            ).all()
    session.close()
    return result


