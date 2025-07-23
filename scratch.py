import datetime as dt
import itertools
import os

from ortools.sat.python import cp_model
from tqdm import tqdm

import data


def main(reqJobs, scheduled, downtimes, availabilities, holidays, start, horizon, resourcesByType):
    """
	scheduled, downtimes, availabilities, holidays: come from data.getAvailabilities
    reqJobs is the gantt chart for the requested schedule template
    start and horizon are the start/end datetimes within which we want to compute schedules for the given gantt chart
    """

    T_START = start.timestamp()
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
    # print("Machine Types:", machineTypes, numMachines, machineIntervals)  ##
    # print(f"{availabilities = }")

    # populate machineIntervals with downtimes, holidays, and already-scheduled times
    for resId, L in itertools.chain(scheduled.items(), downtimes.items(), holidays.items()):
        for start,end in L:
            start = dt.datetime.strptime(start, "%Y-%m-%d %H:%M:%S.%f")
            end = dt.datetime.strptime(end, "%Y-%m-%d %H:%M:%S.%f")
            start_ts = int(start.timestamp() - T_START)
            end_ts = int(end.timestamp() - T_START)
            duration = end_ts - start_ts

            if duration <= 0:
                continue

            # Create IntVars specific to the current redId
            start_var = model.NewIntVar(start_ts, start_ts, f"unavailable_start_{resId}")
            end_var = model.NewIntVar(end_ts, end_ts, f"unavailable_end_{resId}")
            duration_var = model.NewIntVar(duration, duration, f"unavailable_dur_{resId}")

            # Create an interval that blocks scheduling on this machine only
            unavailableInterval = model.NewIntervalVar(start_var, duration_var, end_var, f"unavailable_{resId}")

            # appending the interval to the corresponding machine
            if resId in machineIntervals:
                unavailableIntervals[resId].append(unavailableInterval)
        # else:
        #     machineIntervals[resId] = [unavailableInterval]


    # populate machineIntervals with the inverse of availabilities
    for resId, d in availabilities.items():
        last = 0
        for (start, end), L in d.items():
            start = dt.datetime(START.year, START.month, START.day, start.hour, start.minute)
            end = dt.datetime(START.year, START.month, START.day, end.hour, end.minute)
            if end.timestamp() - T_START < 0:
                continue
            if start.timestamp() - T_START > HORIZON:
                continue
            for weekday,avail in enumerate(L):
                offset = weekday - start.weekday()
                if offset < 0:
                    offset += 7
                curr = start + dt.timedelta(days=offset)
                while curr < end:
                    print(curr, end)  ##
                    ford = False
                    # print(f"{curr = }, {end = }")
                    for av in avail:
                        dayStart = av.get('from')
                        dayEnd = av.get('to')

                        # print('day:', dayStart, dayEnd)  ##

                        if dayStart is None or dayEnd is None:
                            continue

                        ford = True

                        dayStart = int(dt.datetime(curr.year, curr.month, curr.day, dayStart.hour, dayStart.minute).timestamp() - T_START)
                        dayEnd  = int(dt.datetime(curr.year, curr.month, curr.day, dayEnd.hour, dayEnd.minute).timestamp() - T_START)

                        if last < dayStart:
                            start_var = model.NewIntVar(last, last, f"unavailable_start_{resId}_{curr.date()}")
                            end_var = model.NewIntVar(dayStart, dayStart, f"unavailable_end_{resId}_{curr.date()}")
                            duration_var = model.NewIntVar(dayStart - last, dayStart - last, f"unavailable_dur_{resId}_{curr.date()}")

                            unavail_interval = model.NewIntervalVar(start_var, duration_var, end_var, f"unavailable_{resId}_{curr.date()}")
                            unavailableIntervals.setdefault(resId, []).append(unavail_interval)

                        curr = curr + dt.timedelta(days=7)
                        last = dayEnd 

                    if not ford:  # we never went through that loop
                        break

                curr = curr - dt.timedelta(days=7)
    print(f"{machineIntervals = }")
    jobs = {}
    jobEndTimes = []
    
    daySeconds = 86400
    horizonDays = HORIZON // daySeconds + 1
    step_target_start_days = []
    last = 0
    for step, tasks in enumerate(tqdm(reqJobs)):
        if step > 0:
            _, _, _, delay_str, _ = reqJobs[step][0]
            strip = dt.datetime.strptime(delay_str, "%Y-%m-%d %H:%M:%S.%f")
            step_delay = int((strip.day - 1) * 86400 + strip.hour * 3600 + strip.minute * 60 + strip.second)

            prev_end_times = [task["end-time"] for task in jobs[step - 1].values()]
            prev_end_days = [task["end_day"] for task in jobs[step - 1].values()]

            prev_max_end = model.NewIntVar(0, HORIZON, f"prev_max_end_step_{step}")
            prev_max_end_day = model.NewIntVar(0, horizonDays, f"prev_max_end_day_step_{step}")

            model.AddMaxEquality(prev_max_end, prev_end_times)
            model.AddMaxEquality(prev_max_end_day, prev_end_days)

            target_start_day = model.NewIntVar(0, horizonDays, f"target_start_day_step_{step}")
            model.Add(target_start_day == prev_max_end_day + (step_delay // daySeconds))
            step_target_start_days.append(target_start_day)

            # Back-propagate: ensure previous step ends early enough
            model.Add(prev_max_end_day <= target_start_day - (step_delay // daySeconds))
        else:
            step_delay = 0
            prev_max_end = None
            prev_max_end_day = None
            target_start_day = model.NewIntVar(0, horizonDays, f"target_start_day_step_{step}")
            model.Add(target_start_day == 0)
            step_target_start_days.append(target_start_day)

        for i, (resId, resTypeId, taskId, delay, duration) in enumerate(tasks):
            print(f"{last = }")  ##
            print(f"{HORIZON = }")  ##
            print(f"{duration = }")  ##
            print(f"{delay = }")  ##

            #duration = int(dt.datetime.strptime(duration, "%Y-%m-%d %H:%M:%S.%f").timestamp())
            strip = dt.datetime.strptime(duration, "%Y-%m-%d %H:%M:%S.%f")
            duration = int(strip.hour * 3600 + strip.minute * 60 + strip.second)

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
            # print(machineIntervals, machines) ##
    
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
                # print("machineIntervals keys:", machineIntervals.keys())  ##
                print(f"Added optional machine interval step_{step}_job_{i}_machine_{machineNum}")  ##

                machineOptions.append((machineNum, assigned))
                machineIntervals[machineNum].append((assigned, optInterval))

            # Create day index variables for the start and end of the task.
            start_day = model.NewIntVar(0, horizonDays, f"start_day_{step}_{i}")
            end_day = model.NewIntVar(0, horizonDays, f"end_day_{step}_{i}")
            model.Add(startTime >= start_day * daySeconds)
            model.Add(startTime < (start_day + 1) * daySeconds)
            model.Add(endTime >= end_day * daySeconds)
            model.Add(endTime < (end_day + 1) * daySeconds)
        
            # Store the task info including the new day variables.
            jobs.setdefault(step, {})[i] = {"start-time": startTime,
                                            "duration": duration,
                                            "end-time": endTime,
                                            "machine-options": machineOptions,
                                            "machineType": machineTypes,
                                            "start_day": start_day,
                                            "end_day": end_day}
            
            # Enforce step-wide target start day
            model.Add(start_day >= target_start_day)
        
            # For tasks in step > 0 that have a delay, enforce that this task must start
            # after the latest finish (plus delay) of the previous step and on a later day.
            # if step > 0 and delay_str > 0:
            #     model.Add(startTime >= prev_max_end + delay_str)
            #     model.Add(prev_max_end< startTime - delay_str)
            #     model.Add(start_day >= prev_max_end_day + (delay_str // daySeconds))


            # here we set a constraint that only one machine must be true for a job.
            model.Add(sum(assigned for (_, assigned) in machineOptions) == 1)
    
            # jobs.setdefault(step, {})[i] = {"start-time": startTime,
            #                                 "duration": duration,
            #                                 "end-time": endTime,
            #                                 "machine-options": machineOptions,  # list of (machineNum, assigned Boolean)
            #                                 "machineType": machineTypes,
            #                                 }
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

    print("*"*30)  ##
    # here we enforce the rule that only machines scheduled should have no overlap.
    for machineNum, intervals in machineIntervals.items():
        # print(f"{intervals = }")

        opt_intervals = [opt_interval for (_, opt_interval) in intervals]
        if machineNum in unavailableIntervals and unavailableIntervals[machineNum]:
            opt_intervals += unavailableIntervals[machineNum]

        if opt_intervals:
            model.AddNoOverlap(opt_intervals)
        # if not unavailableIntervals[machineNum]:  # Ensure it's not empty
        #     continue

        # model.AddNoOverlap(unavailableIntervals[machineNum])

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
    model.Minimize(sum(jobEndTimes))

    # Solve the model
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60  # Limit execution to 60 sec
    # solver.parameters.log_search_progress = True  # Print solver progress
    solver.parameters.num_search_workers = 4  # Enable parallel processing
    status = solver.Solve(model)

    if not (status == cp_model.OPTIMAL or status == cp_model.FEASIBLE):
        return None

    print("*"*15, "schedule", "*"*15)
    print(T_START)
    schedule = []
    for step,tasks in jobs.items():
        for i,job in tasks.items():
            assigned_machine = None
            for (machineNum, assigned) in job["machine-options"]:
                if solver.Value(assigned) == 1:
                    assigned_machine = machineNum
                    break

            schedule.append({"start-time": dt.datetime.fromtimestamp(T_START + solver.Value(jobs[step][i]["start-time"])),
                             "duration": solver.value((jobs[step][i]["duration"])//3600),
                             "machine": assigned_machine,
                             "end-time": dt.datetime.fromtimestamp(T_START + solver.Value(jobs[step][i]["end-time"])),
                             })

    return schedule
