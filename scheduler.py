import datetime as dt
import itertools
import operator
import os
from ortools.sat.python import cp_model

import data

from ortools.sat.python import cp_model
from datetime import datetime

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, jobs, T_START):
        """
        initializing variables for the jobs and start time.
        """
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._jobs = jobs
        self._T_START = T_START
        self._solution_count = 0
        self.solutions = []

    def OnSolutionCallback(self):
        """
        using cp_sat CpSolverSolutionCallback function to search for all possible functions.
        """
        self._solution_count += 1
        solution = []
        
        # Loop through the scheduled jobs and collect solution details.
        for step in sorted(self._jobs.keys()):
            stepJob = []
            for i in sorted(self._jobs[step].keys()):
                job = self._jobs[step][i]
                startTime = self.Value(job["start-time"])
                endTime = self.Value(job["end-time"])
                assignedMachine = None
                for (machineNum, assigned) in job["machine-options"]:
                    if self.Value(assigned) == 1:
                        assignedMachine = machineNum
                        break

                # Convert the time stamps to datetime objects
                startDate = datetime.fromtimestamp(self._T_START + startTime)
                endDate = datetime.fromtimestamp(self._T_START + endTime)
                duration = job["duration"] // 3600
                # Store each job's details in the dictionary
                currSolution = [ assignedMachine,startDate,endDate,duration ]
                stepJob.append(currSolution)

            solution.append(stepJob)
                
        self.solutions.append(solution)

    def SolutionCount(self):
        """
        Returns the total number of solutions found.
        """
        return self._solution_count

    def get_solutions(self):
        """
        Return the dictionary containing all the solutions.
        """
        return self.solutions

def getUnavailability(start, horizon, availabilities):
    """
    start, horizon, and availabilities are the same parameters given to main()
    """

    START, HORIZON = start, horizon
    T_START = int(START.timestamp())
    start = 0
    horizon = int(horizon.timestamp() - T_START)
    daySeconds = (dt.datetime.fromtimestamp(0) + dt.timedelta(days=1)).timestamp()

    answer = {}
    for resId, d in availabilities.items():
        answer[resId] = []
        for (ruleStart, ruleEnd), days in d.items():
            currDay = ruleStart
            while currDay <= ruleEnd:
                weekday = currDay.weekday()
                specs = days[weekday]

                if sum(1 for spec in specs if spec)==0:  # not working on this day
                    startTime = dt.datetime(currDay.year, currDay.month, currDay.day, 0,0,0).timestamp() - T_START
                    endTime = dt.datetime(currDay.year, currDay.month, currDay.day, 23, 59, 59).timestamp() - T_START
                    answer[resId].append((startTime, endTime))
                    currDay += dt.timedelta(days=1)
                    continue

                for i,spec in enumerate(specs):
                    if not spec:
                        continue

                    fromTime = spec['from']
                    toTime = spec['to']

                    if i==0:  # add midnight to startTime
                        startTime = dt.datetime(currDay.year, currDay.month, currDay.day, 0,0,0).timestamp() - T_START
                        endTime = dt.datetime(currDay.year, currDay.month, currDay.day, fromTime.hour, fromTime.minute, fromTime.second).timestamp() - T_START

                        answer[resId].append((startTime, endTime))
                        continue
                    
                    last = specs[i-1]['to']
                    startTime = dt.datetime(currDay.year, currDay.month, currDay.day, last.hour, last.minute, last.second).timestamp() - T_START

                    currFrom = spec['from']
                    endTime =  dt.datetime(currDay.year, currDay.month, currDay.day, currFrom.hour, currFrom.minute, currFrom.second).timestamp() - T_START

                    answer[resId].append((startTime, endTime))

                last = specs[-1].get('to', None)
                if last is not None:
                    startTime = dt.datetime(currDay.year, currDay.month, currDay.day, last.hour, last.minute, last.second).timestamp() - T_START
                    endTime =  dt.datetime(currDay.year, currDay.month, currDay.day, 23, 59, 59).timestamp() - T_START
                    answer[resId].append((startTime, endTime))

                currDay += dt.timedelta(days=1)

    answer = {k:[(int(a), int(b)) for a,b in v] for k,v in answer.items()}

    backfills = fillUnvailabilities(START, HORIZON, answer)
    for k,L in backfills.items():
        answer.setdefault(k, []).extend(L)

    return answer


