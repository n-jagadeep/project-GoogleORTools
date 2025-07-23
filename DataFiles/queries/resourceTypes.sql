SELECT RT.id
      ,COALESCE(R.user_id, R.id)

FROM cm_resource_types as RT
INNER JOIN resources as R
        ON R.type_id = RT.id
