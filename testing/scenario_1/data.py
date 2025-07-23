import datetime as dt
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import schema


tenant = schema.Tenant(id=uuid.uuid4(), name='Pro Kidney', code="PK")
org = schema.Organizations(id = uuid.uuid4(),
                           email_domain = 'naperville.prokidney.com',
                           tenant_id = tenant.id,
                           name = 'Naperville',
                           type = '',
                           )

john = schema.User(id=uuid.uuid4(), tenant_id=tenant.id, email='john@prokidney.com', user_type='')
mark = schema.User(id=uuid.uuid4(), tenant_id=tenant.id, email='mark@prokidney.com', user_type='')

chemist = schema.Roles(id=uuid.uuid4(), name='chemist', tenant_id=tenant.id)
surgeon = schema.Roles(id=uuid.uuid4(), name='surgeon', tenant_id=tenant.id)

userRole1 = schema.UserRoles(id=uuid.uuid4(), user_id=john.id, role_id=chemist.id)  # noqa N816
userRole2 = schema.UserRoles(id=uuid.uuid4(), user_id=mark.id, role_id=surgeon.id)  # noqa N816

holidays = [schema.OrganizationHolidays(organization_id = org.id,
                                        description = 'H1',
                                        start_datetime = dt.datetime(2024, 12, 25),
                                        end_datetime = dt.datetime(2024, 12, 25, 23, 59),
                                        ),
            schema.OrganizationHolidays(organization_id = org.id,
                                        description = 'H2',
                                        start_datetime = dt.datetime(2024, 12, 26),
                                        end_datetime = dt.datetime(2024, 12, 26, 23, 59),
                                        ),
            schema.OrganizationHolidays(organization_id = org.id,
                                        description = 'H3',
                                        start_datetime = dt.datetime(2024, 12, 31),
                                        end_datetime = dt.datetime(2024, 12, 31, 23, 59),
                                        ),
            schema.OrganizationHolidays(organization_id = org.id,
                                        description = 'H4',
                                        start_datetime = dt.datetime(2025, 1, 1),
                                        end_datetime = dt.datetime(2025, 1, 1, 23, 59),
                                        ),
            ]

resourceTypes = [schema.ResourceTypes(id=uuid.uuid4(), tenant_id=tenant.id, name='Clean Room', code='CR'),  # noqa N816
                 schema.ResourceTypes(id=uuid.uuid4(), tenant_id=tenant.id, name='O2 incubator', code='O2'),
                 schema.ResourceTypes(id=uuid.uuid4(), tenant_id=tenant.id, name='Chemist', code='Ch'),
                 schema.ResourceTypes(id=uuid.uuid4(), tenant_id=tenant.id, name='Surgeon', code='Su'),
                 ]

resources = [schema.Resources(id = uuid.uuid4(),
                              tenant_id = tenant.id,
                              type_id = resourceTypes[0].id,
                              organization_id = org.id,
                              user_id = None,
                              name = 'CR-01',
                              attributes = '',
                              ),
             schema.Resources(id = uuid.uuid4(),
                              tenant_id = tenant.id,
                              type_id = resourceTypes[1].id,
                              organization_id = org.id,
                              user_id = None,
                              name = 'O2-01',
                              attributes = '',
                              ),
             schema.Resources(id = uuid.uuid4(),
                              tenant_id = tenant.id,
                              type_id = resourceTypes[2].id,
                              organization_id = org.id,
                              user_id = john.id,
                              name = 'John',
                              attributes = '',
                              ),
             schema.Resources(id = uuid.uuid4(),
                              tenant_id = tenant.id,
                              type_id = resourceTypes[3].id,
                              organization_id = org.id,
                              user_id = mark.id,
                              name = 'Mark',
                              attributes = '',
                              ),
             ]

downtimes = [schema.ResourceDowntime(tenant_id = tenant.id,
                                     resource_id = john.id,
                                     start_datetime = dt.datetime(2024, 12, 24),
                                     end_datetime = dt.datetime(2024, 12, 24, 23, 59),
                                     ),

             schema.ResourceDowntime(tenant_id = tenant.id,
                                     resource_id = mark.id,
                                     start_datetime = dt.datetime(2024, 12, 29),
                                     end_datetime = dt.datetime(2024, 12, 29, 23, 59),
                                     ),
             ]

