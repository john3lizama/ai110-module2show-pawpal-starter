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


# ---------------------------------------------------------------------------
# Sorting Correctness — sort_tasks_by_time
# ---------------------------------------------------------------------------

class TestSortingCorrectness:
    """Verify that sort_tasks_by_time returns tasks in chronological order."""

    def _make_scheduler(self, owner_with_availability):
        return Scheduler(owner_with_availability)

    def test_sorts_tasks_in_chronological_order(self, owner_with_availability):
        """Tasks given out-of-order times should come back earliest-first."""
        scheduler = Scheduler(owner_with_availability)
        t1 = Task("Evening walk",  30, Priority.LOW,  scheduled_time="18:00")
        t2 = Task("Lunch feeding", 10, Priority.HIGH, scheduled_time="12:00")
        t3 = Task("Morning meds",  5,  Priority.HIGH, scheduled_time="08:00")
        result = scheduler.sort_tasks_by_time([t1, t2, t3])
        assert [t.scheduled_time for t in result] == ["08:00", "12:00", "18:00"]

    def test_tasks_without_scheduled_time_sort_to_end(self, owner_with_availability):
        """Tasks with no scheduled_time use sentinel (24,0) and appear last."""
        scheduler = Scheduler(owner_with_availability)
        t_no_time = Task("Unscheduled",  15, Priority.MEDIUM)
        t_early    = Task("Early task",   10, Priority.HIGH, scheduled_time="07:00")
        result = scheduler.sort_tasks_by_time([t_no_time, t_early])
        assert result[0].scheduled_time == "07:00"
        assert result[1].scheduled_time is None

    def test_single_digit_hour_sorts_before_two_digit_hour(self, owner_with_availability):
        """'9:00' must sort before '10:00' (fails lexicographically but passes numerically)."""
        scheduler = Scheduler(owner_with_availability)
        t_ten  = Task("Ten o'clock", 20, Priority.LOW,  scheduled_time="10:00")
        t_nine = Task("Nine o'clock", 20, Priority.LOW, scheduled_time="09:00")
        result = scheduler.sort_tasks_by_time([t_ten, t_nine])
        assert result[0].scheduled_time == "09:00"
        assert result[1].scheduled_time == "10:00"

    def test_sort_is_stable_for_same_scheduled_time(self, owner_with_availability):
        """Two tasks sharing a time slot should both be present in output."""
        scheduler = Scheduler(owner_with_availability)
        t1 = Task("Task A", 10, Priority.HIGH,   scheduled_time="08:00")
        t2 = Task("Task B", 20, Priority.MEDIUM, scheduled_time="08:00")
        result = scheduler.sort_tasks_by_time([t1, t2])
        assert len(result) == 2
        assert all(t.scheduled_time == "08:00" for t in result)

    def test_sort_empty_list_returns_empty(self, owner_with_availability):
        scheduler = Scheduler(owner_with_availability)
        assert scheduler.sort_tasks_by_time([]) == []

    def test_sort_does_not_mutate_original_list(self, owner_with_availability):
        """sort_tasks_by_time must return a new list, leaving the original unchanged."""
        scheduler = Scheduler(owner_with_availability)
        t1 = Task("Z task", 10, Priority.LOW,  scheduled_time="20:00")
        t2 = Task("A task", 10, Priority.HIGH, scheduled_time="06:00")
        original = [t1, t2]
        scheduler.sort_tasks_by_time(original)
        assert original[0].title == "Z task"  # order unchanged


# ---------------------------------------------------------------------------
# Recurrence Logic — complete_task
# ---------------------------------------------------------------------------

