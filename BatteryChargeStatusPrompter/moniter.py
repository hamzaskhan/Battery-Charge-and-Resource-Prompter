import os
import psutil
import asyncio
import threading
import sys
from notifier import send_modern_notification, log_event
from concurrent.futures import ThreadPoolExecutor
import time

# Thresholds for dynamic activation and notifications
BATTERY_THRESHOLD = 80  # Notify if battery > 80% while plugged in
CPU_THRESHOLD = 80  # Notify if CPU usage > 80%
MEMORY_THRESHOLD = 80  # Notify if memory usage > 80%
DISK_THRESHOLD = 90  # Notify if disk usage > 90%

# Global flag to control monitoring
monitoring = True

# Get the directory of the current script or executable
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# Update the icon path to be relative to the script's location
icon_path = os.path.join(base_path, 'icon.ico')  # Main icon path

# Alert scheduling intervals in seconds
alert_schedule = [1800, 3600, 7200]  # 30 mins, 1 hour, 2 hours
last_alert_time = time.time()  # Initialize last_alert_time

# ThreadPoolExecutor for sending notifications
executor = ThreadPoolExecutor(max_workers=5)

def send_notification_async(title, message, category, icon_path):
    executor.submit(send_modern_notification, title, message, category, icon_path)

def dynamic_sleep(cpu_usage, memory_usage, battery_percent, sleep_time):
    """Adjust sleep time based on battery level and system resource usage."""
    if battery_percent < 50 and cpu_usage < 50 and memory_usage < 50:
        return max(600, sleep_time)  # Sleep for 10 minutes
    elif battery_percent >= BATTERY_THRESHOLD or cpu_usage > CPU_THRESHOLD or memory_usage > MEMORY_THRESHOLD:
        return 30  # Sleep for 30 seconds (high activity)
    else:
        return min(180, sleep_time)  # Sleep for 3 minutes (moderate activity)

async def check_battery():
    """Monitor battery status and notify if charger is plugged in and battery > 80%."""
    battery = psutil.sensors_battery()
    if battery:
        battery_percent = battery.percent
        is_plugged_in = battery.power_plugged

        if is_plugged_in and battery_percent >= BATTERY_THRESHOLD:
            send_notification_async(
                'Battery Warning',
                f'Battery is at {battery_percent}%. Unplug your charger to protect battery health!',
                "battery",
                icon_path  # Use the dynamic icon path
            )
            log_event(f"Battery warning sent at {battery_percent}% with charger plugged in.")
        else:
            log_event(f"Battery at {battery_percent}%, Charger plugged in: {is_plugged_in}")
    else:
        log_event("No battery sensor found.")
    return battery.percent if battery else 100  # Return battery percentage for dynamic sleep calculation

async def monitor_resources():
    """Monitor CPU, memory, and disk usage, notifying if usage exceeds thresholds."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')

    # Log resource usage
    log_event(f"CPU: {cpu_usage}%, Memory: {memory_info.percent}%, Disk: {disk_usage.percent}%")

    # Check CPU usage
    if cpu_usage > CPU_THRESHOLD:
        send_notification_async('High CPU Usage', f'CPU usage is at {cpu_usage}%', "cpu", icon_path="icon.ico")
        log_event(f"Notification sent for CPU Usage: {cpu_usage}%")

    # Check memory usage
    if memory_info.percent > MEMORY_THRESHOLD:
        send_notification_async('High Memory Usage', f'Memory usage is at {memory_info.percent}%', "memory", icon_path="icon.ico")
        log_event(f"Notification sent for Memory Usage: {memory_info.percent}%")

    # Check disk usage
    if disk_usage.percent > DISK_THRESHOLD:
        send_notification_async('High Disk Usage', f'Disk usage is at {disk_usage.percent}%', "disk", icon_path="icon.ico")
        log_event(f"Notification sent for Disk Usage: {disk_usage.percent}%")

    return cpu_usage, memory_info.percent

async def monitor_system():
    """Main monitoring function that adjusts sleep based on system and battery status."""
    global monitoring, last_alert_time
    sleep_time = 180  # Initialize sleep time
    while monitoring:
        try:
            # Check battery status
            battery_percent = await check_battery()

            # Check resource usage
            cpu_usage, memory_usage = await monitor_resources()

            # Dynamically adjust sleep time based on resource and battery status
            sleep_time = dynamic_sleep(cpu_usage, memory_usage, battery_percent, sleep_time)

            # Check for scheduled alerts
            current_time = time.time()
            if current_time - last_alert_time >= min(alert_schedule):
                send_notification_async("Scheduled Alert", "This is a scheduled alert.", "info", icon_path)
                log_event("Scheduled alert sent.")
                last_alert_time = current_time

            # Log the sleep time for transparency
            log_event(f"Sleeping for {sleep_time} seconds based on system status.")

            # Sleep asynchronously
            await asyncio.sleep(sleep_time)

        except Exception as e:
            # Handle any exception gracefully
            log_event(f"Error in monitoring: {str(e)}")
            send_notification_async("Monitoring Error", f"An error occurred: {str(e)}", "error", icon_path)

async def shutdown():
    """Gracefully shut down the monitoring system."""
    global monitoring
    log_event("Shutting down monitoring system.")
    monitoring = False

def start_monitoring():
    """Start the monitoring system in a background thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor_system())

def background_monitoring():
    """Run the monitoring system in a background thread."""
    monitor_thread = threading.Thread(target=start_monitoring)
    monitor_thread.start()
    return monitor_thread  # Return the thread reference

async def show_startup_notification():
    """Show a notification when the program starts."""
    send_notification_async(
        'Program Started',
        'The monitoring program is now running!',
        'info',  # Custom category for the notification
        icon_path  # Use the defined path for startup icon
    )
    await asyncio.sleep(4)  # Keep the notification visible for 4 seconds

if __name__ == "__main__":
    try:
        log_event("Monitoring system started.")
        # Create a new event loop to avoid the DeprecationWarning
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # Show the startup notification
        loop.run_until_complete(show_startup_notification())
        monitor_thread = background_monitoring()  # Store the thread reference
        loop.run_forever()  # Run the event loop

    except Exception as e:
        # Log any critical error
        log_event(f"Critical error: {str(e)}")
        send_notification_async("Monitoring Error", f"Critical Error: {str(e)}", "error", icon_path)

    finally:
        asyncio.run(shutdown())  # Ensure proper shutdown sequence
        log_event("Monitoring system has been shut down.")
