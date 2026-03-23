from pawpal_system import Pet, Task, Owner, Scheduler, Priority
import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🐾 PawPal+ — Your Pet's Personal Scheduler")
st.caption("Keep your furry, feathery, or scaly friends happy and on schedule!")

# ── Session-state vault ───────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None
if "availability" not in st.session_state:
    st.session_state.availability = [("08:00", 60), ("12:00", 30), ("18:00", 90)]

# ── Helpers ───────────────────────────────────────────────────────────────────
SPECIES_EMOJI = {"dog": "🐶", "cat": "🐱", "other": "🐾"}
PRIORITY_EMOJI = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
FREQ_EMOJI     = {"daily": "📅", "weekly": "🗓️", "as-needed": "📌"}

# ── Owner setup ───────────────────────────────────────────────────────────────
st.subheader("🧑 Pet Parent Profile")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Your name", value="Jordan")
with col2:
    owner_email = st.text_input("Your email", value="jordan@example.com")

with st.expander("⏰ Set your availability windows"):
    st.caption("Tell us when you're free to care for your pet — start time (HH:MM) and how many minutes.")
    new_windows = []
    for i, (t, m) in enumerate(st.session_state.availability):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            nt = st.text_input("Start time", value=t, key=f"avail_t_{i}")
        with c2:
            nm = st.number_input("Minutes free", min_value=1, max_value=480, value=m, key=f"avail_m_{i}")
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
    if st.button("➕ Add window"):
        st.session_state.availability.append((add_time, add_mins))
        st.rerun()

if st.button("💾 Save profile"):
    st.session_state.owner = Owner(owner_name, owner_email, list(st.session_state.availability))
    st.session_state.scheduler = None
    st.success(f"Welcome, {owner_name}! Your profile is all set. 🎉")

st.divider()

# ── Pet setup ─────────────────────────────────────────────────────────────────
st.subheader("🐾 Meet Your Pet")
if st.session_state.owner is None:
    st.info("👆 Save your profile above to get started!")
else:
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        pet_name = st.text_input("Pet's name", value="Mochi")
    with pc2:
        species = st.selectbox(
            "Species", ["dog", "cat", "other"],
            format_func=lambda s: f"{SPECIES_EMOJI[s]} {s.title()}"
        )
    with pc3:
        breed = st.text_input("Breed", value="Shiba Inu")
    with pc4:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

    if st.button(f"💾 Save {pet_name or 'pet'}"):
        pet = Pet(pet_name, species, breed, age)
        st.session_state.pet = pet
        st.session_state.owner.add_pet(pet)
        st.session_state.scheduler = None
        emoji = SPECIES_EMOJI.get(species, "🐾")
        st.success(f"{emoji} {pet_name} the {breed} has joined the family!")

st.divider()

# ── Task management ───────────────────────────────────────────────────────────
st.subheader("📋 Task List")
if st.session_state.pet is None:
    st.info("🐾 Add your pet above, then start building their routine!")
else:
    pet = st.session_state.pet
    tc1, tc2, tc3, tc4 = st.columns(4)
    with tc1:
        task_title = st.text_input("Task name", value="Morning walk")
    with tc2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with tc3:
        priority_str = st.selectbox(
            "Priority", ["LOW", "MEDIUM", "HIGH"], index=2,
            format_func=lambda p: f"{PRIORITY_EMOJI[p]} {p}"
        )
    with tc4:
        frequency = st.selectbox(
            "Frequency", ["daily", "weekly", "as-needed"],
            format_func=lambda f: f"{FREQ_EMOJI[f]} {f.title()}"
        )

    if st.button("➕ Add task"):
        already_exists = any(t.title == task_title for t in pet.tasks)
        if already_exists:
            st.warning(f"⚠️ '{task_title}' already exists for {pet.name}. Try a different name!")
        else:
            task = Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=Priority[priority_str],
                frequency=frequency,
            )
            pet.add_task(task)
            st.session_state.scheduler = None
            st.success(f"✅ '{task_title}' added to {pet.name}'s routine!")

    pending = pet.get_pending_tasks()
    if pending:
        pet_emoji = SPECIES_EMOJI.get(pet.species, "🐾")
        st.markdown(f"**{pet_emoji} {pet.name}'s pending tasks** — {len(pending)} item(s):")
        rows = [
            {
                "Task": t.title,
                "⏱ Duration": f"{t.duration_minutes} min",
                "Priority": f"{PRIORITY_EMOJI[t.priority.name]} {t.priority.name}",
                "Frequency": f"{FREQ_EMOJI.get(t.frequency, '')} {t.frequency}",
                "Status": t.status.title(),
            }
            for t in pending
        ]
        st.table(rows)

        remove_title = st.selectbox("Select task to remove", [""] + [t.title for t in pending])
        if st.button("🗑️ Remove selected task") and remove_title:
            pet.remove_task(remove_title)
            st.session_state.scheduler = None
            st.rerun()
    else:
        st.info(f"No pending tasks for {pet.name} yet — add one above! 🐾")

