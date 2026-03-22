import pytest
from pawpal_system import Task, Pet, Owner, Scheduler, Priority


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def basic_task():
    return Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH)

@pytest.fixture
def basic_pet():
    return Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)

@pytest.fixture
def owner_with_availability():
    return Owner(
        name="Jordan",
        email="jordan@example.com",
        availability=[("08:00", 60), ("12:00", 30), ("18:00", 90)],
    )

@pytest.fixture
def loaded_owner(owner_with_availability, basic_pet):
    pet = basic_pet
    pet.add_task(Task("Morning walk", 30, Priority.HIGH))
    pet.add_task(Task("Feeding", 10, Priority.HIGH))
    pet.add_task(Task("Grooming", 20, Priority.MEDIUM))
    pet.add_task(Task("Playtime", 15, Priority.LOW))
    owner_with_availability.add_pet(pet)
    return owner_with_availability


# ---------------------------------------------------------------------------
# Task — state transitions
# ---------------------------------------------------------------------------

class TestTask:

    def test_initial_status_is_pending(self, basic_task):
        assert basic_task.status == "pending"

    def test_mark_complete_changes_status(self, basic_task):
        basic_task.mark_complete()
        assert basic_task.status == "complete"

    def test_cancel_changes_status(self, basic_task):
        basic_task.cancel()
        assert basic_task.status == "cancelled"

    def test_reschedule_updates_time(self, basic_task):
        basic_task.reschedule("14:00")
        assert basic_task.scheduled_time == "14:00"

    def test_reschedule_resets_cancelled_task_to_pending(self, basic_task):
        basic_task.cancel()
        basic_task.reschedule("09:00")
        assert basic_task.status == "pending"

    def test_is_high_priority_true(self, basic_task):
        assert basic_task.is_high_priority() is True

    def test_is_high_priority_false_for_low(self):
        task = Task("Bath", 20, Priority.LOW)
        assert task.is_high_priority() is False

    # Edge cases
    def test_mark_complete_twice_stays_complete(self, basic_task):
        basic_task.mark_complete()
        basic_task.mark_complete()
        assert basic_task.status == "complete"

    def test_cancel_already_complete_task(self, basic_task):
        basic_task.mark_complete()
        basic_task.cancel()
        assert basic_task.status == "cancelled"

    def test_zero_duration_task_is_valid(self):
        task = Task("Quick check", 0, Priority.LOW)
        assert task.duration_minutes == 0

    def test_very_long_task(self):
        task = Task("All-day care", 480, Priority.HIGH)
        assert task.duration_minutes == 480


# ---------------------------------------------------------------------------
# Pet — task management
# ---------------------------------------------------------------------------

class TestPet:

    def test_new_pet_has_no_tasks(self, basic_pet):
        assert len(basic_pet.tasks) == 0

    def test_add_task_increases_task_count(self, basic_pet, basic_task):
        basic_pet.add_task(basic_task)
        assert len(basic_pet.tasks) == 1

    def test_add_multiple_tasks_increases_count(self, basic_pet):
        basic_pet.add_task(Task("Walk", 30, Priority.HIGH))
        basic_pet.add_task(Task("Feed", 10, Priority.MEDIUM))
        basic_pet.add_task(Task("Groom", 20, Priority.LOW))
        assert len(basic_pet.tasks) == 3

    def test_remove_task_by_title(self, basic_pet, basic_task):
        basic_pet.add_task(basic_task)
        basic_pet.remove_task("Morning walk")
        assert len(basic_pet.tasks) == 0

    def test_remove_nonexistent_task_does_not_raise(self, basic_pet):
        basic_pet.remove_task("Ghost task")  # should not raise
        assert len(basic_pet.tasks) == 0

    def test_get_pending_tasks_excludes_complete(self, basic_pet):
        t1 = Task("Walk", 30, Priority.HIGH)
        t2 = Task("Feed", 10, Priority.MEDIUM)
        t2.mark_complete()
        basic_pet.add_task(t1)
        basic_pet.add_task(t2)
        pending = basic_pet.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].title == "Walk"

    def test_get_pending_tasks_excludes_cancelled(self, basic_pet):
        t1 = Task("Walk", 30, Priority.HIGH)
        t2 = Task("Feed", 10, Priority.MEDIUM)
        t2.cancel()
        basic_pet.add_task(t1)
        basic_pet.add_task(t2)
        assert len(basic_pet.get_pending_tasks()) == 1

    def test_get_pending_tasks_empty_when_all_complete(self, basic_pet):
        task = Task("Walk", 30, Priority.HIGH)
        task.mark_complete()
        basic_pet.add_task(task)
        assert basic_pet.get_pending_tasks() == []

    # Edge case: two pets should not share the same task list
    def test_two_pets_have_independent_task_lists(self):
        pet_a = Pet("Mochi", "dog", "Shiba", 3)
        pet_b = Pet("Luna", "cat", "Siamese", 2)
        pet_a.add_task(Task("Walk", 30, Priority.HIGH))
        assert len(pet_b.tasks) == 0


# ---------------------------------------------------------------------------
# Owner — pet management
# ---------------------------------------------------------------------------

