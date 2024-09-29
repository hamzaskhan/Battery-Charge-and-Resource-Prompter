import os
import psutil
import asyncio
import threading
import sys
from win10toast_click import ToastNotifier
from concurrent.futures import ThreadPoolExecutor
import time
import logging

# Set up logging path within AppData folder
log_file_path = os.path.join(os.getenv('APPDATA'), 'Betty', 'monitor.log')
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

# Notification thresholds
BATTERY_THRESHOLD = 80
CPU_THRESHOLD = 80
MEMORY_THRESHOLD = 80
DISK_THRESHOLD = 90

monitoring = True  # Flag to control monitoring

# Handle relative paths for icon files, accommodating for bundled executables
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
icon_path = os.path.join(base_path, 'icon.ico')

# Set alert intervals: 30 mins, 1 hour, 2 hours
alert_schedule = [1800, 3600, 7200]
last_alert_time = time.time()

# Thread pool for notification handling
executor = ThreadPoolExecutor(max_workers=5)

def send_notification_async(title, message, category):
    """Send system notifications asynchronously."""
    executor.submit(send_modern_notification, title, message, category, icon_path)

def send_modern_notification(title, message, category, icon_path=None):
    """Send toast notification with specified parameters."""
    try:
        toaster = ToastNotifier()
        toaster.show_toast(title, message, icon_path=icon_path, duration=10)
        log_event(f"Notification sent successfully: [{category}] {title}")
    except Exception as e:
        log_event(f"Failed to send notification: {str(e)}")

def log_event(message):
    """Log event messages with a timestamp."""
    logging.info(message)

def dynamic_sleep(cpu_usage, memory_usage, battery_percent, sleep_time):
    """Adjust sleep time based on current system resource usage."""
    if battery_percent < 50 and cpu_usage < 50 and memory_usage < 50:
        return max(600, sleep_time)
    elif battery_percent >= BATTERY_THRESHOLD or cpu_usage > CPU_THRESHOLD or memory_usage > MEMORY_THRESHOLD:
        return 30  # Short sleep if high activity
    else:
        return min(180, sleep_time)  # Moderate activity sleep

async def check_battery():
    """Check battery status and notify user if necessary."""
    battery = psutil.sensors_battery()
    if battery:
        battery_percent = battery.percent
        is_plugged_in = battery.power_plugged

        if is_plugged_in and battery_percent >= BATTERY_THRESHOLD:
            send_notification_async(
                'Battery Warning',
                f'Battery is at {battery_percent}%. Unplug your charger to protect battery health!',
                "battery"
            )
            log_event(f"Battery warning sent at {battery_percent}% with charger plugged in.")
        else:
            log_event(f"Battery at {battery_percent}%, Charger plugged in: {is_plugged_in}")
    else:
        log_event("No battery sensor found.")
    return battery.percent if battery else 100  # Return for dynamic sleep

async def monitor_resources():
    """Monitor CPU, memory, and disk usage; notify user when thresholds are crossed."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')

    log_event(f"CPU: {cpu_usage}%, Memory: {memory_info.percent}%, Disk: {disk_usage.percent}%")

    if cpu_usage > CPU_THRESHOLD:
        send_notification_async('High CPU Usage', f'CPU usage is at {cpu_usage}%', "cpu")
        log_event(f"Notification sent for CPU Usage: {cpu_usage}%")

    if memory_info.percent > MEMORY_THRESHOLD:
        send_notification_async('High Memory Usage', f'Memory usage is at {memory_info.percent}%', "memory")
        log_event(f"Notification sent for Memory Usage: {memory_info.percent}%")

    if disk_usage.percent > DISK_THRESHOLD:
        send_notification_async('High Disk Usage', f'Disk usage is at {disk_usage.percent}%', "disk")
        log_event(f"Notification sent for Disk Usage: {disk_usage.percent}%")

    return cpu_usage, memory_info.percent

async def monitor_system():
    """Main system monitoring loop, adjusting sleep based on system state."""
    global monitoring, last_alert_time
    sleep_time = 180
    while monitoring:
        try:
            battery_percent = await check_battery()  # Battery status check
            cpu_usage, memory_usage = await monitor_resources()  # Resource usage check

            # Adjust sleep dynamically based on system conditions
            sleep_time = dynamic_sleep(cpu_usage, memory_usage, battery_percent, sleep_time)

            # Handle scheduled alerts based on predefined intervals
            current_time = time.time()
            if current_time - last_alert_time >= min(alert_schedule):
                send_notification_async("Scheduled Alert", "This is a scheduled alert.", "info")
                log_event("Scheduled alert sent.")
                last_alert_time = current_time

            log_event(f"Sleeping for {sleep_time} seconds based on system status.")
            await asyncio.sleep(sleep_time)

        except Exception as e:
            log_event(f"Error in monitoring: {str(e)}")
            send_notification_async("Monitoring Error", f"An error occurred: {str(e)}", "error")

async def shutdown():
    """Gracefully shut down monitoring tasks."""
    global monitoring
    log_event("Shutting down monitoring system.")
    monitoring = False

def start_monitoring():
    """Start system monitoring in a new asyncio event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor_system())

def background_monitoring():
    """Run monitoring in a background thread to keep the main thread free."""
    monitor_thread = threading.Thread(target=start_monitoring)
    monitor_thread.start()
    return monitor_thread

async def show_startup_notification():
    """Show notification at program startup."""
    send_notification_async(
        'Program Started',
        'The monitoring program is now running!',
        'info'
    )
    await asyncio.sleep(4)

if __name__ == "__main__":
    try:
        log_event("Monitoring system started.")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(show_startup_notification())
        monitor_thread = background_monitoring()
        loop.run_forever()

    except Exception as e:
        log_event(f"Critical error: {str(e)}")
        send_notification_async("Monitoring Error", f"Critical Error: {str(e)}", "error")

    finally:
        asyncio.run(shutdown())
        log_event("Monitoring system has been shut down.")
