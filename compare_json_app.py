import streamlit as st
import json
from typing import Any, Dict, Optional, Tuple

st.set_page_config(
    page_title="JSON Comparison Tool",
    page_icon="🔍",
    layout="wide"
)

# Example JSON data
EXAMPLE_JSON_1 = ""

EXAMPLE_JSON_2 = ""

def reset_inputs():
    """Clear all inputs and session state"""
    st.session_state.json1_input = ""
    st.session_state.json2_input = ""
    st.rerun()

def parse_json_content(content: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Parse JSON content and return the data or an error message."""
    if not content:
        return None, None
    
    try:
        data = json.loads(content)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON format: {str(e)}"
    except Exception as e:
        return None, f"Error parsing JSON: {str(e)}"

def parse_json_file(uploaded_file) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Parse a JSON file and return the data or an error message."""
    if uploaded_file is None:
        return None, None
    
    try:
        content = uploaded_file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        return parse_json_content(content)
    except Exception as e:
        return None, f"Error reading file: {str(e)}"

def deep_diff(obj1: Any, obj2: Any, path: str = "") -> Tuple[list, list, list]:
    """
    Recursively diff two JSON values.
    Returns (added_keys, removed_keys, changed_values).
    - added_keys: paths present in obj2 but not obj1
    - removed_keys: paths present in obj1 but not obj2
    - changed_values: list of dicts {path, old, new} where leaf values differ
    """
    added_keys: list = []
    removed_keys: list = []
    changed_values: list = []

    if isinstance(obj1, dict) and isinstance(obj2, dict):
        all_keys = sorted(set(obj1.keys()) | set(obj2.keys()))
        for key in all_keys:
            full_path = f"{path}.{key}" if path else key
            if key not in obj1:
                added_keys.append(full_path)
            elif key not in obj2:
                removed_keys.append(full_path)
            else:
                a, r, c = deep_diff(obj1[key], obj2[key], full_path)
                added_keys.extend(a)
                removed_keys.extend(r)
                changed_values.extend(c)

    elif isinstance(obj1, list) and isinstance(obj2, list):
        for i in range(max(len(obj1), len(obj2))):
            full_path = f"{path}[{i}]"
            if i >= len(obj1):
                added_keys.append(full_path)
            elif i >= len(obj2):
                removed_keys.append(full_path)
            else:
                a, r, c = deep_diff(obj1[i], obj2[i], full_path)
                added_keys.extend(a)
                removed_keys.extend(r)
                changed_values.extend(c)

    else:
        if obj1 != obj2:
            changed_values.append({"path": path or "(root)", "old": obj1, "new": obj2})

    return added_keys, removed_keys, changed_values

def display_json(data: Dict[str, Any], title: str):
    """Display JSON data in a formatted way."""
    st.subheader(title)
    json_str = json.dumps(data, indent=2)
    st.code(json_str, language="json")

def display_differences(added_keys: list, removed_keys: list, changed_values: list, mode: str):
    """Display the differences based on comparison mode."""
    st.subheader("Differences")

    show_keys = mode in ("Full", "Keys & Structure Only")
    show_values = mode in ("Full", "Values Only")

    visible_count = (
        (len(added_keys) + len(removed_keys)) if show_keys else 0
    ) + (len(changed_values) if show_values else 0)

    st.metric("Total Changes", visible_count)

    if show_keys:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Keys Added in JSON 2")
            if added_keys:
                for path in added_keys:
                    st.code("+ " + path, language="diff")
            else:
                st.info("No keys added.")
        with col2:
            st.markdown("### Keys Removed from JSON 1")
            if removed_keys:
                for path in removed_keys:
                    st.code("- " + path, language="diff")
            else:
                st.info("No keys removed.")

    if show_values:
        st.markdown("### Value Changes")
        if changed_values:
            for change in changed_values:
                st.markdown(f"**`{change['path']}`**")
                c1, c2 = st.columns(2)
                with c1:
                    st.code(f"- {json.dumps(change['old'])}", language="diff")
                with c2:
                    st.code(f"+ {json.dumps(change['new'])}", language="diff")
        else:
            st.info("No value changes found.")

    if visible_count == 0:
        st.success("No differences found for the selected comparison mode.")

def main():
    st.title("JSON Comparison Tool")
    st.markdown("Compare JSON files or directly paste JSON content to see the differences.")
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ("File Upload", "Direct Input"),
        horizontal=True
    )
    
    # Action buttons row - Load Examples always shown
    col1, col2 = st.columns([1,1])
    # with col1:
        # if st.button("Load Example JSONs"):
        #     st.session_state.json1_input = json.dumps(EXAMPLE_JSON_1, indent=2)
        #     st.session_state.json2_input = json.dumps(EXAMPLE_JSON_2, indent=2)
        #     st.success("Example JSONs loaded!")
        #     st.rerun()
    
    # Only show Reset button in Direct Input mode
    if input_method == "Direct Input":
        with col2:
            if st.button("Reset All", type="secondary"):
                reset_inputs()
    
    if input_method == "File Upload":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Upload first JSON file")
            file1 = st.file_uploader("Choose the first JSON file", type=["json"], key="file1")
        with col2:
            st.markdown("### Upload second JSON file")
            file2 = st.file_uploader("Choose the second JSON file", type=["json"], key="file2")
        
        json1, error1 = parse_json_file(file1)
        json2, error2 = parse_json_file(file2)
        
        if error1:
            st.error(f"Error in first file: {error1}")
        if error2:
            st.error(f"Error in second file: {error2}")
    
    else:  # Direct Input
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### First JSON Content")
            json1_input = st.text_area(
                "Paste first JSON here", 
                height=200, 
                key="json1_input",
                value=st.session_state.get("json1_input", "")
            )
        with col2:
            st.markdown("### Second JSON Content")
            json2_input = st.text_area(
                "Paste second JSON here", 
                height=200, 
                key="json2_input",
                value=st.session_state.get("json2_input", "")
            )
        
        json1, error1 = parse_json_content(json1_input)
        json2, error2 = parse_json_content(json2_input)
        
        if error1:
            st.error(f"Error in first JSON: {error1}")
        if error2:
            st.error(f"Error in second JSON: {error2}")
    
    # Comparison mode selector
    st.markdown("### Comparison Mode")
    comparison_mode = st.radio(
        "What to compare:",
        ("Full", "Keys & Structure Only", "Values Only"),
        horizontal=True,
        help=(
            "**Full** – report added/removed keys AND changed values.\n\n"
            "**Keys & Structure Only** – only report keys added or removed (ignore value changes).\n\n"
            "**Values Only** – only report value changes for keys that exist in both JSONs."
        )
    )

    # Compare button
    if st.button("Compare JSONs", type="primary"):
        if json1 is not None and json2 is not None:
            st.success("Comparison results:")

            added_keys, removed_keys, changed_values = deep_diff(json1, json2)

            tab1, tab2, tab3 = st.tabs(["Differences", "JSON 1", "JSON 2"])

            with tab1:
                display_differences(added_keys, removed_keys, changed_values, comparison_mode)

            with tab2:
                display_json(json1, "JSON 1 Content")

            with tab3:
                display_json(json2, "JSON 2 Content")

            report = {
                "comparison_mode": comparison_mode,
                "added_keys": added_keys,
                "removed_keys": removed_keys,
                "changed_values": changed_values,
            }
            st.download_button(
                label="Download Report",
                data=json.dumps(report, indent=2),
                file_name="json_comparison_report.json",
                mime="application/json"
            )
        else:
            st.warning("Please provide valid JSON content in both inputs to compare.")
    
    st.markdown("---")
    st.markdown("Made by [Yahia Eldow](https://www.yahia-eldow.com)", unsafe_allow_html=True)

if __name__ == "__main__":
    main()