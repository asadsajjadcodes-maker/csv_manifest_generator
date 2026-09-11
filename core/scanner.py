import csv
from utilities.logger import setup_logger
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


#================================================================================================================================

def scan_directory(target_dir: str | Path, extension_filter: Optional[str] = None) -> List[dict[str, Any]]:

    # Convert string or Path object to the absolute resolved Path instance.
    base_path = Path(target_dir).resolve()

    # Empty list to add the metadata dictionaries.
    manifest_data: list[dict[str, Any]] = []

    # Validate the directory.
    if not base_path.exists() or not base_path.is_dir():
        # Raise an ValueError if Path dose not exist or is not a directory.
        raise ValueError(f"Invalid dir path : '{base_path}'")

    logger.info(f"Starting scan in directory: '{base_path}'")

    # Normalize the extension 
    target_ext = extension_filter.lower().strip() if extension_filter else None
    # make extension lower and remove spaces from start and end if extension is given else None 

    if target_ext and not target_ext.startswith("."):
        target_ext = f".{target_ext}"


    for path in base_path.rglob("*"):
        if path.is_file():
            # Apply file extension filter if set: skip if it does not match
            if target_ext and path.suffix.lower() != target_ext:
                continue
            # Extract file metadata dictionary using the helper function
            metadata = get_file_metadata(path)

            # Append metadata to the results list  if successfully retrieved.
            if metadata:
                manifest_data.append(metadata)


    logger.info(f"Scan complete. Found '{len(manifest_data)}' matching files.")

    # return the collected data.
    return manifest_data

#================================================================================================================


def export_to_csv(manifested_data: list[dict[str, Any]], output_file: str | Path) -> Path:

    # Create the Path object.
    output_path = Path(output_file).resolve()

    # Create parant folders if dont exist.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if there is no data.
    if not manifested_data:
        logger.warning("No data is available to export.")

        return output_path

    # Define strict column header ordering for CSV document.
    fieldnames = ["Filename", "Extension", "Parent_Folder", "Size_MB", "Last_Modified", "Full_Path"]

    with open(output_path, mode="w", newline="", encoding="utf-8") as csv_file:
        # Dictwritter to define fieldnames order 
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        # Write the header row(column names).
        writer.writeheader()
        # Write all rows from manifest dictionary list.
        writer.writerows(manifested_data)

    logger.info(f"Successfully generated manifest CSV: {output_path}")
    return output_path




         
    


