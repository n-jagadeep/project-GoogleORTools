SELECT SE.resource_id
      ,SE.start_time
      ,SE.end_time

FROM cm_schedule_events as SE
INNER JOIN cm_schedule_template_tasks as TT
        ON (SE.task_id = TT.id AND
            SE.tenant_id = TT.id
            )
INNER JOIN cm_schedule_template_task_resource_configs as RC
        ON (RC.schedule_template_task_id = TT.id AND
            RC.tenant_id = TT.tenant_id
            )

WHERE SE.resource_id IN ${resourceIds}
