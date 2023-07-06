import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def extract_fields(schema, prefix=''):
    fields = []

    if isinstance(schema, dict):
        for key, value in schema.items():
            field_name = f'{prefix}.{key}' if prefix else key
            field_type = extract_fields(value, prefix=field_name)
            fields.extend(field_type)
    elif isinstance(schema, list):
        for item in schema:
            field_type = extract_fields(item, prefix=prefix)
            fields.extend(field_type)
    else:
        fields.append({'name': prefix, 'type': type(schema).__name__})

    return fields

def extract_fields_from_json(json_content):
    try:
        json_data = json.loads(json_content)
        return extract_fields(json_data)
    except json.JSONDecodeError as e:
        print(f'Errore durante il parsing del file JSON: {e}')
        return None

def extract_element_names_and_types(xsd_content):
    elements = []

    def process_element(element, prefix=''):
        element_name = f'{prefix}.{element.get("name")}' if prefix else element.get("name")
        element_type = element.get("type")
        elements.append({'name': element_name, 'type': element_type})

        for child_element in element.find_all("element"):
            process_element(child_element, prefix=element_name)

    try:
        soup = BeautifulSoup(xsd_content, features="xml")
        for element in soup.find_all("element"):
            process_element(element)

        fields = elements 
        return elements
    except Exception as e:
        print(f'Errore durante il parsing del file XSD: {e}')
        return None