def fillUnvailabilities(start, horizon, unavailabilities):
    """
    start, horizon, and availabilities are the same parameters given to main()
    """

    unavailabilities = {k: sorted(v, key=operator.itemgetter(0)) for k,v in unavailabilities.items()}

    START, HORIZON = start, horizon
    T_START = START.timestamp()
    start = 0
    horizon = horizon.timestamp() - T_START

    answer = {}
    for resId, L in unavailabilities.items():
        if not L:
            answer[resId] = [(T_START, horizon)]
            continue

        answer[resId] = []
        for i, (intStart, intEnd) in enumerate(L):
            if not i:  # we need an interval from start
                answer[resId].append((start, intStart))
                continue

                answer[resId].append((L[i-1][1], intStart))

        answer[resId].append((L[-1][1], horizon))

    answer = {k:[(int(a), int(b)) for a,b in L] for k,L in answer.items()}
    return answer

def mergeUnavailabilities(unavailabilities, scheduled, holidays, downtimes, start, horizon):
    """
    unavailabilities: output of getUnavailability
    scheduled, holidays, downtimes: same as the input to main()
    """

    START, HORIZON = start, horizon
    T_START = int(start.timestamp())
    start = 0
    horizon = int(horizon.timestamp())

    scheduled = {k:[(int(a.timestamp()-T_START), int(b.timestamp()-T_START)) for a,b in L] for k,L in scheduled.items()}
    holidays = {k:[(dt.datetime.strptime(a, "%Y-%m-%d %H:%M:%S.%f"), dt.datetime.strptime(b, "%Y-%m-%d %H:%M:%S.%f")) for a,b in L] for k,L in holidays.items()}
    holidays = {k:[(int(a.timestamp()-T_START), int(b.timestamp()-T_START)) for a,b in L] for k,L in holidays.items()}

    downtimes = {k:[(dt.datetime.strptime(a, "%Y-%m-%d %H:%M:%S.%f"), dt.datetime.strptime(b, "%Y-%m-%d %H:%M:%S.%f")) for a,b in L] for k,L in downtimes.items()}
    downtimes = {k:[(int(a.timestamp()-T_START), int(b.timestamp()-T_START)) for a,b in L] for k,L in downtimes.items()}

    combined = {}
    for resId, L in itertools.chain.from_iterable(d.items() for d in (unavailabilities, scheduled, holidays, downtimes)):
        combined.setdefault(resId, []).extend(L)

    for resId, L in combined.items():
        L.sort()

    answer = {}
    for resId, L in combined.items():
        answer[resId] = [L[0]]
        for s,e in L[1:]:
            last = None
            while answer[resId] and s <= answer[resId][-1][1]-60:  # the new start is within 60sec of the last end
                last = answer[resId].pop(-1)

            if last is None:
                answer[resId].append((s,e))
            else:
                 answer[resId].append((min(s, last[0]), max(e, last[1])))

    return answer


