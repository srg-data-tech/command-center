import logging
import json

def process_encounter(message_json):
    """Processes and extracts required fields for Encounter."""

    resource_id = message_json.get("id", "Unknown")
    resource_type = message_json.get("resourceType", "Unknown")

    # Extract identifier list
    identifier_list = []
    for identifier in message_json.get("identifier", []):
        system = identifier.get("system", "")
        value = identifier.get("value", "")
        if system and value:
            identifier_list.append({"system": system, "value": value})

    # Extract location list without unnested key-value pairs
    location_list = message_json.get("location", [])

    # Extract subject reference
    subject_reference = message_json.get("subject", {}).get("reference", "")

    # Construct the transformed JSON
    transformed_message = {
        "id": resource_id,
        "identifier": identifier_list,
        "location": location_list,  # Keeping all key-value pairs as-is
        "resourceType": resource_type,
        "subject": {"reference": subject_reference}
    }

    return transformed_message

