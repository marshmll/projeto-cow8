import random
import time
import logging
import json
import hashlib
from datetime import datetime
from collections import deque
from threading import Lock

import paho.mqtt.client as mqtt

# MQTT reconnect parameters
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60
DUPLICATE_TTL = 300  # 5 minutes
SHORT_DUPLICATE_WINDOW = 5  # seconds

class MQTTClient:
    def __init__(self):
        self._client = None
        self._lock = Lock()
        self._is_connected = False
        self._pending_subscriptions = []
        self._subscribed_topics = set()
        self._listener_callbacks = []
        self._logger = logging.getLogger(__name__)

        self._message_history = deque()
        self._message_index = {}
        self._last_cleanup = time.time()

    def _fingerprint(self, topic, payload):
        try:
            # Try decoding payload as JSON and sorting keys to ensure consistency
            parsed = json.loads(payload.decode() if isinstance(payload, bytes) else payload)
            normalized_payload = json.dumps(parsed, sort_keys=True, separators=(',', ':'))
        except Exception:
            # Fallback to raw payload string if not JSON
            normalized_payload = payload.decode() if isinstance(payload, bytes) else str(payload)

        data = f"{topic}:{normalized_payload}".encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    def _cleanup_history(self):
        now = time.time()
        while self._message_history and now - self._message_history[0][1] > DUPLICATE_TTL:
            old_fp, _ = self._message_history.popleft()
            self._message_index.pop(old_fp, None)
        self._last_cleanup = now

    def _subscribe_internal(self, topic, qos):
        try:
            result, _ = self._client.subscribe(topic, qos)
            self._logger.info(f"Subscribed to {topic} with QoS {qos}")
            return result == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            self._logger.error(f"Failed to subscribe to {topic}: {e}")
            return False

    def _handle_message(self, topic, payload):
        for handler in self._listener_callbacks:
            if handler['topic'] == topic:
                handler['callback'](self._logger, payload)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self._is_connected = True
            self._subscribed_topics.clear()
            self._logger.info("Connected to MQTT Broker")
            # self._client.publish('cow8/status', f'Connected at {datetime.now()}')

            for topic, qos in self._pending_subscriptions:
                if self._subscribe_internal(topic, qos):
                    self._subscribed_topics.add(topic)
            self._pending_subscriptions.clear()
        else:
            self._logger.error(f"Connect failed: {reason_code}")

    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        self._is_connected = False
        self._logger.warning(f"Disconnected: {reason_code}")

        reconnect_count, delay = 0, FIRST_RECONNECT_DELAY
        while reconnect_count < MAX_RECONNECT_COUNT:
            self._logger.info(f"Reconnecting in {delay}s...")
            time.sleep(delay)
            try:
                client.reconnect()
                self._logger.info("Reconnected successfully")
                return
            except Exception as e:
                self._logger.error(f"Reconnect failed: {e}")
            delay = min(delay * RECONNECT_RATE, MAX_RECONNECT_DELAY)
            reconnect_count += 1
        self._logger.error("Giving up after max reconnect attempts")

    def on_message(self, client, userdata, msg):
        with self._lock:
            now = time.time()
            if now - self._last_cleanup > 60:
                self._cleanup_history()

            fp = self._fingerprint(msg.topic, msg.payload)
            last_seen = self._message_index.get(fp)

            if last_seen and now - last_seen < SHORT_DUPLICATE_WINDOW:
                self._logger.debug(f"Ignoring duplicate: {msg.topic}")
                return

            self._message_index[fp] = now
            self._message_history.append((fp, now))

        self._logger.debug(f"New message on {msg.topic}: {msg.payload}")
        self._handle_message(msg.topic, msg.payload)

    def on_subscribe(self, client, userdata, mid, reason_codes, properties):
        self._logger.info(f"Subscription confirmed (MID: {mid})")

    def connect(self, broker='broker.emqx.io', port=1883, retries=3, delay=2):
        with self._lock:
            if self._client and self._is_connected:
                return True

            for attempt in range(retries):
                try:
                    client_id = f'flask-app-{random.randint(0, 1000)}'
                    self._client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
                    self._client.on_connect = self.on_connect
                    self._client.on_disconnect = self.on_disconnect
                    self._client.on_message = self.on_message
                    self._client.on_subscribe = self.on_subscribe

                    self._client.connect(broker, port, keepalive=60)
                    self._client.loop_start()
                    return True
                except Exception as e:
                    self._logger.warning(f"Connect attempt {attempt + 1} failed: {e}")
                    time.sleep(delay)

            self._client = None
            return False

    def disconnect(self):
        with self._lock:
            if self._client:
                try:
                    self._client.loop_stop()
                    self._client.disconnect()
                except Exception as e:
                    self._logger.error(f"Disconnect error: {e}")
                finally:
                    self._client = None
                    self._is_connected = False

    def subscribe(self, topic, qos=0):
        with self._lock:
            if topic in self._subscribed_topics:
                self._logger.debug(f"Already subscribed to {topic}")
                return True

            if self._is_connected:
                if self._subscribe_internal(topic, qos):
                    self._subscribed_topics.add(topic)
                    return True
                return False
            else:
                self._pending_subscriptions.append((topic, qos))
                return True


    def publish(self, topic, payload=None, qos=0, retain=False):
        """
        Publish a message to an MQTT topic.
        
        Args:
            topic (str): The topic to publish to
            payload (str/bytes/dict, optional): The message payload. If dict, will be JSON serialized.
            qos (int, optional): Quality of Service level (0, 1, or 2)
            retain (bool, optional): Whether the message should be retained
        
        Returns:
            tuple: (success: bool, message_id: int or None)
        """
        with self._lock:
            if not self._is_connected or not self._client:
                self._logger.warning(f"Not connected, cannot publish to {topic}")
                return False, None

            try:
                # Handle different payload types
                if payload is None:
                    payload = ""
                elif isinstance(payload, dict):
                    payload = json.dumps(payload)
                elif not isinstance(payload, (str, bytes)):
                    payload = str(payload)

                # Convert to bytes if not already
                if isinstance(payload, str):
                    payload = payload.encode('utf-8')

                # Check for duplicate publication
                fp = self._fingerprint(topic, payload)
                now = time.time()
                if fp in self._message_index and now - self._message_index[fp] < SHORT_DUPLICATE_WINDOW:
                    self._logger.debug(f"Skipping duplicate publish to {topic}")
                    return True, None  # Consider it successful but didn't actually send

                # Actually publish the message
                info = self._client.publish(topic, payload, qos=qos, retain=retain)
                
                if info.rc == mqtt.MQTT_ERR_SUCCESS:
                    self._logger.debug(f"Published to {topic} (QoS: {qos}, Retain: {retain})")
                    # Track this message to avoid processing our own publications
                    self._message_index[fp] = now
                    self._message_history.append((fp, now))
                    return True, info.mid
                else:
                    self._logger.error(f"Publish failed to {topic} with error code {info.rc}")
                    return False, info.mid

            except Exception as e:
                self._logger.error(f"Error publishing to {topic}: {e}")
                return False, None


    def add_listener_on_topic(self, uid, topic, callback):
        existing = [h for h in self._listener_callbacks if h['topic'] == topic]
        if any(h['uid'] == uid and h['topic'] == topic for h in existing):
            return False
        if existing:
            self._logger.warning(f"Multiple listeners on topic '{topic}'. Existing: {[h['uid'] for h in existing]}, New: {uid}")
        self._listener_callbacks.append({'uid': uid, 'topic': topic, 'callback': callback})
        self.subscribe(topic)
        return True


    def remove_listener(self, uid):
        self._listener_callbacks = [h for h in self._listener_callbacks if h['uid'] != uid]

    def get_client(self):
        with self._lock:
            return self._client if self._is_connected else None

    def is_connected(self):
        with self._lock:
            return self._is_connected
