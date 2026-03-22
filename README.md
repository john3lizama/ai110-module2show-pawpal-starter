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