class TestOwner:

    def test_new_owner_has_no_pets(self, owner_with_availability):
        assert len(owner_with_availability.pets) == 0

    def test_add_pet_increases_count(self, owner_with_availability, basic_pet):
        owner_with_availability.add_pet(basic_pet)
        assert len(owner_with_availability.pets) == 1

    def test_remove_pet_by_name(self, owner_with_availability, basic_pet):
        owner_with_availability.add_pet(basic_pet)
        owner_with_availability.remove_pet("Mochi")
        assert len(owner_with_availability.pets) == 0

    def test_remove_nonexistent_pet_does_not_raise(self, owner_with_availability):
        owner_with_availability.remove_pet("Ghost")  # should not raise

    def test_get_schedule_returns_all_pending_tasks(self, loaded_owner):
        tasks = loaded_owner.get_schedule()
        assert len(tasks) == 4

    def test_get_schedule_excludes_completed_tasks(self, loaded_owner):
        loaded_owner.pets[0].tasks[0].mark_complete()
        tasks = loaded_owner.get_schedule()
        assert len(tasks) == 3

    def test_get_schedule_with_no_pets_returns_empty(self, owner_with_availability):
        assert owner_with_availability.get_schedule() == []

    def test_get_schedule_aggregates_across_multiple_pets(self, owner_with_availability):
        pet_a = Pet("Mochi", "dog", "Shiba", 3)
        pet_b = Pet("Luna", "cat", "Siamese", 2)
        pet_a.add_task(Task("Walk", 30, Priority.HIGH))
        pet_b.add_task(Task("Feed", 10, Priority.MEDIUM))
        owner_with_availability.add_pet(pet_a)
        owner_with_availability.add_pet(pet_b)
        assert len(owner_with_availability.get_schedule()) == 2


# ---------------------------------------------------------------------------
# Scheduler — the brain
# ---------------------------------------------------------------------------

class TestScheduler:

    def test_prioritize_puts_high_before_low(self, loaded_owner):
        scheduler = Scheduler(loaded_owner)
        tasks = loaded_owner.get_schedule()
        ordered = scheduler.prioritize_tasks(tasks)
        assert ordered[0].priority == Priority.HIGH

    def test_prioritize_within_same_priority_shorter_first(self, owner_with_availability):
        pet = Pet("Mochi", "dog", "Shiba", 3)
        pet.add_task(Task("Long high", 60, Priority.HIGH))
        pet.add_task(Task("Short high", 10, Priority.HIGH))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)
        ordered = scheduler.prioritize_tasks(pet.get_pending_tasks())
        assert ordered[0].title == "Short high"

    def test_generate_schedule_assigns_time_slots(self, loaded_owner):
        scheduler = Scheduler(loaded_owner)
        scheduled = scheduler.generate_schedule()
        for task in scheduled:
            assert task.scheduled_time is not None

    def test_generate_schedule_skips_task_that_does_not_fit(self, owner_with_availability):
        pet = Pet("Mochi", "dog", "Shiba", 3)
        # 120-minute task won't fit in any window (60, 30, 90)
        pet.add_task(Task("Mega task", 120, Priority.HIGH))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)
        scheduled = scheduler.generate_schedule()
        assert len(scheduled) == 0

    def test_generate_schedule_does_not_overflow_window(self, owner_with_availability):
        pet = Pet("Mochi", "dog", "Shiba", 3)
        # Two 40-min tasks: first fits in 60-min window, second (also 40 min) needs its own window
        pet.add_task(Task("Task A", 40, Priority.HIGH))
        pet.add_task(Task("Task B", 40, Priority.HIGH))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)
        scheduled = scheduler.generate_schedule()
        # Task A takes 40 of 60 mins, leaving 20 — Task B (40 min) won't fit there,
        # but fits in the 18:00 window (90 min)
        assert len(scheduled) == 2
        assert scheduled[0].scheduled_time != scheduled[1].scheduled_time

    def test_cancel_task_removes_from_schedule(self, loaded_owner):
        scheduler = Scheduler(loaded_owner)
        scheduler.generate_schedule()
        scheduler.cancel_task("Morning walk")
        titles = [t.title for t in scheduler.scheduled_tasks]
        assert "Morning walk" not in titles

    def test_cancel_task_marks_task_as_cancelled_on_pet(self, loaded_owner):
        scheduler = Scheduler(loaded_owner)
        scheduler.generate_schedule()
        scheduler.cancel_task("Morning walk")
        all_tasks = loaded_owner.pets[0].tasks
        walk = next(t for t in all_tasks if t.title == "Morning walk")
        assert walk.status == "cancelled"

    def test_cancel_nonexistent_task_does_not_raise(self, loaded_owner):
        scheduler = Scheduler(loaded_owner)
        scheduler.cancel_task("Ghost task")  # should not raise

    def test_explain_plan_before_generate_returns_message(self, loaded_owner):
        scheduler = Scheduler(loaded_owner)
        result = scheduler.explain_plan()
        assert "generate_schedule" in result

    def test_explain_plan_contains_owner_name(self, loaded_owner):
        scheduler = Scheduler(loaded_owner)
        scheduler.generate_schedule()
        plan = scheduler.explain_plan()
        assert "Jordan" in plan

    def test_owner_availability_not_mutated_after_schedule(self, loaded_owner):
        original = list(loaded_owner.availability)
        scheduler = Scheduler(loaded_owner)
        scheduler.generate_schedule()
        assert loaded_owner.availability == original

    def test_generate_schedule_with_no_tasks_returns_empty(self, owner_with_availability):
        pet = Pet("Mochi", "dog", "Shiba", 3)
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)
        assert scheduler.generate_schedule() == []
