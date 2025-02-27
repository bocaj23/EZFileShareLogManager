import os
import time
import shutil
from datetime import datetime, timedelta

LOG_DIR = "logs"
MEDIUM_TERM_DIR = "medium_term_logs"
LONG_TERM_DIR = "long_term_logs"
LOG_FILE = "dummy_log.txt"

# Retention Periods
SHORT_TERM_DAYS = 7     
MEDIUM_TERM_DAYS = 30  
LONG_TERM_DAYS = 365

def wait_until(hour, minute):
    """Pauses execution until the given time (hour, minute) in the next 24-hour period."""
    now = datetime.now()
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if target_time < now:
        target_time += timedelta(days=1)

    wait_seconds = (target_time - now).total_seconds()
    time.sleep(wait_seconds)

def get_formatted_date():
    """Returns the current date formatted as MM_DD_YYYY."""
    return datetime.now().strftime("%m_%d_%Y")

def ensure_directories():
    """Ensures required directories exist."""
    for directory in [LOG_DIR, MEDIUM_TERM_DIR, LONG_TERM_DIR]:
        os.makedirs(directory, exist_ok=True)

def rotate_logs():
    """Copies the log file to the logs directory with a timestamped filename and clears it."""
    if not os.path.exists(LOG_FILE) or os.stat(LOG_FILE).st_size == 0:
        print("No log file to rotate.")
        return

    formatted_date = get_formatted_date()
    backup_file = os.path.join(LOG_DIR, f"log_{formatted_date}.txt")

    shutil.copy(LOG_FILE, backup_file)  # Copy file
    open(LOG_FILE, "w").close()  # Clear the log file

def archive_medium_term():
    """Archives logs older than SHORT_TERM_DAYS but within MEDIUM_TERM_DAYS."""
    now = datetime.now()
    archive_name = os.path.join(MEDIUM_TERM_DIR, f"medium_logs_{get_formatted_date()}.tar.gz")
    
    logs_to_archive = []
    
    for filename in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, filename)
        if os.path.isfile(file_path):
            try:
                file_date_str = filename.replace("log_", "").replace(".txt", "")
                file_date = datetime.strptime(file_date_str, "%m_%d_%Y")
                
                if SHORT_TERM_DAYS < (now - file_date).days <= MEDIUM_TERM_DAYS:
                    logs_to_archive.append(file_path)
            except ValueError:
                continue 

    if logs_to_archive:
        shutil.make_archive(archive_name.replace(".tar.gz", ""), 'gztar', LOG_DIR)
        for log in logs_to_archive:
            os.remove(log)

def move_to_long_term():
    """Moves logs older than MEDIUM_TERM_DAYS to long-term storage."""
    now = datetime.now()

    for filename in os.listdir(MEDIUM_TERM_DIR):
        file_path = os.path.join(MEDIUM_TERM_DIR, filename)
        if os.path.isfile(file_path) and filename.endswith(".tar.gz"):
            try:
                file_date_str = filename.replace("medium_logs_", "").replace(".tar.gz", "")
                file_date = datetime.strptime(file_date_str, "%m_%d_%Y")
                
                if (now - file_date).days > MEDIUM_TERM_DAYS:
                    shutil.move(file_path, LONG_TERM_DIR)
            except ValueError:
                continue 

def cleanup_old_logs():
    """Deletes logs older than LONG_TERM_DAYS from long-term storage."""
    now = datetime.now()

    for filename in os.listdir(LONG_TERM_DIR):
        file_path = os.path.join(LONG_TERM_DIR, filename)
        if os.path.isfile(file_path) and filename.endswith(".tar.gz"):
            try:
                file_date_str = filename.replace("medium_logs_", "").replace(".tar.gz", "")
                file_date = datetime.strptime(file_date_str, "%m_%d_%Y")

                if (now - file_date).days > LONG_TERM_DAYS:
                    os.remove(file_path)
            except ValueError:
                continue 

if __name__ == "__main__":
    ensure_directories()

    while True:
        wait_until(0, 0) 
        rotate_logs()  
        archive_medium_term()
        move_to_long_term()
        cleanup_old_logs()

