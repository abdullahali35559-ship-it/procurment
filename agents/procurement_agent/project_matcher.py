"""
Project Matcher Module
Matches emails to existing or new projects
"""
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Project, Client
from database.connection import SessionLocal
from models.pixtral_client import PixtralClient
import re


class ProjectMatcher:
    """Match emails to existing or new projects"""
    
    def __init__(self):
        self.llm = PixtralClient()
    
    def find_matching_project(self,
                              client_id: int,
                              project_data: Dict,
                              session: Optional[Session] = None) -> Optional[Project]:
        """
        Find matching project for a client
        
        Args:
            client_id: Client ID
            project_data: Dict with 'subject', 'body', 'attachments'
            session: Database session (optional)
            
        Returns:
            Project object if match found, None otherwise
        """
        own_session = session is None
        if own_session:
            session = SessionLocal()
        
        try:
            # Extract project reference from email
            project_ref = self.extract_project_reference(project_data)
            
            # Get all projects for this client
            projects = session.query(Project).filter(
                Project.contact_id == client_id,
                Project.status == 'ACTIVE'
            ).all()
            
            if not projects:
                return None
            
            # Try exact reference match first
            if project_ref:
                for project in projects:
                    if project.topic_reference and project_ref.lower() in project.topic_reference.lower():
                        print(f"DONE: Matched project by reference: {project.topic_name}")
                        return project
            
            # Use LLM for similarity matching
            project_name = self._extract_project_name(project_data)
            
            # GENERIC NAMES PROTECTION:
            # If the subject is very generic, do NOT match by similarity alone.
            generic_keywords = [
                'calculation', 'tender', 'procurement', 'itt', 'quotation', 'qutation', 
                'project', 'document', 'package', 'offer', 'quote'
            ]
            
            clean_name = project_name.lower().strip()
            # If name is JUST a generic keyword or starts with one followed by very little else
            is_generic = any(kw in clean_name for kw in generic_keywords)
            
            # If it's short and contains generic keywords, treat as generic
            if is_generic and len(clean_name) < 25:
                print(f"WARN: Subject '{project_name}' is too generic ({len(clean_name)} chars). Skipping similarity match.")
                return None

            for project in projects:
                similarity = self.calculate_similarity(
                    project_name,
                    project.topic_name or ""
                )
                
                # Higher threshold (0.9) for similarity to be safe
                if similarity >= 0.9:  
                    print(f"DONE: Matched project by similarity ({similarity:.0%}): {project.topic_name}")
                    return project
            
            return None
            
        finally:
            if own_session:
                session.close()
    
    def extract_project_reference(self, project_data: Dict) -> str:
        """
        Extract project reference number from email
        
        Args:
            project_data: Dict with email data
            
        Returns:
            Project reference string
        """
        subject = project_data.get('subject', '')
        body = project_data.get('body', '')
        
        # Common patterns for tender references
        patterns = [
            r'Procurement[:\s-]*([A-Z0-9/-]+)',
            r'ITT[:\s-]*([A-Z0-9/-]+)',
            r'Tender[:\s-]*([A-Z0-9/-]+)',
            r'Project[:\s-]*([A-Z0-9/-]+)',
            r'Ref[:\s\.]*([A-Z0-9/-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1)
            
            match = re.search(pattern, body[:500], re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def calculate_similarity(self, project1: str, project2: str) -> float:
        """
        Calculate similarity between two project names using LLM
        
        Args:
            project1: First project name
            project2: Second project name
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not project1 or not project2:
            return 0.0
        
        prompt = f"""
Compare these two project names and determine if they refer to the same project.

Project 1: {project1}
Project 2: {project2}

Return a JSON object with similarity score (0.0 to 1.0):
{{
    "similarity": 0.85,
    "reasoning": "Brief explanation"
}}

Consider:
- Same project name with minor variations = 1.0
- Same location/client but different scope = 0.5
- Completely different projects = 0.0
"""
        
        try:
            result = self.llm.generate(
                system_prompt="You are a project matching expert.",
                user_prompt=prompt,
                temperature=0.1
            )
            
            if isinstance(result, dict) and 'similarity' in result:
                return float(result['similarity'])
            
        except Exception as e:
            print(f"Warning: Similarity calculation failed: {e}")
        
        # Fallback: simple string matching
        if project1.lower() == project2.lower():
            return 1.0
        elif project1.lower() in project2.lower() or project2.lower() in project1.lower():
            return 0.7
        else:
            return 0.0
    
    def create_new_project(self,
                          client_id: int,
                          tender_id: str,
                          project_name: str,
                          project_reference: str = "",
                          session: Optional[Session] = None) -> Project:
        """
        Create new project for a client
        
        Args:
            client_id: Client ID
            tender_id: Tender ID to link
            project_name: Project name
            project_reference: Project reference (optional)
            session: Database session (optional)
            
        Returns:
            New Project object
        """
        own_session = session is None
        if own_session:
            session = SessionLocal()
        
        try:
            # Update client's project count
            client = session.query(Client).filter(Client.id == client_id).first()
            if client:
                client.total_interactions += 1
            
            # Create project
            project = Project(
                contact_id=client_id,
                topic_name=project_name,
                topic_reference=project_reference,
                thread_id=tender_id,
                status='ACTIVE',
                folder_path=f"./storage/tenders/{tender_id}",
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                meta_data={}
            )
            
            session.add(project)
            session.commit()
            session.refresh(project)
            
            print(f"DONE: Created new project: {project_name}")
            return project
            
        finally:
            if own_session:
                session.close()
    
    def _extract_project_name(self, project_data: Dict) -> str:
        """Extract project name from email data"""
        subject = project_data.get('subject', '')
        
        # Simple extraction: use subject as project name
        # Remove common prefixes
        name = subject
        for prefix in ['Procurement:', 'ITT:', 'Tender:', 'Re:', 'FW:', 'Fwd:']:
            name = name.replace(prefix, '')
        
        return name.strip()