st.divider()

# ── Schedule generation ───────────────────────────────────────────────────────
st.subheader("📆 Build Schedule")
if st.session_state.owner is None or st.session_state.pet is None:
    st.info("🐾 Set up your profile and pet first, then we'll build the perfect schedule!")
else:
    gen_col, filter_col = st.columns([1, 2])

    with gen_col:
        if st.button("🚀 Generate schedule", use_container_width=True):
            scheduler = Scheduler(st.session_state.owner)
            scheduled = scheduler.generate_schedule()
            st.session_state.scheduler = scheduler
            if scheduled:
                st.success(f"🎉 Scheduled {len(scheduled)} task(s) — let's go!")
            else:
                st.warning("😕 No tasks could fit the available windows. Try adding more time slots.")

    if st.session_state.scheduler is not None:
        scheduler = st.session_state.scheduler

        # ── Conflict warnings (detect_conflicts) ──────────────────────────
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.markdown("### ⚠️ Scheduling Conflicts Detected")
            for warning in conflicts:
                st.warning(f"🔔 {warning}")
        else:
            st.success("✅ No conflicts — your pet's schedule looks great!")

        # ── Filter controls (filter_tasks) ────────────────────────────────
        with filter_col:
            f1, f2 = st.columns(2)
            with f1:
                filter_status = st.selectbox(
                    "Filter by status",
                    ["All", "pending", "complete", "cancelled"],
                    key="sched_filter_status",
                )
            with f2:
                all_pet_names = [p.name for p in scheduler.owner.pets]
                filter_pet = st.selectbox(
                    "Filter by pet",
                    ["All"] + all_pet_names,
                    key="sched_filter_pet",
                )

        # ── Apply filter_tasks + sort_tasks_by_time ────────────────────────
        all_tasks     = list(scheduler.scheduled_tasks)
        status_arg    = None if filter_status == "All" else filter_status
        pet_arg       = None if filter_pet == "All" else filter_pet
        filtered      = scheduler.filter_tasks(all_tasks, status=status_arg, pet_name=pet_arg)
        sorted_tasks  = scheduler.sort_tasks_by_time(filtered)

        # ── Metrics row ───────────────────────────────────────────────────
        total     = len(all_tasks)
        n_pending = len([t for t in all_tasks if t.status == "pending"])
        n_done    = len([t for t in all_tasks if t.status == "complete"])
        n_high    = len([t for t in all_tasks if t.is_high_priority()])
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total tasks", total)
        m2.metric("Pending", n_pending)
        m3.metric("Completed", n_done)
        m4.metric("High priority", n_high)

        # ── Schedule table ────────────────────────────────────────────────
        st.markdown(f"### 🗓️ Schedule ({len(sorted_tasks)} shown)")
        if sorted_tasks:
            pets_by_name = {p.name: p for p in scheduler.owner.pets}
            rows = []
            for t in sorted_tasks:
                pet_name_str = scheduler._find_pet_for_task(t)
                pet_obj      = pets_by_name.get(pet_name_str)
                pet_label = (
                    f"{SPECIES_EMOJI.get(pet_obj.species, '🐾')} {pet_obj.name}"
                    if pet_obj else "—"
                )
                rows.append({
                    "🕐 Time":     t.scheduled_time or "—",
                    "Task":        t.title,
                    "Priority":    f"{PRIORITY_EMOJI[t.priority.name]} {t.priority.name}",
                    "⏱ Duration":  f"{t.duration_minutes} min",
                    "Pet":         pet_label,
                    "Status":      t.status.title(),
                })
            st.table(rows)
        else:
            st.info("No tasks match your current filter. 🐾")

        # ── Cancel task ───────────────────────────────────────────────────
        cancel_options = [t.title for t in scheduler.scheduled_tasks if t.status == "pending"]
        if cancel_options:
            st.markdown("---")
            cc1, cc2 = st.columns([3, 1])
            with cc1:
                cancel_title = st.selectbox("Select task to cancel", [""] + cancel_options)
            with cc2:
                st.write("")
                st.write("")
                if st.button("❌ Cancel task") and cancel_title:
                    scheduler.cancel_task(cancel_title)
                    st.rerun()
