from pawpal_system import Pet, Task, Owner, Scheduler, Priority
import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Session-state vault ──────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None
if "availability" not in st.session_state:
    st.session_state.availability = [("08:00", 60), ("12:00", 30), ("18:00", 90)]

# ── Owner setup ──────────────────────────────────────────────────────────────
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Name", value="Jordan")
with col2:
    owner_email = st.text_input("Email", value="jordan@example.com")

with st.expander("Availability windows"):
    st.caption("Each row is a start time (HH:MM) and how many minutes are free.")
    new_windows = []
    for i, (t, m) in enumerate(st.session_state.availability):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            nt = st.text_input("Start", value=t, key=f"avail_t_{i}")
        with c2:
            nm = st.number_input("Minutes", min_value=1, max_value=480, value=m, key=f"avail_m_{i}")
        with c3:
            st.write("")
            st.write("")
            remove = st.button("✕", key=f"rm_avail_{i}")
        if not remove:
            new_windows.append((nt, nm))
    st.session_state.availability = new_windows

    ac1, ac2 = st.columns(2)
    with ac1:
        add_time = st.text_input("New start time", value="10:00", key="new_avail_t")
    with ac2:
        add_mins = st.number_input("Minutes free", min_value=1, max_value=480, value=30, key="new_avail_m")
    if st.button("Add window"):
        st.session_state.availability.append((add_time, add_mins))
        st.rerun()

if st.button("Save owner"):
    st.session_state.owner = Owner(owner_name, owner_email, list(st.session_state.availability))
    st.session_state.scheduler = None  # reset scheduler when owner changes
    st.success(f"Owner '{owner_name}' saved.")

st.divider()

# ── Pet setup ────────────────────────────────────────────────────────────────
st.subheader("Pet")
if st.session_state.owner is None:
    st.info("Save an owner first.")
else:
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with pc2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with pc3:
        breed = st.text_input("Breed", value="Shiba Inu")
    with pc4:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

    if st.button("Save pet"):
        pet = Pet(pet_name, species, breed, age)
        st.session_state.pet = pet
        st.session_state.owner.add_pet(pet)
        st.session_state.scheduler = None
        st.success(f"Pet '{pet_name}' saved and linked to {st.session_state.owner.name}.")

st.divider()

# ── Task management ──────────────────────────────────────────────────────────
st.subheader("Tasks")
if st.session_state.pet is None:
    st.info("Save a pet first.")
else:
    tc1, tc2, tc3, tc4 = st.columns(4)
    with tc1:
        task_title = st.text_input("Title", value="Morning walk")
    with tc2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with tc3:
        priority_str = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH"], index=2)
    with tc4:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as-needed"])

    if st.button("Add task"):
        already_exists = any(
            t.title == task_title for t in st.session_state.pet.tasks
        )
        if already_exists:
            st.warning(f"Task '{task_title}' already exists for {st.session_state.pet.name}.")
        else:
            task = Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=Priority[priority_str],
                frequency=frequency,
            )
            st.session_state.pet.add_task(task)
            st.session_state.scheduler = None
            st.success(f"Added '{task_title}'.")

    pending = st.session_state.pet.get_pending_tasks()
    if pending:
        st.write(f"Pending tasks for **{st.session_state.pet.name}**:")
        rows = [
            {
                "Title": t.title,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority.name,
                "Frequency": t.frequency,
                "Status": t.status,
            }
            for t in pending
        ]
        st.table(rows)

        remove_title = st.selectbox("Remove task", [""] + [t.title for t in pending])
        if st.button("Remove selected task") and remove_title:
            st.session_state.pet.remove_task(remove_title)
            st.session_state.scheduler = None
            st.rerun()
    else:
        st.info("No pending tasks. Add one above.")

st.divider()

# ── Schedule generation ──────────────────────────────────────────────────────
st.subheader("Build Schedule")
if st.session_state.owner is None or st.session_state.pet is None:
    st.info("Set up an owner and a pet before generating a schedule.")
else:
    if st.button("Generate schedule"):
        scheduler = Scheduler(st.session_state.owner)
        scheduled = scheduler.generate_schedule()
        st.session_state.scheduler = scheduler
        if scheduled:
            st.success(f"Scheduled {len(scheduled)} task(s).")
        else:
            st.warning("No tasks could be fit into the available time windows.")

    if st.session_state.scheduler is not None:
        st.text(st.session_state.scheduler.explain_plan())

        cancel_options = [t.title for t in st.session_state.scheduler.scheduled_tasks]
        if cancel_options:
            cancel_title = st.selectbox("Cancel a task", [""] + cancel_options)
            if st.button("Cancel selected task") and cancel_title:
                st.session_state.scheduler.cancel_task(cancel_title)
                st.rerun()
