import streamlit as st
import json
import difflib
from typing import Dict, Any, Tuple, Optional
import pandas as pd

st.set_page_config(
    page_title="JSON Comparison Tool",
    page_icon="🔍",
    layout="wide"
)

def parse_json_file(uploaded_file) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Parse a JSON file and return the data or an error message."""
    if uploaded_file is None:
        return None, None
    
    try:
        content = uploaded_file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        data = json.loads(content)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON format: {str(e)}"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"

def find_differences(json1: Dict[str, Any], json2: Dict[str, Any]) -> Dict[str, Any]:
    """Find differences between two JSON objects and return a difference summary."""
    differences = {}
    
    # Convert both JSONs to sorted string format for comparison
    json1_str = json.dumps(json1, sort_keys=True, indent=2).splitlines()
    json2_str = json.dumps(json2, sort_keys=True, indent=2).splitlines()
    
    # Get differences using difflib
    diff = list(difflib.unified_diff(json1_str, json2_str, n=0))
    
    # Remove the headers (first two lines)
    if len(diff) > 2:
        diff = diff[2:]
    
    # Organize differences
    added = [line[1:] for line in diff if line.startswith('+')]
    removed = [line[1:] for line in diff if line.startswith('-')]
    
    differences["added_to_json2"] = added
    differences["removed_from_json1"] = removed
    
    # Also include a count of differences
    differences["total_changes"] = len(added) + len(removed)
    
    return differences

def display_json(data: Dict[str, Any], title: str):
    """Display JSON data in a formatted way with copy button."""
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
    st.markdown("""
    Upload two JSON files to compare their contents and see the differences.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Upload first JSON file")
        file1 = st.file_uploader("Choose the first JSON file", type=["json"], key="file1")
    
    with col2:
        st.markdown("### Upload second JSON file")
        file2 = st.file_uploader("Choose the second JSON file", type=["json"], key="file2")
    
    # Parse the uploaded files
    json1, error1 = parse_json_file(file1)
    json2, error2 = parse_json_file(file2)
    
    # Handle errors
    if error1:
        st.error(f"Error in first file: {error1}")
    if error2:
        st.error(f"Error in second file: {error2}")
    
    # If both files are uploaded and parsed correctly, compare them
    if json1 is not None and json2 is not None:
        st.success("Both files uploaded successfully!")
        
        tab1, tab2, tab3 = st.tabs(["Differences", "JSON 1", "JSON 2"])
        
        with tab1:
            differences = find_differences(json1, json2)
            display_differences(differences)
        
        with tab2:
            display_json(json1, "JSON 1 Content")
        
        with tab3:
            display_json(json2, "JSON 2 Content")
        
        # Option to download comparison report
        if st.button("Generate Comparison Report"):
            report = {
                "total_changes": differences["total_changes"],
                "additions": differences["added_to_json2"],
                "removals": differences["removed_from_json1"]
            }
            report_str = json.dumps(report, indent=2)
            st.download_button(
                label="Download Report",
                data=report_str,
                file_name="json_comparison_report.json",
                mime="application/json"
            )
    # Add footer
    st.markdown("---")
    st.markdown("Made by [Yahia Eldow](https://www.yahia-eldow.com)", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

