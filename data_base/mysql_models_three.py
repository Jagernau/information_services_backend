# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String, text
from sqlalchemy.dialects.mysql import TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class ServiceEvent(Base):
    __tablename__ = 'service_event'
    __table_args__ = {'comment': 'События сервисов'}

    id_event = Column(Integer, primary_key=True, comment='ID события')
    time_event = Column(DateTime, comment='Время события')
    id_serv_subscription = Column(Integer, comment='ID подписки')
    processing_status = Column(Integer, comment='Статус обработки 0-не оработанна 1 - обработанна')
    monitoring_system = Column(String(100, 'utf8mb3_unicode_ci'), comment='Система мониторинга')
    object_name = Column(String(150, 'utf8mb3_unicode_ci'), comment='Имя объекта мониторинга')
    client_name = Column(String(300, 'utf8mb3_unicode_ci'), comment='Имя клиента')
    it_name = Column(String(300, 'utf8mb3_unicode_ci'), comment='Имя фамилия ИТ специалиста')
    necessary_treatment = Column(TINYINT, comment='Нужна ли обработка IT специалистом 0 - не нужна обработка 1 - нужна')
    result = Column(VARCHAR(4000), comment='Результат сервиса')
    login = Column(String(100, 'utf8mb3_unicode_ci'), comment='Логин в системе мониторинга предполагается почта')
    password = Column(String(100, 'utf8mb3_unicode_ci'), comment='Пароль')
    send_status = Column(TINYINT, server_default=text("'0'"), comment='Статус отправленно или нет 0 - не отправленно 1 - отправленно')
    ok_desk_report_id = Column(Integer, comment='ID заявки в ОКДЕСК')
    db_obj_id = Column(Integer, comment='ID объекта в бд')
    client_id = Column(Integer, comment='ID Клиента в ДБ_2')
    it_id = Column(Integer, comment='ID Ответственного ИТ специалиста в БД_2')
    ok_desk_obj_id = Column(Integer, comment='id объекта в ОКДЕСКА')
    ok_client_id = Column(Integer, comment='ID Клиента ОКДЕСКА')
    place_shipment = Column(Integer, comment='Место отправки 0- ОКДЕСК 1-ПОЧТА 2-СМС')
    fault_type = Column(Integer, comment='Тип неисправности 0-Не на связи более месяца')
