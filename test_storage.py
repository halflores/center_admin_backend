import sys
import os
from app.services.audio_storage_service import audio_storage_service

def test_storage():
    try:
        content = b"test_content"
        # Using a dummy lesson ID distinct from real ones
        path, size = audio_storage_service.save_audio_from_bytes(content, 999, ".txt")
        print(f"Returned Path: {path}")
        print(f"Size: {size}")
        
        abs_path = audio_storage_service.get_absolute_path(path)
        print(f"Absolute Path: {abs_path}")
        print(f"Exists: {abs_path.exists()}")
        
        # Clean up
        if abs_path.exists():
            print("Cleaning up test file...")
            audio_storage_service.delete_audio_file(path)
            print("Cleaned up.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    test_storage()
