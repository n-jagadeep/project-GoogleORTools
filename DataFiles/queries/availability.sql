SELECT
  RA.resource_id
  , monday
  , tuesday
  , wednesday
  , thursday
  , friday
  , saturday
  , sunday
  , RA.rule_start_datetime
  , RA.rule_end_datetime
FROM
  cm_resource_availability as RA
WHERE
  resource_id in ${resourceIds}
  AND tenant_id = :tenantId
  AND (
    (
      (
        RA.rule_start_datetime >= :startDatetime
        AND RA.rule_start_datetime <= :endDatetime
      )
      OR (
        RA.rule_end_datetime >= :startDatetime
        AND RA.rule_end_datetime <= :endDatetime
      )
    )
    OR (
      RA.rule_start_datetime <= :startDatetime
      AND RA.rule_end_datetime >= :endDatetime
    )
  )
