import logging
import base64
import json

def process_delete_resource(message_json):
    """Processes DeleteResource messages and extracts necessary fields."""

    try:
        attributes = message_json.get("attributes", {})
        action = attributes.get("action", "Unknown")
        last_updated_time = attributes.get("lastUpdatedTime", "Unknown")
        resource_type = attributes.get("resourceType", "Unknown")

        # Decode the 'data' field to extract the ID
        encoded_data = message_json.get("data", "")
        decoded_id = base64.b64decode(encoded_data).decode("utf-8") if encoded_data else "Unknown"

        # Extract only the last part of the ID
        id_value = decoded_id.split("/")[-1] if "/" in decoded_id else decoded_id

        # Construct transformed message
        transformed_message = {
            "action": action,
            "lastUpdatedTime": last_updated_time,
            "resourceType": resource_type,
            "id": id_value
        }

        logging.info(f"Processed DeleteResource message: {transformed_message}")
        return transformed_message

    except Exception as e:
        logging.error(f"Error processing DeleteResource message: {str(e)}")
        return None
