#!/bin/bash
echo "Starting Kinect V2 Motion Watcher..."
echo "Waiting for Mosquitto to be ready..."
sleep 5
python3 -u /app/motion.py
