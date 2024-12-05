# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class ServiceEvent(Base):
    __tablename__ = 'service_event'
    __table_args__ = {'comment': 'События сервисов'}

    id_event = Column(Integer, primary_key=True, comment='ID события')
    time_event = Column(DateTime, comment='Время события')
    id_serv_subscription = Column(Integer, comment='ID подписки')
    processing_status = Column(Integer, comment='Статус обработки')
    monitoring_system = Column(String(100, 'utf8mb3_unicode_ci'), comment='Система мониторинга')
    object_name = Column(String(150, 'utf8mb3_unicode_ci'), comment='Имя объекта мониторинга')
    client_name = Column(String(300, 'utf8mb3_unicode_ci'), comment='Имя клиента')
    it_name = Column(String(300, 'utf8mb3_unicode_ci'), comment='Имя фамилия ИТ специалиста')
    necessary_treatment = Column(TINYINT, comment='Нужна ли обработка IT специалистом')
    result = Column(String(1000, 'utf8mb3_unicode_ci'), comment='Результат сервиса')
    login = Column(String(100, 'utf8mb3_unicode_ci'), comment='Логин в системе мониторинга предполагается почта')
    password = Column(String(100, 'utf8mb3_unicode_ci'), comment='Пароль')
