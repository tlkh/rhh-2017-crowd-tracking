# RHH 2017 Camera-based Crowd Tracking

Red Hat Hackathon Singapore 2017 Camera-based Crowd Tracking Solution

First place, but shitty code. It's hacked together after all.

Documentation may or may not come along. The code may not work on your setup. 

Important bits:
- camera_test.py: use Pi camera to do real-time tracking
- local_test.py: test using a video file


Other bits:
- heatmap.py: generate a heatmap from a log file generated for any of the above
- app.py: web interface, doesn't quite work
- MicOutSerial: Arduino code to upload noise data over MQTT