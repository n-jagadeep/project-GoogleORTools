SELECT cm_resource_downtime.resource_id AS resourceId
      ,cm_resource_downtime.start_datetime AS startDatetime
      ,cm_resource_downtime.end_datetime AS endDatetime

FROM cm_resource_downtime

WHERE cm_resource_downtime.resource_id IN ${resourceIds}

  AND cm_resource_downtime.tenant_id = :tenantId
  AND (((cm_resource_downtime.start_datetime >= :startDatetime AND
         cm_resource_downtime.start_datetime <= :endDatetime
         )
 
         OR
 
        (cm_resource_downtime.end_datetime >= :startDatetime AND
         cm_resource_downtime.end_datetime <= :endDatetime
         )
        )

       OR

       (cm_resource_downtime.start_datetime <= :startDatetime AND
        cm_resource_downtime.end_datetime >= :endDatetime
        )
       )
