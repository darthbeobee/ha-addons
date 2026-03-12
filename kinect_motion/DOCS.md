Kinect V2 Motion Watcher for Home Assistant

This is a custom Home Assistant OS Add-on that transforms a standard Xbox One Kinect (V2) into a highly sensitive, local-only MQTT motion sensor.

Unlike other Kinect implementations that require heavy GPU acceleration or full skeletal tracking, this add-on is heavily optimized for low-power hardware (like mini PCs or older All-In-Ones). It bypasses the massive 1080p RGB video feed and forces libfreenect2 into a CPU-only packet pipeline, analyzing raw infrared depth data to detect motion while saving massive amounts of USB bandwidth.
⚙️ Hardware Requirements

``  Home Assistant OS (Must have the Supervisor to run Add-ons).
    Xbox Kinect V2 with the Windows PC USB 3.0 Adapter.
    A dedicated USB 3.0 port. (The Kinect V2 uses massive USB bandwidth. Do not plug it into a USB hub).
    An MQTT Broker (like the official Mosquitto Add-on).

🚀 Installation

``  Navigate to your Home Assistant Settings > Add-ons.
    Click Add-on Store in the bottom right.
    Click the three dots (...) in the top right corner and select Repositories.
    Paste the URL of this GitHub repository and click Add.
    Close the popup, scroll down to find the new repository, and click Kinect V2 Motion Watcher.
    Click Install. (Note: This builds C++ drivers from source, so installation may take 10-20 minutes depending on your CPU).

🛠️ Configuration

Before starting the Add-on, go to the Configuration tab to set your variables:

``  MQTT Broker: Usually core-mosquitto if running the local HA add-on.
    MQTT User / Pass: Credentials for your MQTT broker.
    Sensitivity: How drastic the pixel change needs to be to trigger motion. Default is 100000000. Lower this number if it isn't picking you up; raise it if it is triggering on empty-room static.
    Cooldown: The number of seconds the room must be completely still before it sends the OFF signal.

🔗 Home Assistant Integration

Once the add-on is running, you need to create a sensor in Home Assistant to listen to it. Add this block to your configuration.yaml file and restart Home Assistant:
```
mqtt:
  binary_sensor:
    - name: "Kinect Motion"
      state_topic: "kinect/motion"
      payload_on: "ON"
      payload_off: "OFF"
      device_class: motion
```
      
   ⚠️ Troubleshooting

   The log is spammed with [DepthPacketStreamParser] XX packets were lost This is normal on lower-power machines. The Kinect blasts 30 frames per second of raw data. If your host machine's USB controller gets overwhelmed, it drops fragments of the data. The Python script is designed with a "Heartbeat" to push through this packet loss and will still trigger motion accurately even if the C++ drivers are complaining in the background. If it fails to connect entirely, ensure you are plugged directly into a blue USB 3.0 port (and not a USB hub).

   The Add-on hangs at Starting optimized motion script... This is a "Zombie USB" lock. If you restarted the Add-on while the camera was active, the host OS may not have released the USB port yet. Fix: Physically unplug the Kinect's USB cable from your server, wait 3 seconds, and plug it back in to force a reset.
 
   The log shows CRITICAL ERROR: /data/options.json not found You tried to start the Add-on before saving your settings. Fix: Go to the Configuration tab, type in your MQTT details, and hit Save (even if the default values are already there). Then go back and start the Add-on.

   The sensor is constantly stuck on "Detected" or never triggers Your threshold is likely fighting with the infrared static in your room.

   Fix: Look at the Add-on logs. When the room is completely empty, look at the Score: XXXXXXXX number being printed. Go to your Configuration tab and set the Sensitivity number slightly higher than that baseline static score.
