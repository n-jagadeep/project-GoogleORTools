SELECT
FROM cm_resource_availability as RA
INNER JOIN cm_resource_downtime as DT
        ON RA.tenant_id = DT.tenant_id AND
           RA.resource_id = DT.resource_id
INNER JOIN organizaions as O
        ON O.tenant_id = DT.tenant_id
INNER JOIN cm_organization_holidays as H
        ON H.organization_id = O.id
INNER JOIN cm_resources as R
        ON R.organization_id = O.id AND
           R.id = DT.resource_id AND
           R.tenant_id = DT.tenant_id
WHERE R.id IN ?
  AND 
