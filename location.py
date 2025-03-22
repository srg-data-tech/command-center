import logging
import json

def process_location(message_json):
    """Processes and extracts required fields for Location."""

    resource_id = message_json.get("id", "Unknown")
    resource_type = message_json.get("resourceType", "Unknown")
    name = message_json.get("name", "Unknown")

    # Discard message if name is "unknown"
    if name.lower() == "unknown":
        logging.info(f" Discarding Location message: Name is 'unknown' (id: {resource_id})")
        return None

    # Extract "code" from physicalType.coding.code
    code = ""
    if "physicalType" in message_json and "coding" in message_json["physicalType"]:
        for coding in message_json["physicalType"]["coding"]:
            if "code" in coding:
                code = coding["code"]
                break  # Take the first available code

    # Construct the transformed JSON
    transformed_message = {
        "id": resource_id,
        "name": name,
        "code": code,
        "resourceType": resource_type
    }

    return transformed_message

