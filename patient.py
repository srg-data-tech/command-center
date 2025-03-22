import logging
import json

def process_patient(message_json):
    """Extracts required fields only if the message meets validation criteria for Patient."""
    
    resource_type = message_json.get("resourceType", "Unknown")
    resource_id = message_json.get("id", "Unknown")

    # Validate Identifier (MRN)
    mrn_value = None
    for identifier in message_json.get("identifier", []):
        if identifier.get("system") == "Clarian MRN":
            mrn_value = identifier.get("value")
            break

    if not mrn_value:
        logging.info(f" Discarding Patient message: No valid MRN found (id: {resource_id})")
        return None

    # Validate Name (Official Use)
    official_name = None
    for name_entry in message_json.get("name", []):
        if name_entry.get("use") == "official":
            official_name = name_entry.get("text")
            break

    if not official_name:
        logging.info(f" Discarding Patient message: No official name found (id: {resource_id})")
        return None

    # Construct transformed JSON
    transformed_message = {
        "birthDate": message_json.get("birthDate", ""),
        "gender": message_json.get("gender", ""),
        "id": resource_id,
        "MRN": mrn_value,
        "name": official_name,
        "resourceType": resource_type
    }

    return transformed_message
