# crud.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from data_base.mysql_models_three import ServiceEvent
from data_base.db_conectors import MysqlDatabaseTwo, MysqlDatabaseThree
import data_base.mysql_models_two as models_two


class CrudService:
    @staticmethod
    async def get_actual_serv_two(data_now) -> List[models_two.InfoServObj]:
        """
        Асинхронный метод получения актуальных сервисов.
        """
        async for session in MysqlDatabaseTwo().get_session():
            result = await session.execute(
                select(models_two.InfoServObj).filter(
                    models_two.InfoServObj.subscription_start <= data_now,
                    models_two.InfoServObj.subscription_end >= data_now
                )
            )
            return result.scalars().all()

    @staticmethod
    async def add_report_to_three(
        time_event, id_serv_subscription, processing_status, monitoring_system,
        object_name, client_name, it_name, necessary_treatment, result, login
    ) -> None:
        """
        Асинхронное добавление отчёта.
        """
        async for session in MysqlDatabaseThree().get_session():
            report = ServiceEvent(
                time_event=time_event,
                id_serv_subscription=id_serv_subscription,
                processing_status=processing_status,
                monitoring_system=monitoring_system,
                object_name=object_name,
                client_name=client_name,
                it_name=it_name,
                necessary_treatment=necessary_treatment,
                result=result,
                login=login
            )
            session.add(report)
            await session.commit()

    @staticmethod
    async def get_sys_mon_name(sys_mon_id: int) -> Optional[str]:
        """
        Возвращает имя системы мониторинга по ID.
        """
        async for session in MysqlDatabaseTwo().get_session():
            result = await session.execute(
                select(models_two.MonitoringSystem).filter(
                    models_two.MonitoringSystem.mon_sys_id == sys_mon_id
                )
            )
            item = result.scalars().first()
            return item.mon_sys_name if item else None
    @staticmethod
    async def get_obj_name(serv_obj_sys_mon_id) -> str:
        async for session in MysqlDatabaseTwo().get_session():
            result = await session.execute(
                select(models_two.CaObject).filter(
                    models_two.CaObject.id == serv_obj_sys_mon_id
                )
            )
            item = result.scalars().first()  # Исправлено: itemn на item
            return item.object_name if item else None  # Проверка на наличие объекта

    @staticmethod
    async def get_client_name(sys_login, sys_password):
        async for session in MysqlDatabaseTwo().get_session():
            query = (
                select(
                    models_two.Contragent.ca_name,
                    models_two.Contragent.service_manager,
                ).select_from(models_two.LoginUser).outerjoin(
                    models_two.Contragent, models_two.LoginUser.contragent_id == models_two.Contragent.ca_id
                ).filter(
                    models_two.LoginUser.login == sys_login,
                    models_two.LoginUser.password == sys_password
                )
            )
            result = await session.execute(query)
            item = result.fetchone()
            return item if item else None  # Проверка на наличие объекта
