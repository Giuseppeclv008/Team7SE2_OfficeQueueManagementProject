TEMPLATE FOR RETROSPECTIVE (Team 07)
=====================================

The retrospective should include _at least_ the following
sections:

- [process measures](#process-measures)
- [quality measures](#quality-measures)
- [general assessment](#assessment)

## PROCESS MEASURES 

### Macro statistics

- Number of stories committed vs done: 3 committed / 1 done (#1)
- Total points committed vs done: 8 committed / 3 done
- Nr of hours planned vs spent (as a team): 43h 30m planned / 43h 14m spent

**Remember**  a story is done ONLY if it fits the Definition of Done:
 
- Unit Tests passing
- Code review completed
- Code present on Git
- End-to-End tests performed

> Please refine your DoD 

### Detailed statistics

| Story  | # Tasks | Points | Hours est. | Hours actual |
|--------|---------|--------|------------|--------------|
| _#0_   |   12      |    -   |       20h     |       31 h 37m       |
| _#1_      |    8     |    3    |     11h 30m      |     10h 45m         |
| _#2_      | 6   |    3    |     9h 30m     |   52m            |
| _#3_   |   4      |    2   |       2h 30m      |       0       |
   

> place technical tasks corresponding to story `#0` and leave out story points (not applicable in this case)

- Hours per task average, standard deviation (estimate and actual)

|            | Mean | StDev |
|------------|------|-------|
| Estimation | 1h 27m (1.45h) | 0.34h |
| Actual     | 1h 26m (1.44h) | 1.11h |

- Total estimation error ratio: sum of total hours spent / sum of total hours effort - 1

    $$\frac{\sum_i spent_{task_i}}{\sum_i estimation_{task_i}} - 1$$

    → 43.23h / 43.5h − 1 = **−0.006 (−0.6%)**. Overall totals match, but only because the overrun on #0 (+58%) offset the work not done on #2 and #3.
    
- Absolute relative task estimation error: sum( abs( spent-task-i / estimation-task-i - 1))/n

    $$\frac{1}{n}\sum_i^n \left| \frac{spent_{task_i}}{estimation_task_i}-1 \right| $$

    → **0.56** (approximated with each story's spent/estimate ratio applied to its tasks; 0.37 if only the stories that were worked on, #0 and #1, are counted)

  
## QUALITY MEASURES 

- Unit Testing:
  - Total hours estimated: 3h
  - Total hours spent:  2h 10m
  - Nr of automated unit test cases: 131 (all passing; DAO, DTO, database, ticket_queue)
  - Coverage: 88% statements on `backend/app` with unit tests only (`main.py` and `routers/tickets.py` are covered by the integration tests); 98% with unit + integration tests
- E2E testing:
  - Total hours estimated: 2h
  - Total hours spent: 1h 40m
  - Nr of test cases: 10 API integration tests (`tests/api/test_new_ticket.py`: HTTP → router → QueueManager → DAO → SQLite), all passing; no automated browser E2E tests
- Code review 
  - Total hours estimated: 30m
  - Total hours spent: 40m
  - Done through GitHub PRs #1–#9; review found DAO/DTO bugs, which were tracked as xfail tests and fixed (c491192)


## ASSESSMENT

- What caused your errors in estimation (if any)?
  - Story #0 (technical setup) overran by 58% (31h 37m vs 20h): CI setup and fixes, Alembic migrations, merge conflicts between parallel branches (revert of review fixes in PR #6, conflict artifact in `TicketDAO.find_all`) and queue ↔ DAO type conversion bugs.
  - The overrun on #0 used up the time planned for #2 (52m of 9h 30m) and #3 (not started).
  - Story #1 was estimated accurately (10h 45m vs 11h 30m, −7%).

- What lessons did you learn (both positive and negative) in this sprint?
  - Positive: writing tests early (xfail for known bugs) made review findings visible and verifiable; CI on every PR caught breakages before merge.
  - Negative: technical setup was badly underestimated, and long-lived feature branches caused conflicts and rework.

- Which improvement goals set in the previous retrospective were you able to achieve? 
  - N/A: this is the first retrospective.
  
- Which ones you were not able to achieve? Why?
  - N/A: this is the first retrospective.
- Improvement goals for the next sprint and how to achieve them (technical tasks, team coordination, etc.)

> Propose one or two

  1. Use short-lived branches merged to `main` at least daily, to reduce conflicts and rework.
  2. Estimate technical tasks with a buffer, and log hours per task (including testing and review), so per-task statistics can be measured exactly.

- One thing you are proud of as a Team!!
  - The complete *Get Ticket* flow works (Totem UI → API → queue → DB), backed by CI and 141 passing tests.
