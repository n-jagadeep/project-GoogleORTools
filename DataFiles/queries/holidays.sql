SELECT COALESCE(R.user_id, R.id)
      ,OH.start_datetime
      ,OH.end_datetime

FROM resources as R
INNER JOIN organizations as O
        ON R.organization_id = O.id
INNER JOIN cm_organization_holidays as OH
        ON OH.organization_id = O.id

WHERE O.tenant_id = :tenantId
  AND R.tenant_id = :tenantId
  AND COALESCE(R.user_id, R.id) in ${resourceIds}
  AND (((OH.start_datetime >= :startDatetime AND
         OH.start_datetime <= :endDatetime
         )

         OR

        (OH.end_datetime >= :startDatetime AND
         OH.end_datetime <= :endDatetime
         )
        )

       OR

       (OH.start_datetime <= :startDatetime AND
        OH.end_datetime >= :endDatetime
        )
       )

