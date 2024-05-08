import base64
import json
from threading import Thread
from queue import Queue

from flask import Flask, request
from google.cloud import pubsub_v1
from testcontainers.google import PubSubContainer
from testcontainers.core.waiting_utils import wait_for_logs


def test_pubsub_container():
    """Assert that the TestContainer and PubSub spins up correctly."""
    with PubSubContainer() as pubsub:
        wait_for_logs(pubsub, r"Server started, listening on \d+", timeout=10)
        # Create a new topic
        publisher = pubsub.get_publisher_client()
        topic_path = publisher.topic_path(pubsub.project, "my-topic")
        publisher.create_topic(name=topic_path)

        # Create a subscription
        subscriber = pubsub.get_subscriber_client()
        subscription_path = subscriber.subscription_path(
            pubsub.project, "my-subscription"
        )
        subscriber.create_subscription(
            request={"name": subscription_path, "topic": topic_path}
        )

        # Publish a message
        publisher.publish(topic_path, b"Hello world!")

        # Receive the message
        queue = Queue()
        subscriber.subscribe(subscription_path, queue.put)
        message = queue.get(timeout=1)
        assert message.data == b"Hello world!"
        message.ack()


def helper_http_flask(msg_queue: Queue):
    """Run a full flask app in a thread.

    Message across threads via the Queue.
    """
    app = Flask("test-app")

    @app.route("/", methods=["POST"])
    def message():
        data = request.data
        msg_queue.put(data)
        print(data)
        return {}, 201

    thread = Thread(
        target=app.run, daemon=True, kwargs=dict(host="localhost", port=7777)
    )
    thread.start()

    return app


def test_pubsub_container_with_push():
    """Test the TestContainer.PubSub to a PUSH endpoint.

    Validate the testcontainer meets the integration testing needs.
    """
    msg_queue = Queue()
    helper_http_flask(msg_queue)

    endpoint = f"http://host.docker.internal:7777/"

    with PubSubContainer() as pubsub:
        wait_for_logs(pubsub, r"Server started, listening on \d+", timeout=10)

        # Create a new topic
        publisher = pubsub.get_publisher_client()
        topic_path = publisher.topic_path(pubsub.project, "my-topic")
        publisher.create_topic(name=topic_path)

        # Create a subscription
        push_config = pubsub_v1.types.PushConfig(push_endpoint=endpoint)
        subscriber = pubsub.get_subscriber_client()
        subscription_path = subscriber.subscription_path(
            pubsub.project, "my-subscription"
        )
        subscriber.create_subscription(
            request={
                "name": subscription_path,
                "topic": topic_path,
                "push_config": push_config,
            },
        )

        # Publish a message
        test_message = b"Hello world!"
        publisher.publish(topic_path, test_message)

        msg = msg_queue.get()

        envelope = json.loads(msg.decode())

        print(envelope)
        encoded_data = envelope.get("message", {}).get("data", None)

        data = base64.b64decode(encoded_data)

        assert data == test_message
