#!/usr/bin/env python3
"""
Test script to verify audio files path configuration
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_audio_path_configuration():
    """Test audio files path configuration"""
    
    print("=" * 60)
    print("Audio Files Path Configuration Test")
    print("=" * 60)
    print()
    
    # Get configuration
    audio_path_env = os.environ.get('AUDIO_FILES_PATH', './audio_files')
    resolved_path = Path(audio_path_env).resolve()
    
    print(f"1. Environment Variable")
    print(f"   AUDIO_FILES_PATH = {audio_path_env}")
    print()
    
    print(f"2. Resolved Path")
    print(f"   {resolved_path}")
    print()
    
    print(f"3. Path Status")
    print(f"   Exists: {resolved_path.exists()}")
    print(f"   Is Directory: {resolved_path.is_dir()}")
    
    if resolved_path.exists():
        # Check permissions
        readable = os.access(resolved_path, os.R_OK)
        writable = os.access(resolved_path, os.W_OK)
        executable = os.access(resolved_path, os.X_OK)
        
        print(f"   Readable: {readable}")
        print(f"   Writable: {writable}")
        print(f"   Executable: {executable}")
        
        # Check disk space
        import shutil
        total, used, free = shutil.disk_usage(resolved_path)
        
        print()
        print(f"4. Disk Space")
        print(f"   Total: {total // (2**30)} GB")
        print(f"   Used: {used // (2**30)} GB")
        print(f"   Free: {free // (2**30)} GB")
        
        # List existing subdirectories (video folders)
        subdirs = [d for d in resolved_path.iterdir() if d.is_dir()]
        
        print()
        print(f"5. Existing Video Folders: {len(subdirs)}")
        if subdirs:
            for subdir in subdirs[:5]:  # Show first 5
                files = list(subdir.glob('*.mp3'))
                print(f"   - {subdir.name} ({len(files)} audio files)")
            if len(subdirs) > 5:
                print(f"   ... and {len(subdirs) - 5} more")
    else:
        print(f"   ⚠️  Directory does not exist!")
        print(f"   Will be created on first audio generation")
    
    print()
    
    # Test AudioService initialization
    print("6. Testing AudioService")
    try:
        from services.audio_service import AudioService
        audio_service = AudioService()
        service_path = audio_service.get_audio_base_path()
        print(f"   AudioService path: {service_path}")
        print(f"   Matches config: {service_path == resolved_path}")
        print(f"   ✅ AudioService initialized successfully")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("=" * 60)
    
    # Summary
    if resolved_path.exists() and os.access(resolved_path, os.W_OK):
        print("✅ Configuration is valid and ready!")
    elif not resolved_path.exists():
        print("⚠️  Directory will be created on first use")
    else:
        print("❌ Permission issue - check directory permissions")
    
    print("=" * 60)

if __name__ == "__main__":
    test_audio_path_configuration()