class TestRecurrenceLogic:
    """Confirm that completing a recurring task creates the correct next occurrence."""

    def test_completing_daily_task_creates_next_task(self, owner_with_availability):
        """Completing a daily task should add exactly one new pending task to the pet."""
        pet = Pet("Mochi", "dog", "Shiba", 3)
        pet.add_task(Task("Morning walk", 30, Priority.HIGH, frequency="daily"))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        scheduler.complete_task("Morning walk")

        pending = pet.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].title == "Morning walk"

    def test_completing_daily_task_sets_due_date_to_tomorrow(self, owner_with_availability):
        """The new task's due_date should be today + 1 day."""
        from datetime import date, timedelta
        pet = Pet("Mochi", "dog", "Shiba", 3)
        pet.add_task(Task("Morning walk", 30, Priority.HIGH, frequency="daily"))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        next_task = scheduler.complete_task("Morning walk")

        expected = (date.today() + timedelta(days=1)).isoformat()
        assert next_task.due_date == expected

    def test_completing_weekly_task_sets_due_date_seven_days_out(self, owner_with_availability):
        """Weekly recurrence should schedule the next task 7 days from today."""
        from datetime import date, timedelta
        pet = Pet("Luna", "cat", "Siamese", 2)
        pet.add_task(Task("Vet checkup", 60, Priority.HIGH, frequency="weekly"))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        next_task = scheduler.complete_task("Vet checkup")

        expected = (date.today() + timedelta(days=7)).isoformat()
        assert next_task.due_date == expected

    def test_completing_as_needed_task_does_not_create_recurrence(self, owner_with_availability):
        """'as-needed' tasks should return None and add no new tasks."""
        pet = Pet("Mochi", "dog", "Shiba", 3)
        pet.add_task(Task("Bath", 45, Priority.MEDIUM, frequency="as-needed"))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        result = scheduler.complete_task("Bath")

        assert result is None
        assert pet.get_pending_tasks() == []

    def test_original_task_is_marked_complete_after_recurrence(self, owner_with_availability):
        """The completed task must have status 'complete', not 'pending'."""
        pet = Pet("Mochi", "dog", "Shiba", 3)
        original = Task("Morning walk", 30, Priority.HIGH, frequency="daily")
        pet.add_task(original)
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        scheduler.complete_task("Morning walk")

        assert original.status == "complete"

    def test_new_recurring_task_inherits_properties(self, owner_with_availability):
        """Recurrence must copy title, duration, priority, frequency, and scheduled_time."""
        pet = Pet("Mochi", "dog", "Shiba", 3)
        pet.add_task(Task("Morning walk", 30, Priority.HIGH,
                          frequency="daily", scheduled_time="08:00"))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        next_task = scheduler.complete_task("Morning walk")

        assert next_task.title == "Morning walk"
        assert next_task.duration_minutes == 30
        assert next_task.priority == Priority.HIGH
        assert next_task.frequency == "daily"
        assert next_task.scheduled_time == "08:00"

    def test_complete_nonexistent_task_returns_none(self, owner_with_availability):
        """Completing a task title that doesn't exist should return None silently."""
        pet = Pet("Mochi", "dog", "Shiba", 3)
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        assert scheduler.complete_task("Ghost task") is None

    def test_completing_already_complete_task_does_not_create_duplicate(self, owner_with_availability):
        """Only pending tasks trigger recurrence; calling again on the completed task is a no-op."""
        pet = Pet("Mochi", "dog", "Shiba", 3)
        pet.add_task(Task("Morning walk", 30, Priority.HIGH, frequency="daily"))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        scheduler.complete_task("Morning walk")   # completes original → adds 1 new
        scheduler.complete_task("Morning walk")   # completes the new one → adds 1 more

        # After two completions there should be exactly one pending (the second recurrence)
        assert len(pet.get_pending_tasks()) == 1


# ---------------------------------------------------------------------------
# Conflict Detection — detect_conflicts
# ---------------------------------------------------------------------------

