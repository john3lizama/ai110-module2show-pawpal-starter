# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

A user should be able to add a new pet with the required information.

A user should be able to see their curated schedule that alligns with their availabilty.

A user should be able to cancel appointments or rescedule an upcoming tasks if something comes up unexpectedly.

**UML Class Diagram:**

```mermaid
classDiagram
    class Owner {
        +String name
        +String email
        +List~String~ availability
        +List~Pet~ pets
        +add_pet(pet: Pet) void
        +remove_pet(pet_name: String) void
        +get_schedule() List~Task~
    }

    class Pet {
        +String name
        +String species
        +String breed
        +int age
        +List~Task~ tasks
        +add_task(task: Task) void
        +remove_task(task_title: String) void
        +get_pending_tasks() List~Task~
    }

    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String status
        +String scheduled_time
        +mark_complete() void
        +reschedule(new_time: String) void
        +cancel() void
        +is_high_priority() bool
    }

    class Scheduler {
        +Owner owner
        +List~Task~ scheduled_tasks
        +generate_schedule() List~Task~
        +prioritize_tasks(tasks: List~Task~) List~Task~
        +explain_plan() String
        +cancel_task(task_title: String) void
    }

    Owner "1" --> "many" Pet : owns
    Pet "1" --> "many" Task : has
    Scheduler "1" --> "1" Owner : schedules for
    Scheduler "1" --> "many" Task : organizes
```


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
