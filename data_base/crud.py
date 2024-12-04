import data_base.mysql_models_two as models_two
import data_base.mysql_models_three as models_three
from data_base.db_conectors import MysqlDatabaseTwo
from data_base.db_conectors import MysqlDatabaseThree

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

def add_report_to_three(
            time_event, # 'Время события'
            id_serv_subscription, # 'ID подписки'
            processing_status, # 'Статус обработки'
            monitoring_system, # 'Система мониторинга' --- -
            object_name, # 'Имя объекта мониторинга' --- -
            client_name, # 'Имя клиента' --- - 
            it_name, # 'Имя фамилия ИТ специалиста' ---
            necessary_treatment, # 'Нужна ли обработка IT специалистом'
            result
        ):
    """
    Добавляется отчёт в Базу данных 2
    """
    db = MysqlDatabaseThree()
    session = db.session
    report = models_three.ServiceEvent(
                time_event=time_event,
                id_serv_subscription=id_serv_subscription,
                processing_status=processing_status,
                monitoring_system=monitoring_system,
                object_name=object_name,
                client_name=client_name,
                it_name=it_name,
                necessary_treatment=necessary_treatment,
                result=result
            )
    session.add(report)
    session.commit()
    session.close()


def get_sys_mon_name(sys_mon_id) -> str:
    db = MysqlDatabaseTwo()
    session = db.session
    result = session.query(models_two.MonitoringSystem).filter(
            models_two.MonitoringSystem.mon_sys_id == sys_mon_id
            ).first()
    session.close()
    return result.mon_sys_name

def get_obj_name(serv_obj_sys_mon_id) -> str:
    db = MysqlDatabaseTwo()
    session = db.session
    result = session.query(models_two.CaObject).filter(
            models_two.CaObject.id == serv_obj_sys_mon_id
            ).first()
    session.close()
    return result.object_name

def get_client_name(sys_login, sys_password):
    db = MysqlDatabaseTwo()
    session = db.session
    result = session.query(
            models_two.Contragent.ca_name,
            models_two.Contragent.service_manager,
            ).outerjoin(
                    models_two.Contragent, models_two.LoginUser.contragent_id == models_two.Contragent.ca_id
                    ).filter(
                            models_two.LoginUser.login == sys_login,
                            models_two.LoginUser.password == sys_password
                            ).first()
    session.close()
    return result[0], result[1]
