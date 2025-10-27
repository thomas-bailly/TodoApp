import streamlit as st
import time


client = st.session_state["api_client"]

def verify_error(result: list[dict] | dict) -> bool:
    """Check API result and display any error message."""
    if not isinstance(result, dict):
        return False
    
    status_code = result.get("status_code")
    st.error(f"Error: {result.get('error')} [status code: {status_code}]")
    if status_code == 401:
        st.warning("Expired session. Please log in again.")
    return True

@st.dialog("Add Todo")
def add_todo_dialog():
    data = {
        "title":st.text_input("Title", value="", max_chars=100,
                              help="minimum 3 characters"),
        "description":st.text_area(
            "Description", value="", max_chars=250
        ),
        "priority":st.slider("Priority", min_value=1, max_value=5,
                             value=3),
        "complete":st.checkbox("Completed", value=False)
    }
    
    if st.button("Submit"):
        result = client.create_todo(data=data)
        
        if "error" in result:
            st.error(f"Creation failed: {result['error']}")
        else:
            st.success(result["message"])
            time.sleep(0.5)
            st.session_state.pop("todos_data", None)
            st.rerun()

@st.dialog("Edit Todo")
def edit_todo_dialog(todo):
    
    fields = {
        "title":st.text_input("Title", value=todo.get('title', ""), max_chars=100,
                              help="minimum 3 characters"),
        "description":st.text_area(
            "Description", value=todo.get('description', ""),
            max_chars=250
        ),
        "priority":st.slider("Priority", min_value=1, max_value=5,
                             value=todo.get('priority')),
        "complete":st.checkbox("Completed",
                               value=todo.get('complete', False))
    }
    
    if st.button("Save changes"):
        updated_data = {}
        for f, v in fields.items():
            if isinstance(v, str):
                if (v.strip() != "") and (v != todo.get(f)):
                    updated_data[f] = v
            elif v != todo.get(f):
                updated_data[f] = v
                 
        result = client.update_todo(todo_id=todo.get('id'),
                                        data=updated_data)
                        
        if "error" in result:
            st.error(f"Update failed: {result['error']}")
        else:
            st.success(result["message"])
            time.sleep(0.5)
            st.session_state.pop("todos_data", None)
            st.rerun()

def delete_todo(todo):
    result = client.delete_todo(todo_id=todo.get('id'))
    if "error" in result:
        st.error(f"Deletion failed: {result['error']}")
    else:
        st.success("Todo deleted successfully.")
        time.sleep(0.5)
        st.session_state.pop("todos_data", None)
        st.rerun()

def todos_page_content():
    st.title("🗒️ Todos")

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
                st.session_state.pop("todos_data", None)
                st.rerun()

    with col4:
        if st.button("Reset", use_container_width=True):
            st.session_state.todos_filters = {"complete": None, "search": None}
            st.session_state.pop("todos_data", None)
            st.rerun()

    # --- Fetch data ---
    st.divider()

    if "todos_data" not in st.session_state:
        with st.spinner("Loading todos..."):
            result = client.read_all_todos(**filters)
            if verify_error(result):
                return
            
            st.session_state["todos_data"] = result

    result = st.session_state["todos_data"]
    
    sub_col1, sub_col2 = st.columns([5, 1], vertical_alignment="bottom")
    with sub_col1:
        st.subheader(f"Todos : {len(result)}")
    with sub_col2:
        if st.button("Add", use_container_width=True):
            add_todo_dialog()

    if (not result) and (filters["complete"] is None) and (filters["search"] is None):
        st.info("No todos found. Add your first todo!")
    
    elif (not result) and (filters["complete"] is True):
        st.info("No completed todos found with the current filters.")
    
    elif (not result) and (filters["complete"] is False):
        st.info("Congratulations! You have no pending todos.")
    
    elif (not result) and (filters["search"] is not None):
        st.info("No todos match the search pattern.")

    # --- Display ---
    for i, todo in enumerate(result):
        
        extender_text = f"**{todo.get('title')}** - Priority: **{todo.get('priority')}**"
        extender_text += f" (ID: {todo.get('id')})"
        extender_icon = "✅" if todo.get('complete') is True else "⏳"
        
        with st.expander(extender_text, icon=extender_icon):
            st.write(f"**Description:** {todo.get('description')}")
            
            extender_col1, extender_col2 = st.columns(2, width=250)
            with extender_col1:
                if st.button("Edit", key=f"edit_{i}", width=100):
                    edit_todo_dialog(todo)
                
            with extender_col2:
                if st.button("Delete", key=f"delete_{i}", width=100):
                    delete_todo(todo)