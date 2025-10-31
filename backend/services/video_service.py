import logging
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from entities.video import Video, VideoWithDialogues
from entities.dialogue import Dialogue, DialogueResponse

logger = logging.getLogger(__name__)


class VideoService:
    """Service for managing video persistence"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def create_video(self, topic: str, script_data: dict) -> Video:
        """Create and save a video with its script"""
        # Create video document
        video = Video(
            title=f"Simulated Interview: {topic}",
            topic=topic,
            introduction=script_data["introduction"],
            conclusion=script_data["conclusion"]
        )
        
        # Save video to database
        video_dict = video.model_dump()
        video_dict['created_at'] = video_dict['created_at'].isoformat()
        await self.db.videos.insert_one(video_dict)
        
        logger.info(f"Video created with ID: {video.id}")
        
        # Save dialogues
        for dialogue_data in script_data["dialogues"]:
            dialogue = Dialogue(
                **dialogue_data,
                video_id=video.id
            )
            dialogue_dict = dialogue.model_dump()
            await self.db.dialogues.insert_one(dialogue_dict)
        
        logger.info(f"Saved {len(script_data['dialogues'])} dialogues")
        
        return video
    
    async def get_video_by_id(self, video_id: str) -> Optional[VideoWithDialogues]:
        """Retrieve a video with all its dialogues"""
        # Get video
        video_doc = await self.db.videos.find_one({"id": video_id}, {"_id": 0})
        if not video_doc:
            return None
        
        # Convert ISO string back to datetime
        if isinstance(video_doc['created_at'], str):
            video_doc['created_at'] = datetime.fromisoformat(video_doc['created_at'])
        
        # Get dialogues
        dialogues_cursor = self.db.dialogues.find({"video_id": video_id}, {"_id": 0}).sort("question_number", 1)
        dialogues = await dialogues_cursor.to_list(1000)
        
        # Convert to response models
        dialogue_responses = [DialogueResponse(**d) for d in dialogues]
        
        return VideoWithDialogues(
            **video_doc,
            dialogues=dialogue_responses
        )
    
    async def get_all_videos(self) -> List[Video]:
        """Retrieve all videos (without dialogues)"""
        videos_cursor = self.db.videos.find({}, {"_id": 0}).sort("created_at", -1)
        videos = await videos_cursor.to_list(1000)
        
        # Convert ISO strings back to datetime
        for video in videos:
            if isinstance(video['created_at'], str):
                video['created_at'] = datetime.fromisoformat(video['created_at'])
        
        return [Video(**v) for v in videos]
