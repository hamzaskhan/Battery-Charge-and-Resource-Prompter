import logging
import os
from plyer import notification

# Set up logging configuration
logging.basicConfig(filename='monitor.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def send_modern_notification(title, message, category, icon_path=None):
    """
    Send a system notification using plyer.
    
    Args:
        title (str): The title of the notification.
        message (str): The body text of the notification.
        category (str): A category identifier for the notification.
        icon_path (str, optional): Path to the icon image.
    """
    try:
        # Check if the icon path is valid
        if icon_path and not os.path.exists(icon_path):
            raise FileNotFoundError(f"Icon file not found: {icon_path}")
        
        notification.notify(
            title=title,
            message=message,
            app_name='System Monitor',
            app_icon=icon_path,  # Use icon if provided
            timeout=10  # Notification will disappear after 10 seconds
        )
        log_event(f"Notification sent: [{category}] {title} - {message}")
    except Exception as e:
        log_event(f"Failed to send notification: {str(e)}")
        print(f"Error: {str(e)}")  # Print the error for feedback

def log_event(message):
    """
    Log an event to a file with a timestamp.
    
    Args:
        message (str): The message to log.
    """
    logging.info(message)
