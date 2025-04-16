# from flask import Flask, Blueprint, render_template, jsonify
# import paho.mqtt.client as mqtt
# import os
# from database.database import SessionLocal, Base, engine
# from database import models
# import json
# from datetime import datetime, timedelta
# from sqlalchemy import extract, func, distinct
# import locale
# from .auth import auth as auth_blueprint

# locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

# MQTT_BROKER = "broker.emqx.io"
# MQTT_PORT = 1883
# MQTT_TOPIC = "flask/test"

# client = mqtt.Client()

# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code " + str(rc))
#     client.subscribe(MQTT_TOPIC)

# def on_message(client, userdata, msg):
#     print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

# client.on_connect = on_connect
# client.on_message = on_message
# client.connect(MQTT_BROKER, MQTT_PORT, 60)
# client.loop_start()

# """PAGES ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"""



# """API +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"""


# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     SessionLocal.remove()

# if __name__ == "__main__":
#     init_db()
#     port = int(os.environ.get('PORT', 5000))
#     app.run(debug=True, host='0.0.0.0', port=port)
