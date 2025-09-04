import json
import logging
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path

def _dict_to_xml(tag, d):
    """
    Recursively converts a dictionary to an XML element.
    Helper function for XML export.
    """
    elem = ET.Element(tag)
    for key, val in d.items():
        # Sanitize key for XML tag
        child_tag = ''.join(c if c.isalnum() else '_' for c in key.replace(' ', '_'))
        child_elem = ET.Element(child_tag)
        if isinstance(val, dict):
            child_elem.extend(_dict_to_xml(child_tag, val).getchildren())
        elif isinstance(val, list):
            for item in val:
                item_elem = ET.Element(f"{child_tag}_item")
                item_elem.text = str(item)
                child_elem.append(item_elem)
        else:
            child_elem.text = str(val)
        elem.append(child_elem)
    return elem

def export_schema(master_schema_path: str, output_dir: str):
    """
    Exports the master schema into multiple formats (XML, Excel).

    Args:
        master_schema_path (str): The path to the master JSON schema file.
        output_dir (str): The directory where the exported files will be saved.
    """
    logging.info(f"Reading master schema from '{master_schema_path}' for exporting.")

    try:
        with open(master_schema_path, 'r') as f:
            schema_data = json.load(f)

        output_dir_path = Path(output_dir)

        # --- Export to Excel ---
        excel_path = output_dir_path / "master_schema.xlsx"
        logging.info(f"Exporting schema to Excel at '{excel_path}'...")
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for category, content in schema_data.items():
                if category == 'metadata':
                    # Handle metadata separately, creating a simple key-value sheet
                    meta_list = [{'key': k, 'value': str(v)} for k, v in content.items()]
                    df = pd.DataFrame(meta_list)
                    df.to_excel(writer, sheet_name='Metadata', index=False)
                elif isinstance(content, dict) and content:
                    # Handle standard categories which are dicts of dicts
                    df_data = list(content.values())
                    df = pd.DataFrame(df_data)
                    df.to_excel(writer, sheet_name=category.capitalize(), index=False)
        logging.info("Successfully exported to Excel.")

        # --- Export to XML ---
        xml_path = output_dir_path / "master_schema.xml"
        logging.info(f"Exporting schema to XML at '{xml_path}'...")
        root = ET.Element("MasterSchema")

        for category, content in schema_data.items():
            cat_element = ET.Element(category)
            if isinstance(content, dict):
                for key, value in content.items():
                    # If the value is a dictionary, it's a standard field.
                    if isinstance(value, dict):
                        field_element = ET.Element("Field")
                        field_element.set("name", key)
                        desc_element = ET.Element("description")
                        desc_element.text = value.get("description", "")
                        field_element.append(desc_element)
                        cat_element.append(field_element)
                    # If the value is a list, it's something like 'source_files'.
                    elif isinstance(value, list):
                        list_element = ET.Element(key)  # e.g., <source_files>
                        for item in value:
                            item_element = ET.Element("item")
                            item_element.text = str(item)
                            list_element.append(item_element)
                        cat_element.append(list_element)
            root.append(cat_element)

        # Pretty print the XML
        xml_str = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(xml_str)
        pretty_xml_str = reparsed.toprettyxml(indent="  ")

        with open(xml_path, 'w') as f:
            f.write(pretty_xml_str)
        logging.info("Successfully exported to XML.")

    except FileNotFoundError:
        logging.error(f"Master schema file not found at '{master_schema_path}'.")
        raise
    except Exception as e:
        logging.error(f"An error occurred during schema export. Error: {e}")
        raise
