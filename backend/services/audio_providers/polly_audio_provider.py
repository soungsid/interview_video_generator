import os
import logging
import boto3
from pathlib import Path
from botocore.exceptions import ClientError

from .base_audio_provider import BaseAudioProvider

logger = logging.getLogger(__name__)


class PollyAudioProvider(BaseAudioProvider):
    """Amazon Polly audio provider"""
    
    def __init__(self):
        self.aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        self.interviewer_voice = os.environ.get('POLLY_VOICE_INTERVIEWER', 'Matthew')
        self.candidate_voice = os.environ.get('POLLY_VOICE_CANDIDATE', 'Joanna')
        
        if not self.aws_access_key or not self.aws_secret_key:
            logger.warning("AWS credentials not configured - Polly will be disabled")
            self.client = None
        else:
            self.client = boto3.client(
                'polly',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
            logger.info(f"PollyAudioProvider initialized with region: {self.aws_region}")
    
    def generate_audio(self, text: str, output_path: Path, voice_id: str) -> bool:
        """Generate audio using Amazon Polly"""
        if not self.client:
            logger.error("Polly client not initialized")
            return False
        
        if output_path.exists():
            logger.info(f"Audio file already exists: {output_path}")
            return False
        
        try:
            logger.info(f"Generating audio with Polly: voice={voice_id}, text_length={len(text)}")
            
            response = self.client.synthesize_speech(
                Engine='neural',
                Text=text,
                TextType='text',
                OutputFormat='mp3',
                VoiceId=voice_id
            )
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            logger.info(f"Polly audio generated: {output_path}")
            return True
            
        except ClientError as e:
            logger.error(f"Polly API error: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Polly error: {str(e)}")
            return False
    
    def get_default_interviewer_voice(self) -> str:
        return self.interviewer_voice
    
    def get_default_candidate_voice(self) -> str:
        return self.candidate_voice
