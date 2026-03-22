from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


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
                    h, m = map(int, start_time.split(":"))
                    new_total = h * 60 + m + task.duration_minutes
                    new_start = f"{new_total // 60:02d}:{new_total % 60:02d}"
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

    def _find_pet_for_task(self, task: Task) -> str:
        """Resolve which pet a scheduled task belongs to."""
        for pet in self.owner.pets:
            if task in pet.tasks:
                return pet.name
        return "Unknown"
