import logging
import os
import boto3
from pathlib import Path
from typing import List
from botocore.exceptions import ClientError
from pydub import AudioSegment

logger = logging.getLogger(__name__)


class AudioService:
    """Service for generating and managing audio files using Amazon Polly"""
    
    def __init__(self):
        """Initialize Amazon Polly client"""
        self.aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        self.voice_interviewer = os.environ.get('POLLY_VOICE_INTERVIEWER', 'Matthew')
        self.voice_candidate = os.environ.get('POLLY_VOICE_CANDIDATE', 'Joanna')
        
        # Configure audio files directory
        audio_path = os.environ.get('AUDIO_FILES_PATH', './audio_files')
        self.audio_base_path = Path(audio_path).resolve()
        
        # Create directory if it doesn't exist
        self.audio_base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Audio files directory: {self.audio_base_path}")
        
        if not self.aws_access_key or not self.aws_secret_key:
            logger.warning("AWS credentials not configured - audio generation will be disabled")
            self.client = None
        else:
            self.client = boto3.client(
                'polly',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
            logger.info(f"AudioService initialized with region: {self.aws_region}")
    
    def generate_audio(self, text: str, output_path: Path, role: str = "interviewer") -> bool:
        """
        Generate audio from text using Amazon Polly
        
        Args:
            text: Text to synthesize
            output_path: Path where audio file will be saved
            role: "interviewer" or "candidate" to select appropriate voice
        
        Returns:
            True if audio was generated, False if file already exists or error occurred
        """
        if not self.client:
            logger.error("Polly client not initialized - skipping audio generation")
            return False
        
        # Check if audio file already exists
        if output_path.exists():
            logger.info(f"Audio file already exists: {output_path}")
            return False
        
        try:
            # Select voice based on role
            voice_id = self.voice_interviewer if role == "interviewer" else self.voice_candidate
            
            logger.info(f"Generating audio: role={role}, voice={voice_id}, text_length={len(text)}")
            
            # Call Amazon Polly
            response = self.client.synthesize_speech(
                Engine='neural',
                Text=text,
                TextType='text',
                OutputFormat='mp3',
                VoiceId=voice_id
            )
            
            # Save audio to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            logger.info(f"Audio generated successfully: {output_path}")
            return True
            
        except ClientError as e:
            logger.error(f"Polly API error: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Failed to generate audio: {str(e)}")
            return False
    
    def concatenate_audio_files(self, audio_paths: List[Path], output_path: Path) -> bool:
        """
        Concatenate multiple audio files into one
        
        Args:
            audio_paths: List of paths to audio files to concatenate
            output_path: Path where concatenated audio will be saved
        
        Returns:
            True if concatenation successful, False otherwise
        """
        try:
            logger.info(f"Concatenating {len(audio_paths)} audio files")
            
            # Filter only existing files
            existing_paths = [p for p in audio_paths if p.exists()]
            
            if not existing_paths:
                logger.warning("No audio files to concatenate")
                return False
            
            # Load first audio file
            combined = AudioSegment.from_mp3(existing_paths[0])
            
            # Add small pause between segments (500ms)
            pause = AudioSegment.silent(duration=500)
            
            # Concatenate all audio files with pauses
            for audio_path in existing_paths[1:]:
                combined = combined + pause + AudioSegment.from_mp3(audio_path)
            
            # Save concatenated audio
            output_path.parent.mkdir(parents=True, exist_ok=True)
            combined.export(output_path, format="mp3")
            
            logger.info(f"Concatenated audio saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to concatenate audio files: {str(e)}")
            return False
    
    def get_audio_base_path(self) -> Path:
        """Get base path for audio files"""
        return self.audio_base_path
    
    def get_video_audio_dir(self, video_id: str) -> Path:
        """Get audio directory for a specific video"""
        return self.get_audio_base_path() / video_id
    
    def generate_video_audio_url(self, video_id: str, filename: str) -> str:
        """Generate audio URL for API response"""
        return f"/api/videos/{video_id}/audio/{filename}"