class TestConflictDetection:
    """Verify that the Scheduler correctly flags duplicate scheduled times."""

    def test_no_conflicts_returns_empty_list(self, owner_with_availability):
        """All tasks at different times → no warnings."""
        pet = Pet("Mochi", "dog", "Shiba", 3)
        pet.add_task(Task("Walk",    30, Priority.HIGH,   scheduled_time="08:00"))
        pet.add_task(Task("Feeding", 10, Priority.MEDIUM, scheduled_time="12:00"))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        assert scheduler.detect_conflicts() == []

    def test_two_tasks_same_time_triggers_conflict(self, owner_with_availability):
        """Two pending tasks at 08:00 should produce exactly one warning."""
        pet = Pet("Mochi", "dog", "Shiba", 3)
        pet.add_task(Task("Walk",    30, Priority.HIGH,   scheduled_time="08:00"))
        pet.add_task(Task("Feeding", 10, Priority.MEDIUM, scheduled_time="08:00"))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        warnings = scheduler.detect_conflicts()

        assert len(warnings) == 1
        assert "08:00" in warnings[0]

    def test_conflict_warning_contains_both_task_titles(self, owner_with_availability):
        """The warning string must name both conflicting tasks."""
        pet = Pet("Mochi", "dog", "Shiba", 3)
        pet.add_task(Task("Walk",    30, Priority.HIGH,   scheduled_time="08:00"))
        pet.add_task(Task("Feeding", 10, Priority.MEDIUM, scheduled_time="08:00"))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        warning = scheduler.detect_conflicts()[0]

        assert "Walk" in warning
        assert "Feeding" in warning

    def test_conflict_across_two_different_pets(self, owner_with_availability):
        """Conflicts should be detected even when tasks belong to different pets."""
        pet_a = Pet("Mochi", "dog",  "Shiba",   3)
        pet_b = Pet("Luna",  "cat",  "Siamese",  2)
        pet_a.add_task(Task("Walk",    30, Priority.HIGH,   scheduled_time="08:00"))
        pet_b.add_task(Task("Feeding", 10, Priority.MEDIUM, scheduled_time="08:00"))
        owner_with_availability.add_pet(pet_a)
        owner_with_availability.add_pet(pet_b)
        scheduler = Scheduler(owner_with_availability)

        warnings = scheduler.detect_conflicts()

        assert len(warnings) == 1
        assert "Mochi" in warnings[0]
        assert "Luna"  in warnings[0]

    def test_three_tasks_same_slot_produces_one_warning(self, owner_with_availability):
        """Three tasks colliding at the same time should appear in a single warning, not three."""
        pet = Pet("Mochi", "dog", "Shiba", 3)
        pet.add_task(Task("Walk",     30, Priority.HIGH,   scheduled_time="08:00"))
        pet.add_task(Task("Feeding",  10, Priority.MEDIUM, scheduled_time="08:00"))
        pet.add_task(Task("Grooming", 20, Priority.LOW,    scheduled_time="08:00"))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        warnings = scheduler.detect_conflicts()

        assert len(warnings) == 1
        assert "Walk" in warnings[0] and "Feeding" in warnings[0] and "Grooming" in warnings[0]

    def test_completed_task_at_same_time_does_not_trigger_conflict(self, owner_with_availability):
        """Completed tasks should be invisible to conflict detection."""
        pet = Pet("Mochi", "dog", "Shiba", 3)
        t_done = Task("Old walk", 30, Priority.HIGH, scheduled_time="08:00")
        t_done.mark_complete()
        pet.add_task(t_done)
        pet.add_task(Task("New walk", 30, Priority.HIGH, scheduled_time="08:00"))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        assert scheduler.detect_conflicts() == []

    def test_task_without_scheduled_time_is_excluded_from_conflict_check(self, owner_with_availability):
        """Tasks with no scheduled_time must be skipped — no KeyError, no false positive."""
        pet = Pet("Mochi", "dog", "Shiba", 3)
        pet.add_task(Task("Walk",        30, Priority.HIGH))           # no scheduled_time
        pet.add_task(Task("Feeding",     10, Priority.MEDIUM))         # no scheduled_time
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        assert scheduler.detect_conflicts() == []

    def test_multiple_conflict_slots_each_produce_one_warning(self, owner_with_availability):
        """Two separate conflict slots (08:00 and 12:00) → two distinct warnings."""
        pet = Pet("Mochi", "dog", "Shiba", 3)
        pet.add_task(Task("Walk A",    30, Priority.HIGH,   scheduled_time="08:00"))
        pet.add_task(Task("Walk B",    30, Priority.HIGH,   scheduled_time="08:00"))
        pet.add_task(Task("Lunch A",   10, Priority.MEDIUM, scheduled_time="12:00"))
        pet.add_task(Task("Lunch B",   10, Priority.MEDIUM, scheduled_time="12:00"))
        owner_with_availability.add_pet(pet)
        scheduler = Scheduler(owner_with_availability)

        warnings = scheduler.detect_conflicts()

        assert len(warnings) == 2
        assert any("08:00" in w for w in warnings)
        assert any("12:00" in w for w in warnings)

    def test_no_pets_returns_empty_conflict_list(self, owner_with_availability):
        """An owner with no pets should return an empty conflict list without raising."""
        scheduler = Scheduler(owner_with_availability)
        assert scheduler.detect_conflicts() == []
