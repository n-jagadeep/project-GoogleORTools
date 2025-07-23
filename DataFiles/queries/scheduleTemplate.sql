SELECT RC.resource_id
      ,RC.resource_type_id
      ,TT.id
      ,TT.task_seq
      ,TT.delay_from_prev_seq
      ,TT.duration

FROM cm_schedule_template_tasks as TT
INNER JOIN cm_schedule_template_task_resource_configs as RC
        ON RC.schedule_template_task_id = TT.id

WHERE TT.schedule_template_id = :scheduleTemplateId

ORDER BY TT.task_seq
