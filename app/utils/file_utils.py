"""
File utility functions.
"""
from pathlib import Path


def save_voice_file(file_content: bytes, filename: str, upload_dir: Path) -> str:
    """
    Save uploaded voice file to disk.
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        upload_dir: Directory to save files
        
    Returns:
        Path to saved file
    """
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename to avoid collisions
    file_path = upload_dir / filename
    
    # If file exists, append a counter
    counter = 1
    while file_path.exists():
        stem = file_path.stem
        suffix = file_path.suffix
        file_path = upload_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    
    file_path.write_bytes(file_content)
    return str(file_path)


def validate_audio_file(content_type: str) -> bool:
    """
    Validate that the uploaded file is an audio file.
    
    Args:
        content_type: MIME type of the file
        
    Returns:
        True if valid audio type, False otherwise
    """
    valid_types = {
        "audio/wav",
        "audio/wave",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp3",
        "audio/mp4",
        "audio/x-m4a",
        "audio/m4a",
        "audio/ogg",
        "audio/webm",
        "audio/flac",
    }
    return content_type.lower() in valid_types

