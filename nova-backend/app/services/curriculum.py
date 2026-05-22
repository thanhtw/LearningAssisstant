"""
Curriculum service - manages topic definitions and progression
"""

import json
import os
from typing import List, Optional, TypedDict


class Topic(TypedDict):
    """Topic definition"""
    id: str
    title: str
    level: str
    prerequisites: List[str]
    description: str


class CurriculumService:
    """Service for loading and querying curriculum topics"""
    
    _instance = None
    _topics: dict[str, Topic] = {}
    
    def __new__(cls):
        """Singleton pattern - only one curriculum instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_curriculum()
        return cls._instance
    
    def _load_curriculum(self) -> None:
        """Load curriculum from JSON file"""
        # Find the curriculum.json file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        curriculum_path = os.path.join(base_dir, "data", "curriculum.json")
        
        if not os.path.exists(curriculum_path):
            raise FileNotFoundError(f"Curriculum file not found at {curriculum_path}")
        
        with open(curriculum_path, "r") as f:
            data = json.load(f)
        
        # Index topics by id
        self._topics = {topic["id"]: topic for topic in data["topics"]}
    
    def get_topic(self, topic_id: str) -> Optional[Topic]:
        """
        Get a single topic by id.
        
        Args:
            topic_id: Topic identifier
            
        Returns:
            Topic definition or None if not found
        """
        return self._topics.get(topic_id)
    
    def get_available_topics(self, mastered: List[str]) -> List[Topic]:
        """
        Get topics that are available based on mastered topics.
        A topic is available if all its prerequisites are in the mastered list.
        
        Args:
            mastered: List of topic ids that student has mastered
            
        Returns:
            List of available topics
        """
        mastered_set = set(mastered)
        available = []
        
        for topic in self._topics.values():
            # Check if all prerequisites are mastered
            prerequisites_met = all(
                prereq in mastered_set for prereq in topic["prerequisites"]
            )
            
            # Topic is available if prerequisites met and not yet mastered
            if prerequisites_met and topic["id"] not in mastered_set:
                available.append(topic)
        
        return sorted(available, key=lambda t: (t["level"], t["title"]))
    
    def get_next_topic(self, mastered: List[str]) -> Optional[Topic]:
        """
        Get the next recommended topic for the student.
        Returns the easiest available topic not yet mastered.
        
        Args:
            mastered: List of topic ids that student has mastered
            
        Returns:
            Next recommended topic or None if all topics mastered
        """
        available = self.get_available_topics(mastered)
        
        # Return the first available (already sorted by level and title)
        return available[0] if available else None
    
    def get_all_topics(self) -> List[Topic]:
        """
        Get all topics in the curriculum.
        
        Returns:
            List of all topics sorted by level and title
        """
        return sorted(
            self._topics.values(),
            key=lambda t: (t["level"], t["title"])
        )
    
    def get_topics_by_level(self, level: str) -> List[Topic]:
        """
        Get all topics at a specific level.
        
        Args:
            level: Level filter ("beginner", "intermediate", "advanced")
            
        Returns:
            List of topics at the specified level
        """
        return [
            t for t in self._topics.values() 
            if t["level"] == level
        ]


# Singleton instance
_curriculum_service = CurriculumService()


# Convenience functions
def get_curriculum_service() -> CurriculumService:
    """Get the curriculum service singleton"""
    return _curriculum_service


def get_topic(topic_id: str) -> Optional[Topic]:
    """Get a topic by id"""
    return _curriculum_service.get_topic(topic_id)


def get_available_topics(mastered: List[str]) -> List[Topic]:
    """Get available topics based on mastery"""
    return _curriculum_service.get_available_topics(mastered)


def get_next_topic(mastered: List[str]) -> Optional[Topic]:
    """Get the next recommended topic"""
    return _curriculum_service.get_next_topic(mastered)
