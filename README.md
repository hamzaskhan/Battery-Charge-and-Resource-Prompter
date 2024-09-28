# Battery-Charge-and-Resource-Prompter
Overcharging a battery beyond 80% can hurt its lifespan, and it's easy to forget to unplug while busy. This program provides timely reminders when the battery reaches this threshold. It also monitors CPU usage, memory consumption, and disk storage, ensuring optimal performance and alerting users to any potential issues.

It's a good idea to convert it into a .exe file and use it like any other application ;)

################### Features

Battery Monitoring Real-time Battery Status: Monitors battery percentage and charging status continuously. Alerts for High Battery Levels: Notifies users when the battery exceeds 80% while charging, suggesting they unplug the charger to protect battery health.

Resource Usage Monitoring CPU Usage Tracking: Alerts when CPU usage exceeds 80%. Memory Usage Tracking: Sends notifications when system memory usage exceeds 80%. Disk Usage Tracking: Monitors and alerts when disk usage exceeds 90%.

Dynamic Alert System Scheduled Alerts: Sends notifications based on user-defined intervals to remind users to check system health. Dynamic Sleep Functionality: Adjusts the monitoring loop's sleep duration based on battery level and resource usage.

Notification System Modern Notifications: Utilizes a notification system for: Battery warnings High resource usage alerts Scheduled notifications Error notifications Customizable Icons: Supports custom icon paths for notifications.

Logging System Event Logging: Logs important events and errors for review and troubleshooting.

Threaded Monitoring Background Thread: Runs monitoring in the background, allowing other applications to operate smoothly.

Graceful Shutdown Shutdown Procedure: Ensures safe shutdown of the monitoring system.

################### How to run?

Clone the repo (bash script) git clone cd battery-life-monitor

pip install psutil (and others if required)

python monitor.py

################### Configure it if you want, but please don't touch the battery marker or you'll be defeating the purrrpose nyaa!

Icon Paths: Update the icon_path variable in the code to customize notification icons. Threshold Values: Modify the threshold values for battery, CPU, memory, and disk usage in the code. Alert Schedule: Adjust the alert intervals by modifying the alert_schedule list in the code.

################### Usage

Once running, the program will monitor your system's battery and resource usage, providing notifications as needed. Significant events will be logged for reference.
