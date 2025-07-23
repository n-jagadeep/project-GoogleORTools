import datetime as dt
import itertools
import os

from flask import Flask, jsonify, request

import data
import scheduler


app = Flask(__name__)


@app.route('/scheduler', methods=['GET'])
def schedulerEndpoint():
    """
    Receive job requests and a horizon. Reutrn a makespan by calling scheduler.py
    The endpoint must receive a list of requested job specs as well as a horizon
    """

    dbFilepath = os.path.join("DataFiles", 'data.db')

    scheduleTemplateId, start, horizon, tenantId = request.get_json()
    start = dt.datetime.fromisoformat(start)
    horizon = dt.datetime.fromisoformat(horizon)

    resourcesByType = data.getResourcesByType(dbFilepath, scheduleTemplateId)
    resourceIds = list(itertools.chain.from_iterable(resourcesByType.values()))

    reqJobs = data.getScheduleTemplate(dbFilepath, scheduleTemplateId, start, horizon)
    availabilities = data.getAvailabilities(dbFilepath, tenantId, resourceIds, start, horizon)
    availability, scheduled, downtimes, holidays = availabilities

    answer, a2 = scheduler.main(reqJobs, scheduled, downtimes, availability, holidays, start, horizon, resourcesByType)
    for schedule in answer:
        schedule['start-time'] = schedule['start-time'].isoformat().replace("T", " ")
        schedule['end-time'] = schedule['end-time'].isoformat().replace("T", " ")
        print(f"{schedule['machine']}: {schedule['duration']} |  {schedule['start-time']} - {schedule['end-time']}")

    print(f"{len(answer) = }")  ##
    print(f"{len(a2) = }")  ##
    for s in a2:
        print(s)
        print("*"*50)
        


    return jsonify(answer)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
