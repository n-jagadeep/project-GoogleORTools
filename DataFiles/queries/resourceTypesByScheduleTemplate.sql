SELECT RT.id
      ,COALESCE(R.user_id, R.id)

FROM cm_schedule_templates as T
INNER JOIN cm_schedule_template_tasks as TT
        ON T.id = TT.schedule_template_id
INNER JOIN cm_schedule_template_task_resource_configs as RC
        ON TT.id = rc.schedule_template_task_id
INNER JOIN cm_resource_types as RT
        ON (CASE
             WHEN RC.resource_id IS NOT NULL THEN NULL
             ELSE RC.resource_type_id
            END) = RT.id
INNER JOIN resources as R
        ON RT.id = R.type_id

WHERE T.id  = :scheduleTemplateId
