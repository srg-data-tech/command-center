import logging
import json

def process_observation(message_json):
    """Processes and extracts required fields for Observation."""

    resource_id = message_json.get("id", "Unknown")
    resource_type = message_json.get("resourceType", "Unknown")

    # Validate if code.coding.display contains "Weight KG"
    found_weight_kg = False
    for coding in message_json.get("code", {}).get("coding", []):
        if coding.get("display") == "Weight KG":
            found_weight_kg = True
            break

    if not found_weight_kg:
        logging.info(f" Discarding Observation message: 'Weight KG' code not found (id: {resource_id})")
        return None

    # Extract encounter reference
    encounter_reference = message_json.get("encounter", {}).get("reference", "")

    # Extract valueQuantity
    value_quantity = message_json.get("valueQuantity", {})

    # Construct the transformed JSON
    transformed_message = {
        "encounter": {"reference": encounter_reference},
        "id": resource_id,
        "resourceType": resource_type,
        "valueQuantity": {
            "unit": value_quantity.get("unit", ""),
            "value": value_quantity.get("value", 0.0)
        }
    }

    return transformed_message

