import os
from typing import Optional, Any, Dict
from pymongo import MongoClient
from pymongo.collection import Collection
from bson import ObjectId
from dotenv import load_dotenv
from models.db_models import Job, StoryverseMetaData

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.mongo_uri = os.getenv('MONGODB_URI')
        self.db_name = os.getenv('MONGODB_DATABASE', 'sherlock-v2')
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]
    
    def create_job(self, job: Job) -> str:
        """Create a new job and return its ID"""
        result = self.db.jobs.insert_one(job.model_dump())
        return str(result.inserted_id)
    
    def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update a job with new data"""
        result = self.db.jobs.update_one(
            {"_id": ObjectId(job_id)}, 
            {"$set": updates}
        )
        return result.modified_count > 0
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID"""
        job_data = self.db.jobs.find_one({"_id": ObjectId(job_id)})
        if job_data:
            return Job(**job_data)
        return None
    
    def update_job_field(self, job_id: str, job: Job) -> bool:
        """Update a job using a Job model instance"""
        result = self.db.jobs.update_one(
            {"_id": ObjectId(job_id)}, 
            {"$set": job.model_dump()}
        )
        return result.modified_count > 0
    
    def get_meta_data(self, story_verse: str) -> Optional[StoryverseMetaData]:
        """Get meta data for story verse"""
        meta_data = self.db.story_verse_meta_data.find_one({"storyVerse": story_verse})
        if meta_data:
            return StoryverseMetaData(**meta_data)
    
    def close(self):
        """Close database connection"""
        self.client.close()