availabilities = [schema.ResourceAvailability(tenant_id = tenant.id,
                                              resource_id = john.id,
                                              monday = [{'from': dt.time(9).isoformat(), 'to': dt.time(17).isoformat()}],
                                              tuesday = [{'from': dt.time(9).isoformat(), 'to': dt.time(17).isoformat()}],
                                              wednesday = [{'from': dt.time(9).isoformat(), 'to': dt.time(17).isoformat()}],
                                              thursday = [{'from': dt.time(9).isoformat(), 'to': dt.time(17).isoformat()}],
                                              friday = [{'from': dt.time(9).isoformat(), 'to': dt.time(17).isoformat()}],
                                              saturday = [{}],
                                              sunday = [{}],

                                              rule_start_datetime = dt.datetime(2024, 12, 27),
                                              rule_end_datetime = dt.datetime(2024, 12, 30, 23, 59),
                                              ),

                  schema.ResourceAvailability(tenant_id = tenant.id,
                                              resource_id = john.id,
                                              monday = [{'from': dt.time(10).isoformat(), 'to': dt.time(16).isoformat()}],
                                              tuesday = [{'from': dt.time(10).isoformat(), 'to': dt.time(16).isoformat()}],
                                              wednesday = [{'from': dt.time(10).isoformat(), 'to': dt.time(16).isoformat()}],
                                              thursday = [{}],
                                              friday = [{}],
                                              saturday = [{}],
                                              sunday = [{}],

                                              rule_start_datetime = dt.datetime(2024, 12, 31),
                                              rule_end_datetime = dt.datetime(2025, 1, 10, 23, 59),
                                              ),

                  schema.ResourceAvailability(tenant_id = tenant.id,
                                              resource_id = mark.id,
                                              monday = [{'from': dt.time(9).isoformat(), 'to': dt.time(17).isoformat()}],
                                              tuesday = [{'from': dt.time(9).isoformat(), 'to': dt.time(17).isoformat()}],
                                              wednesday = [{'from': dt.time(9).isoformat(), 'to': dt.time(17).isoformat()}],
                                              thursday = [{'from': dt.time(9).isoformat(), 'to': dt.time(17).isoformat()}],
                                              friday = [{'from': dt.time(9).isoformat(), 'to': dt.time(17).isoformat()}],
                                              saturday = [{}],
                                              sunday = [{}],

                                              rule_start_datetime = dt.datetime(2025, 1, 1),
                                              rule_end_datetime = dt.datetime(2025, 1, 31, 23, 59),
                                              ),

                  schema.ResourceAvailability(tenant_id = tenant.id,
                                              resource_id = resources[0].id,
                                              monday = [{'from': dt.time(0).isoformat(), 'to': dt.time(23,59,59).isoformat()}],
                                              tuesday = [{'from': dt.time(0).isoformat(), 'to': dt.time(23,59,59).isoformat()}],
                                              wednesday = [{'from': dt.time(0).isoformat(), 'to': dt.time(23,59,59).isoformat()}],
                                              thursday = [{'from': dt.time(0).isoformat(), 'to': dt.time(23,59,59).isoformat()}],
                                              friday = [{'from': dt.time(0).isoformat(), 'to': dt.time(23,59,59).isoformat()}],
                                              saturday = [{}],
                                              sunday = [{}],

                                              rule_start_datetime = dt.datetime(2025, 1, 1),
                                              rule_end_datetime = dt.datetime(2025, 1, 31, 23, 59),
                                              ),

                  schema.ResourceAvailability(tenant_id = tenant.id,
                                              resource_id = resources[1].id,
                                              monday = [{'from': dt.time(9).isoformat(), 'to': dt.time(23,59,59).isoformat()}],
                                              tuesday = [{'from': dt.time(9).isoformat(), 'to': dt.time(23,59,59).isoformat()}],
                                              wednesday = [{'from': dt.time(9).isoformat(), 'to': dt.time(23,59,59).isoformat()}],
                                              thursday = [{'from': dt.time(9).isoformat(), 'to': dt.time(23,59,59).isoformat()}],
                                              friday = [{'from': dt.time(9).isoformat(), 'to': dt.time(23,59,59).isoformat()}],
                                              saturday = [{}],
                                              sunday = [{}],

                                              rule_start_datetime = dt.datetime(2025, 1, 1),
                                              rule_end_datetime = dt.datetime(2025, 1, 31, 23, 59),
                                              ),
                  ]

processing = schema.ScheduleTypes(id=uuid.uuid4(), tenant_id=tenant.id, name='Kidney Cell Count')

template = schema.ScheduleTemplates(id = uuid.uuid4(),
                                    tenant_id = tenant.id,
                                    organization_id = org.id,
                                    name = 'Variant 1',
                                    schedule_type_id = processing.id,
                                    )

