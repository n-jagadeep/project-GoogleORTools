# Repository Overview

This project is a small prototype that schedules tasks with [Google OR-Tools](https://developers.google.com/optimization). The code fetches resource data from a SQLite database, builds a constraint model with OR-Tools, and optionally exposes an API via Flask.

```
.
├── DataFiles/            # SQLite DB and SQL queries
├── api.py                # Flask endpoint for scheduling
├── data.py               # Helpers to read availability & templates from DB
├── run.py                # Example command-line entry point
├── scheduler.py          # Core scheduling logic using OR-Tools CP-SAT
├── schema.py             # SQLAlchemy models and DB schema
└── testing/              # Scenario data to populate the DB for experiments
```

## Database Models

`schema.py` defines SQLAlchemy tables for resources, availabilities, schedules, etc. It includes a helper for creating the database:

```python
class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:  # noqa N805
        name_list = re.findall(r"[A-Z][a-z\d]*", cls.__name__)
        return "_".join(name_list).lower()
```

Create all tables by running `schema.py` directly:

```python
if __name__ == "__main__":
    engine = create_engine("sqlite:///DataFiles/data.db", echo=False)
    Base.metadata.create_all(engine)
```

## Loading Data

`data.py` wraps SQL queries stored under `DataFiles/queries/` to collect:

- resource availability windows
- downtimes and holidays
- schedule templates

Example function:

```python
def getAvailabilities(dbFilepath, tenantId, resourceIds, startDatetime, endDatetime):
    with open(os.path.join(queryLoc, "availability.sql")) as infile:
        query = infile.read().strip()
    query = string.Template(query).substitute({"resourceIds": resourceIdsArray})
    # query DB and parse results...
```

## Scheduling Logic

`scheduler.py` builds the OR-Tools CP-SAT model. It converts availability into intervals, merges scheduled tasks and downtimes, and then creates variables for each job and resource:

```python
def main(reqJobs, scheduled, downtimes, availabilities, holidays, start, horizon, resourcesByType):
    model = cp_model.CpModel()
    machineIntervals = {}
    unavailabilities = getUnavailability(START, horizon, availabilities)
    unavailabilities = mergeUnavailabilities(unavailabilities, scheduled, holidays, downtimes, START, horizon)
    for step, tasks in enumerate(reqJobs):
        ...
        startTime = model.NewIntVar(last, HORIZON - duration, f"step_{step}_job_{i}_start")
        ...
        model.Add(sum(assigned for (_, assigned) in machineOptions) == 1)
```

After building all constraints, the solver enumerates solutions:

```python
solver = cp_model.CpSolver()
status = solver.SearchForAllSolutions(model, solutionPrinter)
if not (status == cp_model.OPTIMAL or status == cp_model.FEASIBLE):
    return None
```

## Example Execution

`run.py` demonstrates how to invoke the scheduler:

```python
if __name__ == "__main__":
    dbFilepath = os.path.join("DataFiles", "data.db")
    tenantId = "..."
    resourceIds = [...]
    scheduleTemplateId = "..."
    startDatetime = dt.datetime(2024, 12, 27)
    endDatetime = dt.datetime(2025, 1, 31, 23, 59, 59)
    resourcesByType = data.getResourcesByType(dbFilepath)
    reqJobs = data.getScheduleTemplate(dbFilepath, scheduleTemplateId, startDatetime, endDatetime)
    availabilities = data.getAvailabilities(dbFilepath, tenantId, resourceIds, startDatetime, endDatetime)
    schedule = scheduler.main(reqJobs, scheduled, downtimes, availabilities, holidays, startDatetime, endDatetime, resourcesByType)
```

## Flask API

`api.py` exposes a `/scheduler` route that accepts JSON with a schedule template ID, start time, end time, and tenant ID. It calls the scheduler and returns the resulting schedule as JSON.

## Testing Data

`testing/scenario_1/data.py` populates the database with a sample tenant, resources, and schedule template to experiment with the solver. Running it fills `DataFiles/data.db` with the scenario's data.

## Next Steps to Explore

1. **Run the example** – Install dependencies from `requirements.txt` (`Flask`, `ortools`, `SQLAlchemy`). Populate the database using the testing scenario or your own data, then run `run.py` to generate a schedule.
2. **Review OR-Tools CP-SAT** – Understanding the solver will help customize constraints or optimize objectives.
3. **Experiment with the Flask API** – Start `api.py` and send JSON requests to `/scheduler` to integrate the scheduler into other applications.
4. **Inspect the SQL Queries** – The SQL files in `DataFiles/queries/` show how the SQLite data is retrieved. Adjusting these queries or the schema lets you experiment with different availability or scheduling data.
5. **Explore Scenario Generation** – The scripts in `testing/` demonstrate how to create synthetic data with SQLAlchemy, which can be extended to build larger or more complex scenarios.

Overall, this repository demonstrates how to use OR-Tools with a database-backed data model and exposes scheduling results via a simple API. With a basic understanding of Python and constraint programming, you can extend it for more sophisticated scheduling tasks.
