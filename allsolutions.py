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
        self.solutions = {}

    def OnSolutionCallback(self):
        """
        using cp_sat CpSolverSolutionCallback function to search for all possible functions.
        """
        self._solution_count += 1
        VarArraySolutionPrinter = {}
        
        # Loop through the scheduled jobs and collect solution details.
        for step, tasks in self._jobs.items():
            VarArraySolutionPrinter[step] = {}
            for i, job in tasks.items():
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
                VarArraySolutionPrinter[step][i] = {
                    "machine": assignedMachine,
                    "start": startDate,
                    "end": endDate,
                    "duration": duration
                }
                
        # Save the solution using a key based on its count
        self.solutions[f"solution_{self._solution_count}"] = VarArraySolutionPrinter

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