scheduleTemplateTasks = [schema.ScheduleTemplateTasks(id = uuid.uuid4(),  # noqa N816
                                                      tenant_id = tenant.id,
                                                      schedule_template_id = template.id,
                                                      name = 'Task 1',
                                                      task_seq = 1,
                                                      delay_from_prev_seq = None,
                                                      start_time = None,
                                                      duration = dt.timedelta(hours=2),
                                                      ),

                         schema.ScheduleTemplateTasks(id = uuid.uuid4(),
                                                      tenant_id = tenant.id,
                                                      schedule_template_id = template.id,
                                                      name = 'Task 2',
                                                      task_seq = 2,
                                                      delay_from_prev_seq = dt.timedelta(days=1),
                                                      start_time = None,
                                                      duration = dt.timedelta(hours=1),
                                                      ),

                         schema.ScheduleTemplateTasks(id = uuid.uuid4(),
                                                      tenant_id = tenant.id,
                                                      schedule_template_id = template.id,
                                                      name = 'Task 3',
                                                      task_seq = 2,
                                                      delay_from_prev_seq = dt.timedelta(days=1),
                                                      start_time = None,
                                                      duration = dt.timedelta(hours=3),
                                                      ),

                         schema.ScheduleTemplateTasks(id = uuid.uuid4(),
                                                      tenant_id = tenant.id,
                                                      schedule_template_id = template.id,
                                                      name = 'Task 4',
                                                      task_seq = 3,
                                                      delay_from_prev_seq = dt.timedelta(days=1),
                                                      start_time = None,
                                                      duration = dt.timedelta(hours=2),
                                                      ),

                         ]

resourceReqs = [schema.ScheduleTemplateTaskResourceConfigs(tenant_id = tenant.id,  # noqa N816
                                                           schedule_template_task_id = scheduleTemplateTasks[0].id,
                                                           resource_type_id = resourceTypes[2].id,
                                                           resource_attributes= '',
                                                           count = 1,
                                                           ),

                schema.ScheduleTemplateTaskResourceConfigs(tenant_id = tenant.id,
                                                           schedule_template_task_id = scheduleTemplateTasks[0].id,
                                                           resource_type_id = resourceTypes[0].id,
                                                           resource_attributes= '',
                                                           count = 1,
                                                           ),

                schema.ScheduleTemplateTaskResourceConfigs(tenant_id = tenant.id,
                                                           schedule_template_task_id = scheduleTemplateTasks[1].id,
                                                           resource_type_id = resourceTypes[3].id,
                                                           resource_attributes= '',
                                                           count = 1,
                                                           ),

                schema.ScheduleTemplateTaskResourceConfigs(tenant_id = tenant.id,
                                                           schedule_template_task_id = scheduleTemplateTasks[1].id,
                                                           resource_type_id = resourceTypes[1].id,
                                                           resource_attributes= '',
                                                           count = 1,
                                                           ),

                schema.ScheduleTemplateTaskResourceConfigs(tenant_id = tenant.id,
                                                           schedule_template_task_id = scheduleTemplateTasks[2].id,
                                                           resource_type_id = resourceTypes[2].id,
                                                           resource_attributes= '',
                                                           count = 1,
                                                           ),

                schema.ScheduleTemplateTaskResourceConfigs(tenant_id = tenant.id,
                                                           schedule_template_task_id = scheduleTemplateTasks[2].id,
                                                           resource_type_id = resourceTypes[1].id,
                                                           resource_attributes= '',
                                                           count = 1,
                                                           ),

                schema.ScheduleTemplateTaskResourceConfigs(tenant_id = tenant.id,
                                                           schedule_template_task_id = scheduleTemplateTasks[3].id,
                                                           resource_type_id = resourceTypes[3].id,
                                                           resource_attributes= '',
                                                           count = 1,
                                                           ),

                schema.ScheduleTemplateTaskResourceConfigs(tenant_id = tenant.id,
                                                           schedule_template_task_id = scheduleTemplateTasks[3].id,
                                                           resource_type_id = resourceTypes[0].id,
                                                           resource_attributes= '',
                                                           count = 1,
                                                           ),
                ]


def main(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    insertThese = [tenant, org,
                   chemist, surgeon,
                   userRole1, userRole2,
                   resourceTypes,
                   resources,
                   holidays, downtimes, availabilities,
                   processing,
                   template, scheduleTemplateTasks,
                   resourceReqs,
                   ]

    for e in insertThese:
        if not isinstance(e, list):
            session.add(e)
            continue

        for row in e:
            session.add(row)

    session.commit()

    print(f"John: {john.id.hex}")  # noqa E 201
    print(f"Mark: {mark.id.hex}")  # noqa E 201
    print(f"Tenant: {tenant.id.hex}")  # noqa E 201
    print(f"Schedule Template: {template.id.hex}")  # noqa E 201


if __name__ == "__main__":
    print('starting')  # noqa T201

    engine = create_engine("sqlite:///DataFiles/data.db", echo=False)
    main(engine)

    print('done')  # noqa T201