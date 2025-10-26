import streamlit as st


def verify_error(result: list[dict] | dict) -> bool:
    """Check API result and display any error message."""
    if not isinstance(result, dict):
        return False
    
    status_code = result.get("status_code")
    st.error(f"Error: {result.get('error')} [status code: {status_code}]")
    if status_code == 401:
        st.warning("Expired session. Please log in again.")
    return True


def todos_page_content():
    st.title("🗒️ Todos")

    client = st.session_state["api_client"]

    # --- Persist filters between runs ---
    if "todos_filters" not in st.session_state:
        st.session_state.todos_filters = {"complete": None, "search": None}

    filters = st.session_state.todos_filters

    # --- UI Filters ---
    col1, col2, col3, col4 = st.columns([1, 2, 1, 1], vertical_alignment="bottom")

    with col1:
        complete_opt = st.selectbox(
            "Status",
            options=["--", True, False],
            format_func=lambda x: "Complete" if x is True else ("Incomplete" if x is False else "--"),
            index=["--", True, False].index(filters["complete"] if filters["complete"] is not None else "--"),
        )

    with col2:
        search_opt = st.text_input("Search", value=filters["search"] or "",
                                   help="Search todos by title or description")

    with col3:
        if st.button("Filter", use_container_width=True):
            complete = None if complete_opt == "--" else complete_opt
            search = search_opt.strip() or None if search_opt else None

            if complete is None and search is None:
                st.warning("No filter options selected.")
            else:
                st.session_state.todos_filters = {"complete": complete, "search": search}
                st.rerun()

    with col4:
        if st.button("Reset", use_container_width=True):
            st.session_state.todos_filters = {"complete": None, "search": None}
            st.rerun()

    # --- Fetch data ---
    st.divider()

    with st.spinner("Loading todos..."):
        result = client.read_all_todos(**filters)
        if verify_error(result):
            return

    st.subheader(f"Todos : {len(result)}")

    if not result:
        st.info("Congratulations! You don't have any more tasks to complete.")
        return

    # --- Display ---
    for i, todo in enumerate(result):
        
        extender_text = f"**{todo.get('title')}** - Priority: **{todo.get('priority')}**"
        extender_text += f" (ID: {todo.get('id')})"
        extender_icon = "✅" if todo.get('complete') is True else "⏳"
        
        with st.expander(extender_text, icon=extender_icon):
            st.write(f"**Description:** {todo.get('description')}")
            
            extender_col1, extender_col2 = st.columns(2, width=250)
            with extender_col1:
                edit_button = st.button("Edit", key=f"edit_{i}", width=100)
            with extender_col2:
                delete_button = st.button("Delete", key=f"delete_{i}", width=100)
                
            if edit_button:
                with st.form(f"edit_form_{i}"):
                    
                    fields = {
                        "title":st.text_input("Title", value=todo.get('title', "")),
                        "description":st.text_area(
                            "Description", value=todo.get('description', ""),
                            max_chars=250
                        ),
                        "priority":st.slider("Priority", min_value=1, max_value=5,
                                             value=todo.get('priority')),
                        "complete":st.checkbox("Completed",
                                               value=todo.get('complete', False))
                    }
                    
                    submitted = st.form_submit_button("Save changes")
                    
                    if submitted:
                        updated_data = {}
                        for f, v in fields.items():
                            if isinstance(v, str):
                                if (v.strip() != "") and (v != todo.get(f)):
                                    updated_data[f] = v
                            elif v != todo.get(f):
                                updated_data[f] = v