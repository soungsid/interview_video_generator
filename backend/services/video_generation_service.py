import logging
from typing import Optional, List, Dict
from pathlib import Path
import cv2
import numpy as np
from moviepy.editor import (
    VideoClip, AudioFileClip, ImageClip, CompositeVideoClip, 
    ColorClip, TextClip, concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment

from entities.video import VideoWithDialogues
from services.content_manager_service import ContentManagerService

logger = logging.getLogger(__name__)


class VideoGenerationService:
    """Service for generating complete videos with avatars and dynamic content"""
    
    def __init__(self):
        """Initialize VideoGenerationService"""
        self.video_output_dir = Path("./generated_videos")
        self.video_output_dir.mkdir(parents=True, exist_ok=True)
        self.content_manager = ContentManagerService()
        logger.info("VideoGenerationService initialized")
    
    def get_video_path(self, video_id: str) -> Path:
        """Get the path for a video file"""
        return self.video_output_dir / f"{video_id}.mp4"
    
    async def generate_video(
        self, 
        video: VideoWithDialogues, 
        audio_path: Path,
        video_id: str
    ) -> Path:
        """
        Generate a complete video with avatars and dynamic content.
        
        Args:
            video: Video object with dialogues
            audio_path: Path to the complete audio file
            video_id: Video identifier
            
        Returns:
            Path to generated video file
        """
        logger.info(f"Starting video generation for {video_id}")
        
        output_path = self.get_video_path(video_id)
        
        try:
            # Get audio duration
            audio_clip = AudioFileClip(str(audio_path))
            total_duration = audio_clip.duration
            logger.info(f"Audio duration: {total_duration} seconds")
            
            # Video dimensions (1920x1080 - Full HD)
            width, height = 1920, 1080
            
            # Create animated background
            background = self._create_animated_background(width, height, total_duration)
            
            # Analyze dialogues and calculate timings
            dialogue_segments = await self._prepare_dialogue_segments(
                video, audio_path, total_duration
            )
            
            # Create avatar section (upper half)
            avatar_clips = self._create_avatar_section(
                dialogue_segments, width, height // 2, total_duration
            )
            
            # Create dynamic content section (lower half)
            content_clips = await self._create_content_section(
                video, dialogue_segments, width, height // 2, total_duration
            )
            
            # Composite all elements
            video_clips = [background]
            video_clips.extend(avatar_clips)
            video_clips.extend(content_clips)
            
            final_video = CompositeVideoClip(video_clips, size=(width, height))
            final_video = final_video.set_duration(total_duration)
            final_video = final_video.set_audio(audio_clip)
            
            # Write video file
            logger.info(f"Writing video to {output_path}")
            final_video.write_videofile(
                str(output_path),
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                logger=None  # Suppress moviepy verbose logging
            )
            
            logger.info(f"Video generation completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}", exc_info=True)
            raise
    
    def _create_animated_background(
        self, 
        width: int, 
        height: int, 
        duration: float
    ) -> VideoClip:
        """
        Create an animated gradient background.
        
        Creates a smooth color gradient that subtly changes over time.
        """
        def make_frame(t):
            # Create gradient that shifts over time
            phase = (t / duration) * 2 * np.pi
            
            # Create vertical gradient
            gradient = np.zeros((height, width, 3), dtype=np.uint8)
            
            for y in range(height):
                # Base colors that shift over time
                r = int(40 + 20 * np.sin(phase + y / height * np.pi))
                g = int(60 + 30 * np.sin(phase + y / height * np.pi + np.pi / 3))
                b = int(80 + 40 * np.sin(phase + y / height * np.pi + 2 * np.pi / 3))
                
                gradient[y, :] = [r, g, b]
            
            return gradient
        
        return VideoClip(make_frame, duration=duration)
    
    async def _prepare_dialogue_segments(
        self, 
        video: VideoWithDialogues,
        audio_path: Path,
        total_duration: float
    ) -> List[Dict]:
        """
        Prepare dialogue segments with timing information.
        
        Analyzes individual audio files to get precise timings for each dialogue.
        """
        segments = []
        current_time = 0.0
        
        audio_dir = audio_path.parent
        
        # Check for legacy introduction
        if video.introduction:
            intro_path = audio_dir / "00_introduction.mp3"
            if intro_path.exists():
                audio_segment = AudioSegment.from_mp3(intro_path)
                duration = len(audio_segment) / 1000.0  # Convert to seconds
                
                segments.append({
                    "dialogue": None,
                    "text": video.introduction,
                    "role": "YOUTUBER",
                    "start_time": current_time,
                    "end_time": current_time + duration,
                    "duration": duration,
                    "is_intro": True
                })
                current_time += duration + 0.5  # Add 0.5s pause
        
        # Process all dialogues
        for dialogue in video.dialogues:
            role = dialogue.role.lower() if hasattr(dialogue.role, 'lower') else dialogue.role
            filename = f"{dialogue.question_number:02d}_{role}.mp3"
            dialogue_audio_path = audio_dir / filename
            
            if dialogue_audio_path.exists():
                audio_segment = AudioSegment.from_mp3(dialogue_audio_path)
                duration = len(audio_segment) / 1000.0
                
                segments.append({
                    "dialogue": dialogue,
                    "text": dialogue.text,
                    "role": dialogue.role,
                    "start_time": current_time,
                    "end_time": current_time + duration,
                    "duration": duration,
                    "is_intro": dialogue.question_number == 0
                })
                current_time += duration + 0.5  # Add 0.5s pause
        
        # Add conclusion
        conclusion_path = audio_dir / "99_conclusion.mp3"
        if conclusion_path.exists():
            audio_segment = AudioSegment.from_mp3(conclusion_path)
            duration = len(audio_segment) / 1000.0
            
            segments.append({
                "dialogue": None,
                "text": video.conclusion,
                "role": "YOUTUBER",
                "start_time": current_time,
                "end_time": current_time + duration,
                "duration": duration,
                "is_conclusion": True
            })
        
        logger.info(f"Prepared {len(segments)} dialogue segments")
        return segments
    
    def _create_avatar_section(
        self, 
        dialogue_segments: List[Dict],
        width: int,
        height: int,
        duration: float
    ) -> List[VideoClip]:
        """
        Create avatar section with YouTuber and Candidate avatars.
        
        During introduction, avatars take full height.
        During Q&A, avatars are in upper half.
        """
        clips = []
        
        # Create avatar placeholders
        youtuber_avatar = self._create_avatar_placeholder("YouTuber", (70, 130, 180))
        candidate_avatar = self._create_avatar_placeholder("Candidate", (180, 130, 70))
        
        for segment in dialogue_segments:
            start_time = segment["start_time"]
            end_time = segment["end_time"]
            role = segment["role"]
            
            # Position avatars based on who's speaking
            if role == "YOUTUBER":
                # YouTuber avatar highlighted (left side, larger)
                youtuber_clip = ImageClip(youtuber_avatar).set_duration(end_time - start_time)
                youtuber_clip = youtuber_clip.resize(height=int(height * 0.8))
                youtuber_clip = youtuber_clip.set_position((width // 4 - youtuber_clip.w // 2, height // 2 - youtuber_clip.h // 2))
                youtuber_clip = youtuber_clip.set_start(start_time)
                clips.append(youtuber_clip)
                
                # Candidate avatar dimmed (right side, smaller)
                candidate_clip = ImageClip(candidate_avatar).set_duration(end_time - start_time)
                candidate_clip = candidate_clip.resize(height=int(height * 0.6))
                candidate_clip = candidate_clip.set_position((3 * width // 4 - candidate_clip.w // 2, height // 2 - candidate_clip.h // 2))
                candidate_clip = candidate_clip.set_start(start_time)
                candidate_clip = candidate_clip.set_opacity(0.6)
                clips.append(candidate_clip)
            else:
                # Candidate avatar highlighted (right side, larger)
                candidate_clip = ImageClip(candidate_avatar).set_duration(end_time - start_time)
                candidate_clip = candidate_clip.resize(height=int(height * 0.8))
                candidate_clip = candidate_clip.set_position((3 * width // 4 - candidate_clip.w // 2, height // 2 - candidate_clip.h // 2))
                candidate_clip = candidate_clip.set_start(start_time)
                clips.append(candidate_clip)
                
                # YouTuber avatar dimmed (left side, smaller)
                youtuber_clip = ImageClip(youtuber_avatar).set_duration(end_time - start_time)
                youtuber_clip = youtuber_clip.resize(height=int(height * 0.6))
                youtuber_clip = youtuber_clip.set_position((width // 4 - youtuber_clip.w // 2, height // 2 - youtuber_clip.h // 2))
                youtuber_clip = youtuber_clip.set_start(start_time)
                youtuber_clip = youtuber_clip.set_opacity(0.6)
                clips.append(youtuber_clip)
        
        return clips
    
    def _create_avatar_placeholder(self, name: str, color: tuple) -> np.ndarray:
        """
        Create a placeholder avatar image.
        
        In future versions, this will be replaced with actual avatar images or AI-generated avatars.
        """
        # Create image with PIL
        img_size = 400
        img = Image.new('RGB', (img_size, img_size), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        
        # Draw circle for avatar
        margin = 20
        draw.ellipse(
            [(margin, margin), (img_size - margin, img_size - margin)],
            fill=color,
            outline=(50, 50, 50),
            width=5
        )
        
        # Draw name
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), name, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_position = ((img_size - text_width) // 2, (img_size - text_height) // 2)
        
        draw.text(text_position, name, fill=(255, 255, 255), font=font)
        
        # Convert to numpy array
        return np.array(img)
    
    async def _create_content_section(
        self, 
        video: VideoWithDialogues,
        dialogue_segments: List[Dict],
        width: int,
        height: int,
        duration: float
    ) -> List[VideoClip]:
        """
        Create dynamic content section (lower half of screen).
        
        Content changes based on dialogue context.
        """
        clips = []
        
        # Position for content section (lower half)
        content_y_position = height  # Below the avatar section
        
        for i, segment in enumerate(dialogue_segments):
            # Skip intro segments - content only shows during Q&A
            if segment.get("is_intro", False):
                continue
            
            start_time = segment["start_time"]
            end_time = segment["end_time"]
            dialogue_text = segment["text"]
            
            # Generate content for this segment
            content = await self.content_manager.generate_content_for_dialogue(
                dialogue_text=dialogue_text,
                audio_duration=segment["duration"],
                context=video.topic,
                dialogue_number=i
            )
            
            if content["content_type"] != "none" and content["content_path"]:
                # Load generated content image
                content_img = ImageClip(str(content["content_path"]))
                content_img = content_img.set_duration(end_time - start_time)
                content_img = content_img.resize(width=int(width * 0.8))
                
                # Center in content section
                content_img = content_img.set_position((
                    (width - content_img.w) // 2,
                    content_y_position + (height - content_img.h) // 2
                ))
                content_img = content_img.set_start(start_time)
                
                clips.append(content_img)
        
        return clips
