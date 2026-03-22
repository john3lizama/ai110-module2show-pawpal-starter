from pawpal_system import Pet, Task, Owner, Scheduler, Priority



def main():
    owner = Owner("bob")
    pet1 = Pet("fluffy", "cat", "persian", 3)
    pet2 = Pet("rex", "dog", "labrador", 5)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    Task1 = Task("feed", "08:00", Priority.HIGH)
    Task2 = Task("walk", "18:00", Priority.MEDIUM)
    Task3 = Task("vet", "12:00", Priority.HIGH)
    pet1.add_task(Task1)
    pet2.add_task(Task2)
    pet1.add_task(Task3)
    scheduler = Scheduler(owner)
    pending_tasks = owner.get_schedule()
    for task in pending_tasks:
        print(f"{task.title} for {task.scheduled_time} with priority {task.priority.name}")

if __name__ == "__main__":    main()