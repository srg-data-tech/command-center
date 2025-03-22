import os
import base64
import json
import logging
from flask import Flask, request
from google.cloud import pubsub_v1

import patient
import location
import encounter
import observation
import delete_resource

app = Flask(__name__)

PROJECT_ID = "certain-haiku-443118-n2"

TOPICS = {
    "Patient": "cc-patient-dest",
    "Location": "cc-location-dest",
    "Encounter": "cc-encounter-dest",
    "Observation": "cc-observation-dest",
    "DeleteResource": "cc-delete-resource-dest"  # New topic for DeleteResource messages
}

INVALID_MESSAGES_TOPIC = "invalid-messages"

publisher = pubsub_v1.PublisherClient()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.route("/", methods=["POST"])
def pubsub_handler():
    """Handles incoming Pub/Sub messages and routes them to the correct processor."""
    
    envelope = request.get_json(silent=True)
    if not envelope or "message" not in envelope:
        logging.error("Received invalid message - Failed to process - Sent to invalid messages topic")
        publish_invalid_message(envelope)
        return ("Invalid Pub/Sub message format", 200)

    pubsub_msg = envelope["message"]
    data = pubsub_msg.get("data")

    if not data:
        logging.error("Received invalid message - Failed to process - Sent to invalid messages topic")
        publish_invalid_message(pubsub_msg)
        return ("OK", 200)

    try:
        message_text = base64.b64decode(data).decode("utf-8")
        if not message_text.strip():
            logging.error("Received invalid message - Failed to process - Sent to invalid messages topic")
            publish_invalid_message(pubsub_msg)
            return ("OK", 200)

        message_json = json.loads(message_text)
    except Exception as e:
        logging.error(f"Received invalid message - Failed to process ({str(e)}) - Sent to invalid messages topic")
        publish_invalid_message(pubsub_msg)
        return ("OK", 200)

    # Extract action from attributes
    action = message_json.get("attributes", {}).get("action", "Unknown")
    logging.info(f"Received message: action: {action}")

    # Handle DeleteResource Messages
    if action == "DeleteResource":
        transformed_message = delete_resource.process_delete_resource(message_json)
        if transformed_message:
            publish_to_topic("DeleteResource", transformed_message)
        else:
            logging.error("DeleteResource message failed to process - Sent to invalid-messages topic")
            publish_invalid_message(message_json)
        return ("OK", 200)

    # If the action is UpdateResource or CreateResource, send directly to invalid-messages
    if action in ["UpdateResource", "CreateResource"]:
        logging.error(f"Unhandled {action} - Sent to invalid-messages topic")
        publish_invalid_message(message_json)
        return ("OK", 200)

    # Continue processing resourceType as before
    resource_type = message_json.get("resourceType", "Unknown")
    resource_id = message_json.get("id", "Unknown")

    logging.info(f"Received message: resourceType: {resource_type}, id: {resource_id}")

    transformed_message = None
    if resource_type == "Patient":
        transformed_message = patient.process_patient(message_json)
    elif resource_type == "Location":
        transformed_message = location.process_location(message_json)
    elif resource_type == "Encounter":
        transformed_message = encounter.process_encounter(message_json)
    elif resource_type == "Observation":
        transformed_message = observation.process_observation(message_json)

    if transformed_message:
        publish_to_topic(resource_type, transformed_message)
    else:
        logging.warning(f"Transformation failed for {resource_type} - Message not published")

    return ("OK", 200)


def publish_to_topic(resource_type, message):
    """Publishes transformed messages to the appropriate topic."""
    destination_topic = TOPICS.get(resource_type)
    if not destination_topic:
        logging.error(f"No topic found for resourceType: {resource_type}")
        return

    topic_path = publisher.topic_path(PROJECT_ID, destination_topic)
    transformed_data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, transformed_data)
    logging.info(f"Processed and sent: resourceType: {resource_type} to {destination_topic}")
    logging.info(f"Message successfully published with ID: {future.result()}")


def publish_invalid_message(message_data):
    """Publishes invalid messages to the 'invalid-messages' topic in their original format."""
    invalid_topic_path = publisher.topic_path(PROJECT_ID, INVALID_MESSAGES_TOPIC)

    if isinstance(message_data, str):
        transformed_data = message_data.encode("utf-8")
    else:
        transformed_data = json.dumps(message_data).encode("utf-8")

    future = publisher.publish(invalid_topic_path, transformed_data)
    logging.info(f"Invalid message published to {INVALID_MESSAGES_TOPIC}")
    return future.result()
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    app.run(debug=True, host="0.0.0.0", port=port)

