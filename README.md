# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

Beyond the core `generate_schedule()` logic, the `Scheduler` class includes four additional features:

**Sorting by time** — `sort_tasks_by_time(tasks)` orders any task list chronologically. It parses each `"HH:MM"` string into an integer tuple `(hours, minutes)` so the comparison is always numerically correct. Tasks with no scheduled time are placed at the end.

**Filtering** — `filter_tasks(tasks, status, pet_name)` narrows a task list by completion status (e.g. `"pending"`, `"complete"`), by pet name, or both at once. Either argument can be omitted to skip that filter.

**Auto-recurrence** — `complete_task(task_title)` marks a task complete and, if its frequency is `"daily"` or `"weekly"`, automatically creates the next occurrence with a `due_date` of today + 1 day or today + 7 days respectively. The new task is added directly to the same pet's task list.

**Conflict detection** — `detect_conflicts()` scans every pending task across all pets and flags any time slot where two or more tasks share the same `scheduled_time`. It returns a list of plain warning strings rather than raising an exception, so the rest of the program keeps running.

## Testing PawPal+

### Running the tests

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

The suite contains **63 tests** organized across five test classes:

| Class | Tests | What it covers |
|---|---|---|
| `TestTask` | 11 | State transitions (`pending` → `complete` → `cancelled`), idempotent operations, zero/large durations |
| `TestPet` | 9 | Adding/removing tasks, `get_pending_tasks()` filtering, independent task lists across pets |
| `TestOwner` | 8 | Adding/removing pets, schedule aggregation across multiple pets |
| `TestScheduler` | 12 | Priority sorting (HIGH → MEDIUM → LOW, shortest-first tie-break), schedule generation, window overflow, cancellation |
| `TestSortingCorrectness` | 6 | Chronological ordering, numeric vs. lexicographic time comparison (`"09:00"` < `"10:00"`), `None` scheduled times, list immutability |
| `TestRecurrenceLogic` | 8 | Daily (+1 day) and weekly (+7 day) due dates, property inheritance on new task, `as-needed` produces no recurrence, no duplicate tasks on repeated completion |
| `TestConflictDetection` | 9 | Same-pet and cross-pet conflicts, three-way collisions in one warning, completed/unscheduled tasks excluded, empty owner |

### Confidence Level

★★★★☆ (4 / 5)

The core scheduling loop, recurrence logic, conflict detection, and all documented edge cases are fully tested and passing. One star is held back because tasks can collide silently when two pets share a task title (the scheduler matches the first one found), and `generate_schedule()` silently skips tasks that exceed every availability window rather than surfacing a warning. Both are observable behaviors worth adding assertions for before shipping to production.
