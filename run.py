import datetime as dt
import os

import data
import scheduler
import time

if __name__ == "__main__":
    starttime = time.perf_counter() 
    print('starting')

    dbFilepath = os.path.join('DataFiles', 'data.db')
    tenantId = 'df0d79e571c147f192044f5ca8d5a342'  # noqa N816
    resourceIds = ['60350ab4731b493da56f305a7d08d268', 'd8311484f72e4d949cae68827992a62d']  # noqa N816
    scheduleTemplateId = '4f8be22d21f24766b5b3882777650357'
    startDatetime = dt.datetime(2024, 12, 27)
    endDatetime = dt.datetime(2025, 1, 31, 23,59,59)
    resourcesByType = data.getResourcesByType(dbFilepath)

    reqJobs = data.getScheduleTemplate(dbFilepath, scheduleTemplateId, startDatetime, endDatetime)
    print("*"*15, "reqJobs", "*"*15)  ##
    for step,jobs in enumerate(reqJobs):  ##
        print(f"{step} | {len(jobs)}", jobs)  ##

    availabilities = data.getAvailabilities(dbFilepath, tenantId, resourceIds, startDatetime, endDatetime)
    availability, scheduled, downtimes, holidays = availabilities

    schedule = scheduler.main(reqJobs, scheduled, downtimes, availability, holidays, startDatetime, endDatetime, resourcesByType)
    #print(makespan)
    if schedule is None:
        print("No solution found")
    else:
        for schedule in schedule:
            print(schedule)


    print('done')
    endtime = time.perf_counter()
    elapsedtime = endtime - starttime
    print(f"Total execution time: {elapsedtime = } seconds")
