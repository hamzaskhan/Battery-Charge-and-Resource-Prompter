import logging
import os
from win10toast_click import ToastNotifier

# Configure logging to write to 'monitor.log' file with timestamped entries
logging.basicConfig(filename='monitor.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Initialize the Windows toast notification system
toaster = ToastNotifier()

def send_modern_notification(title, message, category, icon_path=None, callback=None):
    """
    Display a system notification with an optional icon and callback.
    
    Args:
        title (str): Title of the notification.
        message (str): Body content of the notification.
        category (str): Category for logging purposes.
        icon_path (str, optional): Path to an icon file (optional).
        callback (function, optional): A function to be executed when the notification is clicked (optional).
    """
    try:
        # Check if the icon file exists if an icon path is provided
        if icon_path and not os.path.exists(icon_path):
            raise FileNotFoundError(f"Icon file not found: {icon_path}")
        
        # Display the notification with optional callback on click
        toaster.show_toast(
            title=title,
            msg=message,
            icon_path=icon_path,
            duration=10,  # Duration in seconds the notification stays visible
            threaded=True  # Ensures the notification runs in a non-blocking manner
        )
        log_event(f"Notification sent: [{category}] {title} - {message}")
    except Exception as e:
        log_event(f"Failed to send notification: {str(e)}")
        print(f"Error: {str(e)}")  # Print error for immediate feedback during execution

def log_event(message):
    """
    Log a message to the log file.
    
    Args:
        message (str): Message to log with a timestamp.
    """
    logging.info(message)
