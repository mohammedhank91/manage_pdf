import os
import tempfile
import shutil
import logging
import json
import time
from datetime import datetime

# Persistent storage for tracking files to clean up later
CLEANUP_REGISTRY_FILE = os.path.join(tempfile.gettempdir(), "pdf_manager_cleanup.json")

def mark_for_future_cleanup(filepath):
    """
    Mark a file or directory for cleanup on next application start
    if it can't be deleted now.
    """
    try:
        # Load existing cleanup registry
        cleanup_registry = []
        if os.path.exists(CLEANUP_REGISTRY_FILE):
            try:
                with open(CLEANUP_REGISTRY_FILE, 'r') as f:
                    cleanup_registry = json.load(f)
            except Exception as e:
                logging.error(f"Error reading cleanup registry: {str(e)}")
                cleanup_registry = []
        
        # Add this file if it's not already in the registry
        if filepath not in cleanup_registry:
            cleanup_registry.append(filepath)
            
            # Save updated registry
            with open(CLEANUP_REGISTRY_FILE, 'w') as f:
                json.dump(cleanup_registry, f)
                
            logging.info(f"Marked for future cleanup: {filepath}")
    except Exception as e:
        logging.error(f"Error marking file for future cleanup: {str(e)}")

def process_deferred_cleanup():
    """
    Process any files that were marked for deferred cleanup
    from previous runs.
    """
    if not os.path.exists(CLEANUP_REGISTRY_FILE):
        return 0
        
    cleaned = 0
    try:
        # Load the cleanup registry
        with open(CLEANUP_REGISTRY_FILE, 'r') as f:
            cleanup_registry = json.load(f)
            
        # Keep track of files we couldn't clean up this time
        still_locked = []
            
        # Try to clean up each file/directory
        for filepath in cleanup_registry:
            try:
                if os.path.exists(filepath):
                    if os.path.isdir(filepath):
                        shutil.rmtree(filepath, ignore_errors=True)
                    else:
                        os.unlink(filepath)
                    logging.info(f"Cleaned deferred file/directory: {filepath}")
                    cleaned += 1
                else:
                    # File no longer exists, consider it cleaned
                    cleaned += 1
            except Exception as e:
                logging.warning(f"File still locked, deferring again: {filepath} - {str(e)}")
                still_locked.append(filepath)
                
        # Update the registry with files still locked
        with open(CLEANUP_REGISTRY_FILE, 'w') as f:
            json.dump(still_locked, f)
            
    except Exception as e:
        logging.error(f"Error processing deferred cleanup: {str(e)}")
        
    return cleaned

def force_cleanup_temp_files():
    """
    Forcefully clean up all temporary files created by the PDF Manager application.
    This is a utility function to be called at application exit or on demand.
    """
    # First process any deferred cleanup from previous runs
    cleaned_deferred = process_deferred_cleanup()
    
    # Get the system's temporary directory
    temp_dir = tempfile.gettempdir()
    
    # Search for files and directories that match our application's naming patterns
    patterns = ["pdf_compress_", "pdf_convert_", "compressed_", "temp_", "img_temp_"]
    cleaned_count = 0
    
    try:
        # First pass - look for our temp directories
        for item in os.listdir(temp_dir):
            for pattern in patterns:
                if item.startswith(pattern):
                    full_path = os.path.join(temp_dir, item)
                    try:
                        if os.path.isdir(full_path):
                            # It's a directory, remove it recursively
                            shutil.rmtree(full_path, ignore_errors=True)
                            logging.info(f"Cleaned temp directory: {full_path}")
                        elif os.path.isfile(full_path):
                            # It's a file, remove it directly
                            os.unlink(full_path)
                            logging.info(f"Cleaned temp file: {full_path}")
                        cleaned_count += 1
                    except Exception as e:
                        logging.error(f"Failed to clean {full_path}: {str(e)}")
                        # Mark for deferred cleanup
                        mark_for_future_cleanup(full_path)
                    break  # Break after first match to avoid checking other patterns
        
        # Second pass - look for PDF files in the root of temp directory that might be ours
        for item in os.listdir(temp_dir):
            if item.endswith(".pdf"):
                # Check if it matches any of our known patterns or is likely created by our app
                is_ours = any(pattern in item for pattern in patterns)
                
                if is_ours:
                    full_path = os.path.join(temp_dir, item)
                    try:
                        if os.path.isfile(full_path):
                            os.unlink(full_path)
                            logging.info(f"Cleaned temp PDF file: {full_path}")
                            cleaned_count += 1
                    except Exception as e:
                        logging.error(f"Failed to clean PDF file {full_path}: {str(e)}")
                        # Mark for deferred cleanup
                        mark_for_future_cleanup(full_path)
        
        # Look for any files within temp directories that match our patterns
        for item in os.listdir(temp_dir):
            if os.path.isdir(os.path.join(temp_dir, item)):
                dir_path = os.path.join(temp_dir, item)
                try:
                    for file_item in os.listdir(dir_path):
                        if file_item.endswith(".pdf") or any(p in file_item for p in patterns):
                            file_path = os.path.join(dir_path, file_item)
                            try:
                                if os.path.isfile(file_path):
                                    os.unlink(file_path)
                                    logging.info(f"Cleaned nested temp file: {file_path}")
                                    cleaned_count += 1
                            except Exception as e:
                                logging.error(f"Failed to clean nested file {file_path}: {str(e)}")
                                # Mark for deferred cleanup
                                mark_for_future_cleanup(file_path)
                except Exception:
                    # Ignore errors listing directory contents
                    pass
        
        # Total cleanup count includes deferred cleanups that were processed
        total_cleaned = cleaned_count + cleaned_deferred
        logging.info(f"Cleanup completed: removed {total_cleaned} temporary files/directories")
        return total_cleaned
    except Exception as e:
        logging.error(f"Error during temporary file cleanup: {str(e)}")
        return cleaned_deferred  # Return at least the count of deferred files we cleaned 