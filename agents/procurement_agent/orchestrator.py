from .manager_agent import ManagerAgent
from .researcher_agent import ResearcherAgent
from .writer_agent import WriterAgent
from .auditor_agent import AuditorAgent
from typing import Dict, List
import os

class AgentOrchestrator:
    """
    Coordinates the collaboration between the Manager, Researcher, and Writer agents.
    It manages the data flow and ensures each agent has the context needed to succeed.
    """
    
    def __init__(self):
        self.manager = ManagerAgent()
        self.researcher = ResearcherAgent()
        self.writer = WriterAgent()
        self.auditor = AuditorAgent()

    def process_inquiry(self, 
                        email_data: Dict, 
                        documents: List[Dict] = None, 
                        writing_style_guide: str = "",
                        custom_instructions: str = "") -> Dict:
        """
        Run the complete multi-agent workflow for a single inquiry.
        """
        
        print(f"[ORCHESTRATOR] Starting Multi-Agent workflow for: {email_data.get('subject')}")
        
        # 1. Management Phase
        print("[ORCHESTRATOR] Step 1: Manager analyzing inquiry...")
        analysis = self.manager.analyze_inquiry(
            sender=email_data.get('sender'),
            subject=email_data.get('subject'),
            body=email_data.get('body'),
            attachment_names=[d['filename'] for d in (documents or [])]
        )
        
        if not analysis.get('is_business_inquiry', True):
            print("[ORCHESTRATOR] Manager identified this as non-business. Skipping deep research.")
            return {"status": "SKIPPED", "reason": "Non-business communication"}

        # 2. Research Phase
        print("[ORCHESTRATOR] Step 2: Researcher investigating facts...")
        directives = analysis.get('researcher_directives', [])
        research_results = self.researcher.investigate(
            directives=directives,
            email_context=email_data.get('body', ''),
            document_contexts=documents or []
        )
        
        # 3. Writing Phase
        print("[ORCHESTRATOR] Step 3: Writer drafting response...")
        
        final_draft = self.writer.draft_response(
            sender=email_data.get('sender'),
            subject=email_data.get('subject'),
            strategy=analysis.get('strategic_plan', ''),
            tone=analysis.get('writer_tone', 'Professional'),
            findings=research_results.get('findings', []),
            writing_style_guide=writing_style_guide,
            custom_instructions=custom_instructions
        )
        
        # 4. Auditing Phase (Quality Control)
        print("[ORCHESTRATOR] Step 4: Auditor verifying draft quality...")
        audit_results = self.auditor.review_draft(
            subject=final_draft.get('draft_subject', email_data.get('subject')),
            draft_body=final_draft.get('draft_body', ''),
            strategy=analysis.get('strategic_plan', ''),
            findings=research_results.get('findings', [])
        )
        
        # Revision Loop (Max 1 retry to save time/cost)
        if not audit_results.get('is_approved', True):
            print(f"[ORCHESTRATOR] Auditor REJECTED draft. Feedback: {audit_results.get('revision_feedback')}")
            print("[ORCHESTRATOR] Writer is revising the draft...")
            final_draft = self.writer.draft_response(
                sender=email_data.get('sender'),
                subject=email_data.get('subject'),
                strategy=analysis.get('strategic_plan', ''),
                tone=analysis.get('writer_tone', 'Professional'),
                findings=research_results.get('findings', []),
                writing_style_guide=writing_style_guide,
                custom_instructions=custom_instructions,
                previous_draft=final_draft.get('draft_body', ''),
                revision_feedback=audit_results.get('revision_feedback', '')
            )
            print("[ORCHESTRATOR] Final revised draft complete.")
        else:
            print(f"[ORCHESTRATOR] Auditor APPROVED draft. Score: {audit_results.get('quality_score', 10)}/10")
        
        print("[ORCHESTRATOR] Multi-Agent workflow complete.")
        
        return {
            "status": "SUCCESS",
            "analysis": analysis,
            "research": research_results,
            "audit": audit_results,
            "draft": final_draft
        }
