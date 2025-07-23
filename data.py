import collections
import datetime as dt
import json
import os
import string
import sqlite3
import uuid


def getAvailabilities(dbFilepath, tenantId, resourceIds, startDatetime, endDatetime):
    '''
    Get the availabilities and unavailabilities of all the requested resources.
    Unavailabilities include holidays, downtimes, already scheduled times, etc.

    :param dbFilepath: path like. The path to the SQLite database that contains all the data
    :param tenantId: UUID. the ID of the tenant for whom we're getting resource data
    :param resourceIds: List of UUIDs. The IDs of the resources for which we want the availabilities
    :param startDatetime: dt.datetime. This marks the start time of the period within which we want to compute availabilities
    :param endDatetime: dt.datetime. This marks the end time of the period within which we want to compute availabilities
    :return: (availability, scheduled, downtimes, holidays). The latter three are dictionaries in the following format:
            {resourceId: [(start, end)]}. `resourceId` is a UUID from the `resourceIds` parameter.
            `start` and `end` are datetime objects describing the periods of unavilability
            `availability` has a slightly different format: {resourceId: {(start, end): [days...]}}, where:
                `resourceId` is a UUID from the `resourceIds` parameter
                `start` and `end` are datetime objects describing the period of validity of the availabilty rule
                `days` represent monday - sunday. Each day is a dict of the following format {'from: startTime, 'to':endTime}
                    `startTime` and `endTiem` are  datetime.time objects
    '''

    queryLoc = os.path.join("DataFiles", 'queries')

    conn = sqlite3.connect(dbFilepath)
    cur = conn.cursor()

    sqliteDtFmt = "%Y-%m-%d %H:%M:%S.%f"
    resourceIdsArray = '('+','.join(map(lambda s: f"'{s}'", resourceIds))+")"

    # regular availability patterns
    with open(os.path.join(queryLoc, 'availability.sql')) as infile:
        query = infile.read().strip()

    query = string.Template(query).substitute({'resourceIds': resourceIdsArray})

    availability = collections.defaultdict(dict)
    rows = cur.execute(query,
                       {'tenantId': tenantId,
                        'startDatetime': startDatetime.strftime(sqliteDtFmt),
                        'endDatetime': endDatetime.strftime(sqliteDtFmt),
                        },
                       )
    for resId, *days, start, end in rows:

        start = dt.datetime.strptime(start, sqliteDtFmt)
        end = dt.datetime.strptime(end, sqliteDtFmt)

        for i,day in enumerate(days):
            days[i] = json.loads(day)

        for day in days:
            for i,av in enumerate(day):
                day[i] = {k:dt.time.fromisoformat(v) for k,v in av.items()}

        availability[resId][(start, end)] = days

    # downtimes
    with open(os.path.join(queryLoc, 'downtime.sql')) as infile:
        query = infile.read().strip()

    query = string.Template(query).substitute({'resourceIds': resourceIdsArray})
    res = cur.execute(query,
                      {'tenantId': tenantId,
                       'startDatetime': startDatetime.strftime(sqliteDtFmt),
                       'endDatetime': endDatetime.strftime(sqliteDtFmt),
                       },
                      )

    downtimes = collections.defaultdict(list)
    for resId, start, end in res:
        downtimes[resId].append((start, end))

    # organization holidays
    with open(os.path.join(queryLoc, 'holidays.sql')) as infile:
        query = infile.read().strip()

    query = string.Template(query).substitute({'resourceIds': resourceIdsArray})
    holidays = collections.defaultdict(list)
    for resId, start, end in cur.execute(query,
                                         {'tenantId': tenantId,
                                          'startDatetime': startDatetime.strftime(sqliteDtFmt),
                                          'endDatetime': endDatetime.strftime(sqliteDtFmt),
                                          },
                                         ):
        holidays[resId].append((start, end))

    # scheduled events

    with open(os.path.join(queryLoc, 'scheduled.sql')) as infile:
        query = infile.read().strip()

    query = string.Template(query).substitute({'resourceIds': resourceIdsArray})

    scheduled = collections.defaultdict(list)
    for resId, start, end in cur.execute(query,
                                         {'tenantId': tenantId},
                                         ):
        scheduled[resId].append((start, end))

    return availability, scheduled, downtimes, holidays


def getScheduleTemplate(dbFilepath, scheduleTemplateId, startDatetime, endDatetime):
    '''
    '''

    conn = sqlite3.connect(dbFilepath)
    cur = conn.cursor()

    queryLoc = os.path.join("DataFiles", "queries")
    with open(os.path.join(queryLoc, 'scheduleTemplate.sql')) as infile:
        query = infile.read().strip()

    answer = [[]]
    rows = cur.execute(query, {'scheduleTemplateId': scheduleTemplateId})
    for resId, resTypeId, taskId, taskSeq, delay, duration in rows:
        if taskSeq >= len(answer):
            answer.append([])

        answer[taskSeq].append((resId, resTypeId, taskId, delay, duration))
    
    return [a for a in answer if a]


def getResourcesByType(dbFilepath, scheduleTemplateId=None):
    '''
    '''

    conn = sqlite3.connect(dbFilepath)
    cur = conn.cursor()

    queryLoc = os.path.join("DataFiles", "queries")
    if not scheduleTemplateId:
        queryFile = 'resourceTypes.sql'
    else:
        queryFile = 'resourceTypesByScheduleTemplate.sql'

    with open(os.path.join(queryLoc, queryFile)) as infile:
        query = infile.read().strip()

    if scheduleTemplateId is not None:
        query = string.Template(query).substitute({'scheduleTemplateId': scheduleTemplateId})

    answer = collections.defaultdict(list)
    rows = cur.execute(query, {'scheduleTemplateId': scheduleTemplateId})
    for typeId, resId in rows:
        answer[typeId].append(resId)

    answer = {k:list(set(v)) for k,v in answer.items()}
    return answer
