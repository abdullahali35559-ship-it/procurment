from models.pixtral_client import PixtralClient
from config.prompts import RFQ_AGENT_SYSTEM_PROMPT, Procurement_GENERATION_PROMPT_TEMPLATE, CONSOLIDATED_Procurement_PROMPT_TEMPLATE
from config.settings import REQUIRED_DOCUMENTS, COMPANY_NAME, STORAGE_PATH
import os
from typing import Dict, List
from datetime import datetime

class ProcurementGenerator:
    """Generate Procurement draft emails for missing documents"""
    
    def __init__(self):
        self.llm = PixtralClient()
        self.system_prompt = RFQ_AGENT_SYSTEM_PROMPT
    
    def check_completeness(self, tender_id: str, documents: List[Dict] = None) -> Dict[str, List[str]]:
        """
        Check for missing or incorrect documents, considering all documents in DB for this tender
        
        Args:
            tender_id: Tender ID
            documents: Optional list of documents currently being processed
        
        Returns:
            Dict with 'missing', 'incorrect', and 'irrelevant' lists
        """
        from database.connection import SessionLocal
        from database.models import Document as DocumentModel
        
        db = SessionLocal()
        try:
            # Fetch ALL documents for this tender from database
            db_docs = db.query(DocumentModel).filter(
                DocumentModel.thread_id == tender_id
            ).all()
            
            # Combine with currently processing ones if provided (for same-run awareness)
            all_docs = []
            seen_hashes = set()
            
            # Add DB docs
            for d in db_docs:
                all_docs.append({
                    'category': d.category,
                    'is_correct': d.is_correct,
                    'filename': d.original_filename
                })
                seen_hashes.add(d.file_hash)
            
            # Add currently processing docs (avoid duplicates if already in DB)
            if documents:
                for d in documents:
                    # Use filename/category if hash not available in dict
                    if d.get('file_hash') not in seen_hashes:
                        all_docs.append(d)

            # Get categories present and correct
            present_categories = {doc['category'] for doc in all_docs if doc.get('is_correct', True)}
            
            # Find missing
            missing = []
            base_path = os.path.join(STORAGE_PATH, tender_id)
            
            for category, is_required in REQUIRED_DOCUMENTS.items():
                if is_required and category not in present_categories:
                    # Double check physical folder
                    folder_path = os.path.join(base_path, category)
                    has_physical_files = False
                    if os.path.exists(folder_path):
                        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                        if files:
                            has_physical_files = True
                    
                    if not has_physical_files:
                        missing.append(category)
            
            # Find irrelevant/incorrect
            irrelevant = [doc['filename'] for doc in all_docs if doc.get('category') == '08_Output']
            incorrect_categories = [doc['category'] for doc in all_docs if not doc.get('is_correct', True) and doc.get('category') != '08_Output']
            
            return {
                'missing': missing,
                'incorrect': incorrect_categories,
                'irrelevant': irrelevant
            }
        finally:
            db.close()
    
    def generate_procurement_draft(self, 
                           tender_id: str,
                           missing_category: str,
                           tender_metadata: Dict) -> Dict:
        """
        Generate Procurement draft email for missing document
        
        Returns:
            {
                "procurement_id": str,
                "subject": str,
                "body": str,
                "priority": str,
                "deadline_request": str,
                "status": "DRAFT"
            }
        """
        
        # Map category to human-readable name
        category_names = {
            "01_Instructions": "Tender Instructions",
            "02_Scope_of_Work": "Scope of Work",
            "05_BOQ": "Bill of Quantities (BOQ)",
            "07_Commercial": "Commercial Terms"
        }
        
        missing_item = category_names.get(missing_category, missing_category)
        
        # Build prompt
        current_date_str = datetime.now().strftime("%B %d, %Y")
        user_prompt = Procurement_GENERATION_PROMPT_TEMPLATE.format(
            current_date=current_date_str,
            company_name=COMPANY_NAME,
            tender_id=tender_id,
            missing_item=missing_item,
            client_name=tender_metadata.get('client_name', 'Tender Team'),
            tender_reference=tender_metadata.get('tender_reference', tender_id)
        )
        
        # Few-shot example
        examples = [
            {
                "input": {
                    "current_date": "February 11, 2026",
                    "company_name": "AI Construction Services",
                    "tender_id": "TND-2026-00089",
                    "missing_item": "Bill of Quantities (BOQ)",
                    "client": "NEOM"
                },
                "output": {
                    "subject": "Procurement - Missing BOQ for TND-2026-00089",
                    "body": f"Dear NEOM Tender Team,\n\nWe are processing tender TND-2026-00089 and require the Bill of Quantities (BOQ) to prepare an accurate quotation.\n\nCould you please provide the BOQ file at your earliest convenience?\n\nTender Reference: Procurement-NEOM-2026-089\nDate: {{current_date}}\n\nPlease confirm receipt and expected timeline.\n\nBest regards,\nTender Team\nAI Construction Services",
                    "priority": "HIGH",
                    "deadline_request": "Please provide by 4 days from {{current_date}}"
                }
            }
        ]
        
        # Generate
        result = self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            examples=examples
        )
        
        # Generate Procurement ID
        procurement_id = self._generate_procurement_id(tender_id)
        
        result['procurement_id'] = procurement_id
        result['status'] = 'DRAFT'
        
        return result
    
    def generate_consolidated_procurement_draft(self, 
                                       tender_id: str,
                                       missing_categories: List[str],
                                       incorrect_categories: List[str],
                                       irrelevant_files: List[str],
                                       tender_metadata: Dict) -> Dict:
        """
        Generate ONE consolidated Procurement draft for all missing and incorrect categories
        """
        
        # Map categories to human-readable names
        category_names = {
            "01_Instructions": "Tender Instructions",
            "02_Scope_of_Work": "Scope of Work",
            "03_Drawings": "Drawings (Architectural/Structural/MEP)",
            "04_Specifications": "Technical Specifications",
            "05_BOQ": "Bill of Quantities (BOQ)",
            "06_Standards": "Technical Standards",
            "07_Commercial": "Commercial/Payment Terms"
        }
        
        # Build description list
        issues = []
        for cat in missing_categories:
            issues.append(f"- Missing: {category_names.get(cat, cat)}")
        for cat in incorrect_categories:
            issues.append(f"- Incorrect/Needs Revision: {category_names.get(cat, cat)}")
        
        for file in irrelevant_files:
            issues.append(f"- Irrelevant/Unclear Document: {file} (This file does not appear to be part of the standard tender packages)")
            
        missing_items_list = "\n".join(issues)
        
        # Build prompt
        current_date_str = datetime.now().strftime("%B %d, %Y")
        user_prompt = CONSOLIDATED_Procurement_PROMPT_TEMPLATE.format(
            current_date=current_date_str,
            company_name=COMPANY_NAME,
            tender_id=tender_id,
            missing_items_list=missing_items_list,
            client_name=tender_metadata.get('client_name', 'Tender Team'),
            tender_reference=tender_metadata.get('tender_reference', tender_id)
        )
        
        # Generate
        result = self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt
        )
        
        # Generate Procurement ID
        procurement_id = self._generate_procurement_id(tender_id)
        
        result['procurement_id'] = procurement_id
        result['status'] = 'DRAFT'
        
        return result

    def _generate_procurement_id(self, tender_id: str) -> str:
        """Generate Procurement ID"""
        # TODO: Query database for count
        count = 0  # Placeholder
        return f"{tender_id}-Procurement-{count+1:03d}"
