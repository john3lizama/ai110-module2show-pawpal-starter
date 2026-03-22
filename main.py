from pawpal_system import Pet, Task, Owner, Scheduler, Priority


def main():
    owner = Owner("Bob", "bob@email.com", [("08:00", 120), ("12:00", 60), ("18:00", 90)])

    fluffy = Pet("Fluffy", "cat", "Persian", 3)
    rex = Pet("Rex", "dog", "Labrador", 5)
    owner.add_pet(fluffy)
    owner.add_pet(rex)

    # Add tasks out of order (later times first)
    fluffy.add_task(Task("Evening Feeding",  10, Priority.HIGH,   scheduled_time="18:30"))
    fluffy.add_task(Task("Vet Checkup",      45, Priority.HIGH,   scheduled_time="12:00"))
    fluffy.add_task(Task("Morning Feeding",  10, Priority.HIGH,   scheduled_time="07:00"))
    fluffy.add_task(Task("Grooming",         20, Priority.LOW,    scheduled_time="10:00"))

    rex.add_task(Task("Afternoon Walk",      30, Priority.MEDIUM, scheduled_time="15:00"))
    rex.add_task(Task("Morning Walk",        30, Priority.MEDIUM, scheduled_time="08:00"))
    rex.add_task(Task("Training Session",    20, Priority.LOW,    scheduled_time="09:30"))

    # Deliberately add tasks that clash at the same time
    # Same-pet conflict: two Fluffy tasks both at 08:00
    fluffy.add_task(Task("Medication",    5,  Priority.HIGH,   scheduled_time="08:00"))
    # Cross-pet conflict: Rex also has something at 08:00
    rex.add_task(Task("Flea Treatment",  15, Priority.MEDIUM, scheduled_time="08:00"))
    # Another cross-pet conflict at 18:30 (Fluffy already has Evening Feeding there)
    rex.add_task(Task("Night Walk",      20, Priority.LOW,    scheduled_time="18:30"))

    scheduler = Scheduler(owner)

    # --- Conflict detection (must run before completing any tasks) ---
    print("=== Conflict Detection ===")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts found.")
    print()

    # --- Demonstrate auto-recurrence ---
    print("=== Completing Recurring Tasks ===")

    # "Morning Feeding" is daily → should spawn a new task for tomorrow
    new_task = scheduler.complete_task("Morning Feeding")
    if new_task:
        print(f"  'Morning Feeding' completed. Next occurrence → due_date={new_task.due_date}, status={new_task.status}")

    # "Vet Checkup" is daily by default → spawns next occurrence too
    new_task = scheduler.complete_task("Vet Checkup")
    if new_task:
        print(f"  'Vet Checkup' completed.    Next occurrence → due_date={new_task.due_date}, status={new_task.status}")

    # Change Morning Walk to weekly, then complete it
    rex.tasks[1].frequency = "weekly"
    new_task = scheduler.complete_task("Morning Walk")
    if new_task:
        print(f"  'Morning Walk' completed.   Next occurrence → due_date={new_task.due_date}, status={new_task.status}")

    all_tasks = []
    for pet in owner.pets:
        all_tasks.extend(pet.tasks)

    # --- Sort by time ---
    print("=== All Tasks Sorted by Time ===")
    for task in scheduler.sort_tasks_by_time(all_tasks):
        pet_name = scheduler._find_pet_for_task(task)
        print(f"  {task.scheduled_time}  {task.title:<20}  [{task.priority.name:<6}]  status={task.status}  pet={pet_name}")

    # --- Filter: pending only ---
    print("\n=== Pending Tasks Only ===")
    pending = scheduler.filter_tasks(all_tasks, status="pending")
    for task in scheduler.sort_tasks_by_time(pending):
        pet_name = scheduler._find_pet_for_task(task)
        print(f"  {task.scheduled_time}  {task.title:<20}  pet={pet_name}")

    # --- Filter: complete only ---
    print("\n=== Completed Tasks Only ===")
    completed = scheduler.filter_tasks(all_tasks, status="complete")
    for task in scheduler.sort_tasks_by_time(completed):
        pet_name = scheduler._find_pet_for_task(task)
        print(f"  {task.scheduled_time}  {task.title:<20}  pet={pet_name}")

    # --- Filter: by pet name ---
    print("\n=== Rex's Tasks Only ===")
    rex_tasks = scheduler.filter_tasks(all_tasks, pet_name="Rex")
    for task in scheduler.sort_tasks_by_time(rex_tasks):
        print(f"  {task.scheduled_time}  {task.title:<20}  status={task.status}")

    # --- Filter: combine status + pet name ---
    print("\n=== Rex's Pending Tasks ===")
    rex_pending = scheduler.filter_tasks(all_tasks, status="pending", pet_name="Rex")
    for task in scheduler.sort_tasks_by_time(rex_pending):
        print(f"  {task.scheduled_time}  {task.title:<20}  [{task.priority.name}]")


if __name__ == "__main__":
    main()
