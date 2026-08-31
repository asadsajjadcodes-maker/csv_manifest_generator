import csv
from logger import setup_logger
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = setup_logger(__name__)

def get_file_metadata(file_path: Path) -> Optional[dict[str, Any]]:
    try:
        stat_info = file_path.stat() # stat() to get the metadata like size and timestamps.

        # size in mb 
        size_mb = round(stat_info.st_size/(1024 * 1024), 4)

        # covertes the data to readable formate 
        # last modification date 
        mod_time = datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        # Return structured metadata key-value dictionary for the file.
        return {
            "Filename": file_path.name,
            # if file have ext ok else use no extension 
            "Extension": file_path.suffix.lower() if file_path.suffix else "No_extension",
            "Parent_Folder": str(file_path.parent),
            "Size_MB": size_mb,
            "Last_Modified": mod_time,
            "Full_Path": str(file_path.resolve())
        }

    # Catch file access permission issues and file not found errors safely.
    except (PermissionError, FileNotFoundError) as er:

        # log a warning message with error details and skip the file.
        logger.warning(f"Skipping unreadable file '{file_path}': {er}")

        # Return None to signify the failure in extracting the metadata.
        return None


    