def main(reqJobs, scheduled, downtimes, availabilities, holidays, start, horizon, resourcesByType):
    """
	scheduled, downtimes, availabilities, holidays: come from data.getAvailabilities
    reqJobs is the gantt chart for the requested schedule template
    start and horizon are the start/end datetimes within which we want to compute schedules for the given gantt chart
    """

    T_START = int(start.timestamp())
    START = start
    HORIZON = int(horizon.timestamp() - T_START)

    model = cp_model.CpModel()
    machineIntervals = {}
    unavailableIntervals = {}
    machineTypes = resourcesByType
    numMachines = sum(len(machines) for machines in machineTypes.values())
    for i in machineTypes.values():
        for m in i:
            machineIntervals[m] = [] # empty object (for now) denoting each machine available from the DB
            unavailableIntervals[m] = []

    # populate machineIntervals with the inverse of availabilities
    unavailabilities = getUnavailability(START, horizon, availabilities)
    unavailabilities = mergeUnavailabilities(unavailabilities, scheduled, holidays, downtimes, START, horizon)

    for resId, unavails in unavailabilities.items():
        unavailableIntervals[resId] = []
        for start,end in unavails:
            duration = end - start
            start = model.NewIntVar(start, start, f"unavailable_start_{resId}_{start}")
            end = model.NewIntVar(end, end, f"unavailable_end_{resId}_{end}")

            interval = model.NewIntervalVar(start, duration, end, f"unavailable_{resId}_{start}_{end}")
            unavailableIntervals[resId].append(interval)

    jobs = {}
    jobEndTimes = []
    
    daySeconds = int(dt.timedelta(days=1).total_seconds())
    horizonDays = HORIZON // daySeconds + 1
    horizonHours = HORIZON // 3600
    # step_targetStartDays = []
    last = 0
    for step, tasks in enumerate(reqJobs):
        if step > 0:
            _, _, _, delay_str, _ = reqJobs[step][0]
            delatStrip = dt.datetime.strptime(delay_str, "%Y-%m-%d %H:%M:%S.%f")
            delayDays = delatStrip.day - 1

            prevEndDays = [task["end_day"] for task in jobs[step - 1].values()]
            prevMaxEndDay = model.NewIntVar(0, horizonDays, f"prevMaxEndDay_step_{step}")
            model.AddMaxEquality(prevMaxEndDay, prevEndDays)

            targetStartDay = model.NewIntVar(0, horizonDays, f"targetStartDay_step_{step}")
            model.Add(targetStartDay == prevMaxEndDay + delayDays)

        else:
            targetStartDay = model.NewIntVar(0, horizonDays, f"targetStartDay_{step}")
            model.Add(targetStartDay == 0)

        for i, (resId, resTypeId, taskId, delay, duration) in enumerate(tasks):

            strip = dt.datetime.strptime(duration, "%Y-%m-%d %H:%M:%S.%f")
            duration = int(strip.hour * 3600 + strip.minute * 60 + strip.second)
            durationHours = duration // 3600

            startTime = model.NewIntVar(last, HORIZON - duration, f"step_{step}_job_{i}_start")
            endTime = model.NewIntVar(0, HORIZON, f"step_{step}_job_{i}_end")
            model.Add(endTime == startTime + duration)
            jobEndTimes.append(endTime)  # used later to display endtimes

 
            if resTypeId is None:
                machines = [resId]
            else:
                machines = resourcesByType[resTypeId]
    
            # gets the number of machines of a given type
            if not machines:
                raise ValueError(f"No machines available")  # for machine type: {machineType}")
    
   
            machineOptions = []  # new list used later to enforce one job on one machine rule.
    
            for machineNum in machines:
                assigned = model.NewBoolVar(f"step_{step}_job_{i}_OnMachine_{machineNum}")
                # Using optional interval variable instead of intvar for the machines so that
                # jobs can be scheduled in parallel if machine is available
                # OptIntVar in in the form (start, duration, end, bool, name)
                optInterval = model.NewOptionalIntervalVar(startTime,
                                                           duration,
                                                           endTime,
                                                           assigned,
                                                           f"step_{step}_job_{i}_machine_{machineNum}",
                                                           )
                machineOptions.append((machineNum, assigned))
                machineIntervals[machineNum].append((assigned, optInterval))

            # Create day index variables for the start and end of the task.
            start_day = model.NewIntVar(0, horizonDays, f"start_day_{step}_{i}")
            startHour = model.NewIntVar(0, horizonHours - durationHours, f"step_{step}_job_{i}_startHour")
            end_day = model.NewIntVar(0, horizonDays, f"end_day_{step}_{i}")
            model.Add(startTime >= start_day * daySeconds)
            model.Add(startTime < (start_day + 1) * daySeconds)
            model.Add(endTime >= end_day * daySeconds)
            model.Add(endTime < (end_day + 1) * daySeconds)
            model.Add(startTime == startHour * 3600)

            model.Add(start_day >= targetStartDay)
            if step>0:
                model.Add(prevMaxEndDay == start_day - delayDays)
        
            # Store the task info including the new day variables.
            jobs.setdefault(step, {})[i] = {"start-time": startTime,
                                            "duration": duration,
                                            "end-time": endTime,
                                            "machine-options": machineOptions,
                                            "machineType": machineTypes,
                                            "start_day": start_day,
                                            "end_day": end_day}
            
        
            # here we set a constraint that only one machine must be true for a job.
            model.Add(sum(assigned for (_, assigned) in machineOptions) == 1)
    
    taskIds = {}
    for step, tasks in enumerate(reqJobs):
        for i, (resId, resTypeId, taskId, delay, duration) in enumerate(tasks):
            if taskId not in taskIds:
                taskIds[taskId] = []
            taskIds[taskId].append((step, i))

    for taskId, tasks in taskIds.items():
        if len(tasks) > 1:  # Only need constraints when there are multiple tasks with the same ID
            for i in range(len(tasks) - 1):
                step1, id1 = tasks[i]
                step2, id2 = tasks[i + 1]
                
                # Get the start times and end times of both tasks
                start1 = jobs[step1][id1]["start-time"]
                start2 = jobs[step2][id2]["start-time"]
                
                # Constraint: Tasks must start at the same time
                model.Add(start1 == start2)

    # here we enforce the rule that only machines scheduled should have no overlap.
    for machineNum, intervals in machineIntervals.items():

        opt_intervals = [opt_interval for (_, opt_interval) in intervals]
        if machineNum in unavailableIntervals and unavailableIntervals[machineNum]:
            opt_intervals += unavailableIntervals[machineNum]

        if opt_intervals:
            model.AddNoOverlap(opt_intervals)

    # here we calculate the machineUsage and load for minimizing.
    machineUsage = {machineNum: model.NewIntVar(0, len(reqJobs), f"machineUsage{machineNum}")
                    for machineNum in machineIntervals.keys()
                    }

    for machineNum, intervals in machineIntervals.items():
        assignedJobs = [assigned for (assigned, _) in intervals]
        if assignedJobs:
            model.Add(machineUsage[machineNum] == sum(assignedJobs))

    #makespan = model.NewIntVar(0, HORIZON, f"makespan")
    # Minimize job end times
    #model.AddMaxEquality(makespan,jobEndTimes)
    #for i in jobEndTimes:
    #model.Minimize(sum(jobEndTimes))

    # Solve the model
    solver = cp_model.CpSolver()
    #solver.parameters.max_time_in_seconds = 60  # Limit execution to 60 sec
    # solver.parameters.log_search_progress = True  # Print solver progress
    #solver.parameters.log_search_progress = True
    solutionPrinter = VarArraySolutionPrinter(jobs, T_START)

    #solver.parameters.num_search_workers = 4  # Enable parallel processing
    status = solver.SearchForAllSolutions(model, solutionPrinter)

    if not (status == cp_model.OPTIMAL or status == cp_model.FEASIBLE):
        return None

    print(f"Number of solutions found: {solutionPrinter.SolutionCount()}")

    print("*"*15, "schedule", "*"*15)
    print(T_START)
    schedule = []
    for step,tasks in jobs.items():
        for i,job in tasks.items():
            assignedMachine = None
            for (machineNum, assigned) in job["machine-options"]:
                if solver.Value(assigned) == 1:
                    assignedMachine = machineNum
                    break

            schedule.append({"start-time": dt.datetime.fromtimestamp(T_START + solver.Value(jobs[step][i]["start-time"])),
                             "duration": solver.value((jobs[step][i]["duration"])//3600),
                             "machine": assignedMachine,
                             "end-time": dt.datetime.fromtimestamp(T_START + solver.Value(jobs[step][i]["end-time"])),
                             })

    return schedule, solutionPrinter.solutions
