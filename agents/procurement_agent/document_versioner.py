"""
Document Versioner Module
Handles document version tracking and management
"""
from typing import Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Document
from database.connection import SessionLocal
import os
import re


class DocumentVersioner:
    """Handle document version tracking"""
    
    def get_latest_version(self, 
                          tender_id: str, 
                          filename: str,
                          session: Optional[Session] = None) -> int:
        """
        Get the latest version number for a document
        
        Args:
            tender_id: Tender ID
            filename: Original filename
            session: Database session (optional)
            
        Returns:
            Latest version number (0 if no previous versions)
        """
        own_session = session is None
        if own_session:
            session = SessionLocal()
        
        try:
            # Extract base filename without version suffix
            base_filename = self._get_base_filename(filename)
            
            # Query for all versions of this document
            documents = session.query(Document).filter(
                Document.tender_id == tender_id,
                Document.original_filename.like(f"{base_filename}%")
            ).order_by(Document.version.desc()).all()
            
            if not documents:
                return 0
            
            return documents[0].version
            
        finally:
            if own_session:
                session.close()
    
    def create_versioned_filename(self, 
                                  original: str, 
                                  version: int) -> str:
        """
        Create versioned filename
        
        Args:
            original: Original filename
            version: Version number
            
        Returns:
            Versioned filename (e.g., "Document_v2.pdf")
        """
        if version <= 1:
            return original
        
        # Split filename and extension
        name, ext = os.path.splitext(original)
        
        # Remove existing version suffix if present
        name = re.sub(r'_v\d+$', '', name)
        
        # Add version suffix
        return f"{name}_v{version}{ext}"
    
    def check_if_duplicate(self, 
                          file_hash: str, 
                          tender_id: str,
                          session: Optional[Session] = None) -> Optional[Document]:
        """
        Check if document with same hash already exists
        
        Args:
            file_hash: SHA256 hash of file
            tender_id: Tender ID
            session: Database session (optional)
            
        Returns:
            Document object if duplicate found, None otherwise
        """
        own_session = session is None
        if own_session:
            session = SessionLocal()
        
        try:
            document = session.query(Document).filter(
                Document.tender_id == tender_id,
                Document.file_hash == file_hash
            ).first()
            
            return document
            
        finally:
            if own_session:
                session.close()
    
    def link_versions(self,
                     new_doc_id: int,
                     old_doc_id: int,
                     reason: str,
                     session: Optional[Session] = None):
        """
        Link new document version to previous version
        
        Args:
            new_doc_id: ID of new document
            old_doc_id: ID of previous document
            reason: Reason for new version
            session: Database session (optional)
        """
        own_session = session is None
        if own_session:
            session = SessionLocal()
        
        try:
            new_doc = session.query(Document).filter(
                Document.id == new_doc_id
            ).first()
            
            if new_doc:
                new_doc.previous_version_id = old_doc_id
                new_doc.version_reason = reason
                
                # Mark old document as replaced
                old_doc = session.query(Document).filter(
                    Document.id == old_doc_id
                ).first()
                
                if old_doc:
                    old_doc.replaced_at = datetime.utcnow()
                
                session.commit()
                print(f"DONE: Linked version {new_doc.version} to previous version")
            
        finally:
            if own_session:
                session.close()
    
    def get_version_history(self,
                           tender_id: str,
                           filename: str,
                           session: Optional[Session] = None) -> list:
        """
        Get complete version history for a document
        
        Args:
            tender_id: Tender ID
            filename: Original filename
            session: Database session (optional)
            
        Returns:
            List of Document objects ordered by version
        """
        own_session = session is None
        if own_session:
            session = SessionLocal()
        
        try:
            base_filename = self._get_base_filename(filename)
            
            documents = session.query(Document).filter(
                Document.tender_id == tender_id,
                Document.original_filename.like(f"{base_filename}%")
            ).order_by(Document.version.asc()).all()
            
            return documents
            
        finally:
            if own_session:
                session.close()
    
    def _get_base_filename(self, filename: str) -> str:
        """Remove version suffix from filename"""
        name, ext = os.path.splitext(filename)
        # Remove version suffix like "_v2", "_v3", etc.
        name = re.sub(r'_v\d+$', '', name)
        return f"{name}{ext}"
