from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from datetime import date, datetime, timedelta


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    frequency: str = "daily"        # "daily", "weekly", "as-needed"
    status: str = "pending"         # "pending", "complete", "cancelled"
    scheduled_time: Optional[str] = None  # "HH:MM" format
    due_date: Optional[str] = None        # "YYYY-MM-DD" format

    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.status = "complete"

    def reschedule(self, new_time: str) -> None:
        """Update the scheduled time and reset status to pending."""
        self.scheduled_time = new_time
        self.status = "pending"

    def cancel(self) -> None:
        """Mark this task as cancelled."""
        self.status = "cancelled"

    def is_high_priority(self) -> bool:
        """Return True if this task has HIGH priority."""
        return self.priority == Priority.HIGH


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> None:
        """Remove all tasks matching the given title from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.title != task_title]

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks with a pending status."""
        return [t for t in self.tasks if t.status == "pending"]


class Owner:
    def __init__(self, name: str, email: str, availability: list[tuple[str, int]]):
        self.name = name
        self.email = email
        # availability: list of (start_time "HH:MM", window_minutes)
        # e.g. [("08:00", 60), ("12:00", 30), ("18:00", 90)]
        self.availability = availability
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove all pets matching the given name from this owner's list."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_schedule(self) -> list[Task]:
        """Flatten all pending tasks across every pet into one list."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_pending_tasks())
        return all_tasks


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.scheduled_tasks: list[Task] = []

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort HIGH → MEDIUM → LOW, then by shortest duration first within each tier."""
        return sorted(tasks, key=lambda t: (-t.priority.value, t.duration_minutes))

    def generate_schedule(self) -> list[Task]:
        """
        Assign tasks to the owner's availability windows.
        Tasks are prioritized first, then slotted into the earliest window they fit.
        """
        pending = self.owner.get_schedule()
        ordered = self.prioritize_tasks(pending)

        # Work on a copy so the original availability list is never mutated
        windows = [(start, mins) for start, mins in self.owner.availability]
        self.scheduled_tasks = []

        for task in ordered:
            for i, (start_time, remaining_minutes) in enumerate(windows):
                if task.duration_minutes <= remaining_minutes:
                    task.scheduled_time = start_time

                    # Advance the window's start time and shrink its remaining capacity
                    new_start = (
                        datetime.strptime(start_time, "%H:%M")
                        + timedelta(minutes=task.duration_minutes)
                    ).strftime("%H:%M")
                    windows[i] = (new_start, remaining_minutes - task.duration_minutes)

                    self.scheduled_tasks.append(task)
                    break

        return self.scheduled_tasks

    def explain_plan(self) -> str:
        """Return a human-readable summary of the generated schedule."""
        if not self.scheduled_tasks:
            return "No schedule generated yet. Call generate_schedule() first."

        lines = [f"Daily Care Plan for {self.owner.name}:\n"]
        for task in self.scheduled_tasks:
            pet_name = self._find_pet_for_task(task)
            lines.append(
                f"  {task.scheduled_time}  [{task.priority.name:<6}]  "
                f"{task.title} ({task.duration_minutes} min)  —  {pet_name}"
            )
        return "\n".join(lines)

    def cancel_task(self, task_title: str) -> None:
        """Cancel a task by title across all pets and remove it from the schedule."""
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.title == task_title:
                    task.cancel()
                    self.scheduled_tasks = [
                        t for t in self.scheduled_tasks if t.title != task_title
                    ]
                    return

    def complete_task(self, task_title: str) -> Optional[Task]:
        """
        Mark a task complete. If its frequency is 'daily' or 'weekly', automatically
        create and register the next occurrence on the same pet.
        Returns the new Task if one was created, otherwise None.
        """
        _RECURRENCE_DAYS = {"daily": 1, "weekly": 7}

        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.title == task_title and task.status == "pending":
                    task.mark_complete()

                    delta_days = _RECURRENCE_DAYS.get(task.frequency)
                    if delta_days is None:
                        return None

                    next_date = date.today() + timedelta(days=delta_days)
                    next_task = Task(
                        title=task.title,
                        duration_minutes=task.duration_minutes,
                        priority=task.priority,
                        frequency=task.frequency,
                        scheduled_time=task.scheduled_time,
                        due_date=next_date.isoformat(),
                    )
                    pet.add_task(next_task)
                    return next_task

        return None

    def detect_conflicts(self) -> list[str]:
        """
        Scan all pending tasks across every pet for scheduling conflicts.
        A conflict is any time slot where two or more tasks share the same scheduled_time.
        Returns a list of warning strings (one per conflicting slot) — never raises.
        """
        from collections import defaultdict

        time_map: dict[str, list[tuple[str, Task]]] = defaultdict(list)
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.status == "pending" and task.scheduled_time:
                    time_map[task.scheduled_time].append((pet.name, task))

        warnings = []
        for slot, entries in sorted(time_map.items()):
            if len(entries) > 1:
                details = ", ".join(
                    f"'{t.title}' ({pet})" for pet, t in entries
                )
                warnings.append(f"WARNING: Conflict at {slot} — {details}")

        return warnings

    def sort_tasks_by_time(self, tasks: list[Task]) -> list[Task]:
        """
        Return a new list of tasks sorted chronologically by scheduled_time.

        Uses a lambda key that parses each "HH:MM" string into a (hours, minutes)
        integer tuple so that string comparison never produces wrong order
        (e.g. "9:00" < "10:00" fails lexicographically but works correctly as
        (9, 0) < (10, 0)). Tasks with no scheduled_time are given a sentinel
        value of (24, 0) so they always sort to the end of the list.

        Args:
            tasks: Any list of Task objects to sort.

        Returns:
            A new sorted list; the original list is not modified.
        """
        return sorted(
            tasks,
            key=lambda t: tuple(map(int, t.scheduled_time.split(":"))) if t.scheduled_time else (24, 0)
        )

    def filter_tasks(self, tasks: list[Task], status: str = None, pet_name: str = None) -> list[Task]:
        """
        Return a subset of tasks that match all supplied filter criteria.

        Filters are applied in sequence and are cumulative — providing both
        status and pet_name returns only tasks that satisfy both conditions.
        Omitting a parameter (or passing None) skips that filter entirely,
        so calling filter_tasks(tasks) with no extra args returns the full list.

        Args:
            tasks:    The list of Task objects to filter.
            status:   If provided, keep only tasks whose status equals this
                      string (e.g. "pending", "complete", "cancelled").
            pet_name: If provided, keep only tasks belonging to the pet with
                      this exact name. Uses _find_pet_for_task internally to
                      resolve ownership.

        Returns:
            A new list containing only the tasks that passed every active filter.
        """
        result = tasks
        if status is not None:
            result = [t for t in result if t.status == status]
        if pet_name is not None:
            result = [t for t in result if self._find_pet_for_task(t) == pet_name]
        return result

    def _find_pet_for_task(self, task: Task) -> str:
        """Resolve which pet a scheduled task belongs to."""
        for pet in self.owner.pets:
            if task in pet.tasks:
                return pet.name
        return "Unknown"
