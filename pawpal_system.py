from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    status: str = "pending"  # "pending", "complete", "cancelled"
    scheduled_time: Optional[str] = None

    def mark_complete(self) -> None:
        pass

    def reschedule(self, new_time: str) -> None:
        pass

    def cancel(self) -> None:
        pass

    def is_high_priority(self) -> bool:
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_title: str) -> None:
        pass

    def get_pending_tasks(self) -> list[Task]:
        pass


class Owner:
    def __init__(self, name: str, email: str, availability: list[str]):
        self.name = name
        self.email = email
        self.availability = availability  # e.g. ["08:00", "12:00", "18:00"]
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet_name: str) -> None:
        pass

    def get_schedule(self) -> list[Task]:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.scheduled_tasks: list[Task] = []

    def generate_schedule(self) -> list[Task]:
        pass

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def explain_plan(self) -> str:
        pass

    def cancel_task(self, task_title: str) -> None:
        pass
