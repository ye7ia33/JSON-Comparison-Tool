import streamlit as st
import json
import difflib
from typing import Dict, Any, Tuple, Optional

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

def find_differences(json1: Dict[str, Any], json2: Dict[str, Any]) -> Dict[str, Any]:
    """Find differences between two JSON objects and return a difference summary."""
    differences = {}
    json1_str = json.dumps(json1, sort_keys=True, indent=2).splitlines()
    json2_str = json.dumps(json2, sort_keys=True, indent=2).splitlines()
    diff = list(difflib.unified_diff(json1_str, json2_str, n=0))
    
    if len(diff) > 2:
        diff = diff[2:]
    
    added = [line[1:] for line in diff if line.startswith('+')]
    removed = [line[1:] for line in diff if line.startswith('-')]
    
    differences["added_to_json2"] = added
    differences["removed_from_json1"] = removed
    differences["total_changes"] = len(added) + len(removed)
    
    return differences

def display_json(data: Dict[str, Any], title: str):
    """Display JSON data in a formatted way."""
    st.subheader(title)
    json_str = json.dumps(data, indent=2)
    st.code(json_str, language="json")

def display_differences(differences: Dict[str, Any]):
    """Display the differences between two JSON files."""
    st.subheader("Differences")
    st.metric("Total Changes", differences["total_changes"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Additions to JSON 2")
        if differences["added_to_json2"]:
            for line in differences["added_to_json2"]:
                st.code("+ " + line, language="diff")
        else:
            st.info("No additions found.")
    
    with col2:
        st.markdown("### Removals from JSON 1")
        if differences["removed_from_json1"]:
            for line in differences["removed_from_json1"]:
                st.code("- " + line, language="diff")
        else:
            st.info("No removals found.")

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
    
    # Compare button
    if st.button("Compare JSONs", type="primary"):
        if json1 is not None and json2 is not None:
            st.success("Comparison results:")
            
            tab1, tab2, tab3 = st.tabs(["Differences", "JSON 1", "JSON 2"])
            
            with tab1:
                differences = find_differences(json1, json2)
                display_differences(differences)
            
            with tab2:
                display_json(json1, "JSON 1 Content")
            
            with tab3:
                display_json(json2, "JSON 2 Content")
            
            if st.button("Generate Comparison Report"):
                report = {
                    "total_changes": differences["total_changes"],
                    "additions": differences["added_to_json2"],
                    "removals": differences["removed_from_json1"]
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