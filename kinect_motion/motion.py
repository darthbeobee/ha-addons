import time
import sys
import json
import numpy as np
import paho.mqtt.client as mqtt
from pylibfreenect2 import Freenect2, SyncMultiFrameListener, FrameType, CpuPacketPipeline

print("Loading configuration...", flush=True)

# --- LOAD CONFIGURATION FROM HOME ASSISTANT UI ---
try:
    with open('/data/options.json') as f:
        config = json.load(f)
        
    MQTT_BROKER = config.get("mqtt_broker", "core-mosquitto")
    MQTT_PORT = int(config.get("mqtt_port", 1883))
    MQTT_USER = config.get("mqtt_user", "")
    MQTT_PASS = config.get("mqtt_pass", "")
    SENSITIVITY_THRESHOLD = int(config.get("sensitivity", 100000000))
    COOLDOWN_SECONDS = int(config.get("cooldown", 5))
    
except Exception as e:
    print(f"CRITICAL ERROR loading options: {e}. Did you hit Save in the Configuration tab?", flush=True)
    sys.exit(1)

MQTT_TOPIC = "kinect/motion"
print("Starting optimized motion script...", flush=True)

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}", flush=True)

# Setup MQTT (with a fix for the Deprecation Warning)
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
except AttributeError:
    client = mqtt.Client() 

if MQTT_USER and MQTT_PASS:
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    
client.on_connect = on_connect
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# 1. FORCE THE KINECT INTO LOW-POWER CPU MODE
pipeline = CpuPacketPipeline()
fn = Freenect2()
num_devices = fn.enumerateDevices()
if num_devices == 0:
    print("No Kinect V2 found! Check your USB connection.", flush=True)
    sys.exit(1)

serial = fn.getDeviceSerialNumber(0)
device = fn.openDevice(serial, pipeline=pipeline)

# 2. SEVER THE RGB VIDEO FEED
listener = SyncMultiFrameListener(FrameType.Depth)
device.setIrAndDepthFrameListener(listener)

device.start()
print("Kinect initialized. Watching for motion...", flush=True)

previous_frame = None
last_motion_time = 0
frame_count = 0

try:
    while True:
        frames = listener.waitForNewFrame()
        depth_frame = frames["depth"]
        
        current_frame = depth_frame.asarray()

        frame_count += 1
        if frame_count % 30 == 0:
            print("Heartbeat: Processing frames... (Lost packet warnings above are normal)", flush=True)

        if previous_frame is not None:
            diff = np.sum(np.abs(current_frame - previous_frame))
            
            if diff > SENSITIVITY_THRESHOLD:
                if time.time() - last_motion_time > COOLDOWN_SECONDS:
                    print(f"MOTION DETECTED! (Score: {diff})", flush=True)
                    client.publish(MQTT_TOPIC, "ON")
                    last_motion_time = time.time()
            else:
                if time.time() - last_motion_time > COOLDOWN_SECONDS:
                    client.publish(MQTT_TOPIC, "OFF")

        previous_frame = np.copy(current_frame)
        listener.release(frames)
        
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Stopping...", flush=True)
except Exception as e:
    print(f"CRITICAL ERROR in frame loop: {e}", flush=True)

device.stop()
device.close()
client.loop_stop()
