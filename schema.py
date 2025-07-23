import datetime as dt
import re
import typing
import uuid

from sqlalchemy import String, ForeignKey, DATETIME, Integer, Interval, JSON, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:  # noqa N805
        name_list = re.findall(r"[A-Z][a-z\d]*", cls.__name__)
        return "_".join(name_list).lower()


class Tenant(Base):
    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50))
    code: Mapped[str] = mapped_column(String(20))


class User(Base):
    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(100))
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))
    user_type: Mapped[str] = mapped_column(String(20))


class Roles(Base):
    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50))
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))


class UserRoles(Base):
    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("user.id"))
    role_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("roles.id"))


class Patient(Base):
    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("user.id"))
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))
    first_name: Mapped[str] = mapped_column(String(50))
    middle_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))


class Organizations(Base):
    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))
    name: Mapped[str] = mapped_column(String(50))
    email_domain: Mapped[str] = mapped_column(String(50))
    type: Mapped[str] = mapped_column(String(20))


class OrganizationHolidays(Base):
    __tablename__ = 'cm_organization_holidays'

    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("organizations.id"))
    description: Mapped[str] = mapped_column(String(50))
    start_datetime: Mapped[dt.datetime] = mapped_column(DATETIME)
    end_datetime: Mapped[dt.datetime] = mapped_column(DATETIME)


class ResourceTypes(Base):
    __tablename__ = 'cm_resource_types'

    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))
    name: Mapped[str] = mapped_column(String(50))
    code: Mapped[str] = mapped_column(String(20))


class Resources(Base):
    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))
    type_id: Mapped[str] = mapped_column(ForeignKey("cm_resource_types.id"))
    organization_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("organizations.id"))
    user_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("user.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(50))
    attributes: Mapped[dict[str, typing.Any]] = mapped_column(JSON)


class ResourceDowntime(Base):
    __tablename__ = 'cm_resource_downtime'

    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))
    resource_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("resources.id"))
    start_datetime: Mapped[dt.datetime] = mapped_column(DATETIME)
    end_datetime: Mapped[dt.datetime] = mapped_column(DATETIME)


class ResourceAvailability(Base):
    __tablename__ = 'cm_resource_availability'

    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))
    resource_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("resources.id"))

    monday: Mapped[dict[str, typing.Any]] = mapped_column(JSON)
    tuesday: Mapped[dict[str, typing.Any]] = mapped_column(JSON)
    wednesday: Mapped[dict[str, typing.Any]] = mapped_column(JSON)
    thursday: Mapped[dict[str, typing.Any]] = mapped_column(JSON)
    friday: Mapped[dict[str, typing.Any]] = mapped_column(JSON)
    saturday: Mapped[dict[str, typing.Any]] = mapped_column(JSON)
    sunday: Mapped[dict[str, typing.Any]] = mapped_column(JSON)

    rule_start_datetime: Mapped[dt.datetime] = mapped_column(DATETIME)
    rule_end_datetime: Mapped[dt.datetime] = mapped_column(DATETIME)


class ScheduleTypes(Base):
    __tablename__ = 'cm_schedule_types'

    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))

    name: Mapped[str] = mapped_column(String(50))


class ScheduleTemplates(Base):
    __tablename__ = 'cm_schedule_templates'

    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))
    organization_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column(String(50))
    schedule_type_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("cm_schedule_types.id"))


class ScheduleTemplateTasks(Base):
    __tablename__ = 'cm_schedule_template_tasks'

    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))
    schedule_template_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("cm_schedule_templates.id"))
    name: Mapped[str] = mapped_column(String(50))
    task_seq: Mapped[int] = mapped_column(Integer)
    delay_from_prev_seq: Mapped[dt.timedelta] = mapped_column(Interval, nullable=True)
    start_time: Mapped[dt.datetime] = mapped_column(DATETIME, nullable=True)
    duration: Mapped[dt.timedelta] = mapped_column(Interval)


class ScheduleTemplateTaskResourceConfigs(Base):
    __tablename__ = 'cm_schedule_template_task_resource_configs'

    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))
    schedule_template_task_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("cm_schedule_template_tasks.id"))

    resource_type_id: Mapped[str] = mapped_column(ForeignKey("cm_resource_types.id"))
    resource_id: Mapped[str] = mapped_column(ForeignKey("resources.id"), nullable=True)
    resource_attributes: Mapped[dict[str, typing.Any]] = mapped_column(JSON)
    count: Mapped[int] = mapped_column(Integer)


class Schedules(Base):
    __tablename__ = 'cm_schedules'

    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))
    organization_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column(String(50))
    schedule_template_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("cm_schedule_templates.id"))
    start_datetime: Mapped[dt.datetime] = mapped_column(DATETIME)
    end_datetime: Mapped[dt.datetime] = mapped_column(DATETIME)
    patient_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("user.id"))


class ScheduleEvents(Base):
    __tablename__ = 'cm_schedule_events'

    id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("tenant.id"))
    schedule_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("cm_schedules.id"))
    task_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("cm_schedule_template_tasks.id"))
    resource_id: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), nullable=True)
    start_time: Mapped[dt.datetime] = mapped_column(DATETIME)
    end_time: Mapped[dt.datetime] = mapped_column(DATETIME)


if __name__ == "__main__":
    print('starting')  # noqa T201

    engine = create_engine("sqlite:///DataFiles/data.db", echo=False)
    Base.metadata.create_all(engine)

    print('done')  # noqa T201
