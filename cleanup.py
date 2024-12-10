import os
import time

def cleanup_old_files(directory='download', max_age_hours=24):
    current_time = time.time()
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        file_age = current_time - os.path.getmtime(filepath)
        
        if file_age > (max_age_hours * 3600):
            os.remove(filepath)

if __name__ == "__main__":
    cleanup_old_files()
