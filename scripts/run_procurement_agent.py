"""
General Email Assistant - Main Workflow Execution
Complete email analysis and professional drafting workflow
"""

import sys
sys.path.append('.')

from agents.procurement_agent.email_detector import EmailDetector
from agents.procurement_agent.document_classifier import DocumentClassifier
from agents.procurement_agent.file_manager import FileManager, generate_tender_id
from agents.procurement_agent.draft_manager import DraftManager
from agents.procurement_agent.orchestrator import AgentOrchestrator
# from agents.procurement_agent.metadata_extractor import MetadataExtractor # Generic now
from agents.procurement_agent.client_matcher import ClientMatcher # To be renamed later
from agents.procurement_agent.project_matcher import ProjectMatcher # To be renamed later
from agents.procurement_agent.document_versioner import DocumentVersioner
from agents.procurement_agent.cloud_link_detector import CloudLinkDetector
from agents.procurement_agent.cloud_file_downloader import CloudFileDownloader
from database.connection import SessionLocal
import re
import os
import json
import zipfile
import io
from typing import Dict, List
from datetime import datetime, timezone
from database.models import Thread, Attachment, Email, DraftReply, AuditLog, Contact, Topic, Tag

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to be safe for filesystem"""
    import re
    return re.sub(r'[^\w\.-]', '_', filename)

def apply_tag_inheritance(db, email_record, contact_id, thread_id):
    """
    Apply tags from:
    1. The same thread (if it exists)
    2. The same contact (if they have history)
    """
    applied_tags = set()
    
    # 1. Inherit from Thread
    if thread_id:
        prev_emails = db.query(Email).filter(
            Email.thread_id == thread_id, 
            Email.id != email_record.id
        ).all()
        for pe in prev_emails:
            for t in pe.tags:
                applied_tags.add(t)
    
    # 2. Inherit from Contact (Only if no thread tags yet, or as supplementary)
    if not applied_tags and contact_id:
        # Get tags from last 50 emails from this contact
        recent_emails = db.query(Email).join(Thread, Email.thread_id == Thread.thread_id)\
            .filter(Thread.contact_id == contact_id)\
            .order_by(Email.received_at.desc())\
            .limit(50).all()
        
        for re in recent_emails:
            for t in re.tags:
                applied_tags.add(t)
    
    # Apply tags
    if applied_tags:
        for tag in applied_tags:
            if tag not in email_record.tags:
                email_record.tags.append(tag)
        print(f"  [+] Inherited {len(applied_tags)} tags from history.")
        return True
    return False

def log_progress(db, thread_id, action, details=None):
    try:
        from datetime import timezone
        log = AuditLog(
            thread_id=thread_id,
            agent="GENERAL_EMAIL_ASSISTANT",
            action=action,
            details=details or {},
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"  [!] Failed to log progress: {e}")
        db.rollback()

def process_incoming_email(email_data: Dict):
    """
    Main workflow for General Email Assistant
    """
    print("=== GENERAL EMAIL ASSISTANT STARTED ===\n")
    
    # Step 1: Junk Filter & Actionability
    print("Step 1: Analyzing actionability...")
    detector = EmailDetector()
    detection = detector.detect_actionable_email(
        email_id=email_data['email_id'],
        subject=email_data['subject'],
        sender=email_data['sender'],
        body=email_data['body'],
        attachments=email_data.get('attachments', [])
    )
    
    if detection.get('is_junk'):
        print(f"❌ JUNK EMAIL detected. Confidence: {detection.get('confidence', 0.0):.2f}. IGNORED.")
        return {"status": "SKIPPED", "reason": "Junk email"}
    
    print(f"DONE: ACTIONABLE email detected (Confidence: {detection.get('confidence', 0.0):.2f})")
    
    db_session = SessionLocal()
    try:
        # Step 2: Contact & Topic Identification
        print("\nStep 2: Identifying contact...")
        client_matcher = ClientMatcher()
        contact = client_matcher.find_or_create_client(
            email_sender=email_data['sender'],
            email_body=email_data['body'],
            session=db_session
        )
        
        print("\nStep 3: Matching topic...")
        project_matcher = ProjectMatcher()
        topic = project_matcher.find_matching_project(
            client_id=contact.id,
            project_data=email_data,
            session=db_session
        )
        
        is_update = topic is not None
        if is_update:
            thread_id = topic.thread_id
            print(f"DONE: Existing topic found: {topic.topic_name}")
        else:
            thread_id = generate_tender_id()
            print(f"DONE: New topic - Generated ID: {thread_id}")
            topic = project_matcher.create_new_project(
                client_id=contact.id,
                tender_id=thread_id,
                project_name=email_data['subject'],
                session=db_session
            )
            
        # Parse sender for thread record
        sender_str = email_data['sender']
        from_email = sender_str
        from_name = sender_str
        if '<' in sender_str and '>' in sender_str:
            from_name = sender_str.split('<')[0].strip()
            from_email = sender_str.split('<')[1].replace('>', '').strip()
            
        # ALWAYS ensure Thread record exists (One project can have multiple threads)
        new_thread = db_session.query(Thread).filter(Thread.thread_id == thread_id).first()
        if not new_thread:
            print(f"  [+] Creating new thread record for {thread_id}...")
            new_thread = Thread(
                thread_id=thread_id,
                status='PROCESSING',
                contact_id=contact.id,
                topic_id=topic.id,
                contact_name=contact.contact_name,
                topic_name=topic.topic_name,
                subject=email_data['subject'],
                source_email=from_email,
                source_sender=from_name,
                created_at=datetime.now(timezone.utc).replace(tzinfo=None)
            )
            db_session.add(new_thread)
        
        # Mark email as processed or create record if it came from API directly
        email_record = db_session.query(Email).filter(Email.email_id == email_data['email_id']).first()
        if not email_record:
            print(f"  [+] Creating new email record for {email_data['email_id']}...")
            email_record = Email(
                email_id=email_data['email_id'],
                thread_id=thread_id,
                subject=email_data['subject'],
                sender=email_data['sender'],
                body=email_data['body'],
                received_at=datetime.utcnow(),
                processed=True
            )
            db_session.add(email_record)
        else:
            email_record.processed = True
            email_record.thread_id = thread_id
        
        db_session.commit()
        db_session.refresh(email_record) # Ensure we have the ID and relationships
        log_progress(db_session, thread_id, "Processing Started")

        # Step 3.5: Apply Tag Inheritance
        if email_record and contact:
            print("Step 3.5: Checking for tag inheritance...")
            try:
                apply_tag_inheritance(db_session, email_record, contact.id, thread_id)
                db_session.commit()
            except Exception as e:
                print(f"  [!] Tag inheritance failed: {e}")
                db_session.rollback()
        else:
            print("Step 3.5: Skipping tag inheritance (Missing email_record or contact)")

        # Step 4: Folder and Cloud Downloads
        file_manager = FileManager()
        thread_folder = file_manager.create_thread_folder(thread_id)
        
        cloud_detector = CloudLinkDetector()
        cloud_downloader = CloudFileDownloader()
        cloud_links = cloud_detector.detect_links(email_data.get('body', ''))
        
        if cloud_links:
            print(f"  [!] Found {len(cloud_links)} cloud links. Tagging email...")
            # Ensure "Cloud Link" tag exists
            cloud_tag = db_session.query(Tag).filter(Tag.name == "Cloud Link").first()
            if not cloud_tag:
                cloud_tag = Tag(name="Cloud Link", color="#8b5cf6") # Purple
                db_session.add(cloud_tag)
                db_session.flush()
            
            if cloud_tag not in email_record.tags:
                email_record.tags.append(cloud_tag)
                db_session.commit()

            print(f"  Downloading from {len(cloud_links)} cloud links...")
            found_urls = [l['url'] for l in cloud_links]
            log_progress(db_session, thread_id, "Links Detected", {"urls": found_urls})
            
            for link in cloud_links:
                try:
                    # Create a "Virtual Attachment" so it shows up in the UI lists
                    link_name = f"[LINK] {link['provider'].value.title()} Documents"
                    new_link_att = Attachment(
                        thread_id=thread_id,
                        category="00_Cloud_Links",
                        filename=link_name,
                        original_filename=link_name,
                        file_path=f"URL:{link['url']}", # Prefix to detect in UI
                        file_hash=f"link_{hash(link['url'])}",
                        doc_type="Cloud Link",
                        summary=f"External documents shared via {link['provider'].value}."
                    )
                    db_session.add(new_link_att)
                    
                    # Currently only handles OneDrive automatically for physical download
                    downloaded = cloud_downloader.download_from_onedrive(link['url'], thread_folder) if link['provider'].value == 'onedrive' else []
                    for file_path in downloaded:
                        with open(file_path, 'rb') as f:
                            if 'cloud_files' not in email_data: email_data['cloud_files'] = []
                            email_data['cloud_files'].append({'filename': os.path.basename(file_path), 'content': f.read()})
                except Exception as e:
                    print(f"  [X] Cloud processing error for {link['url']}: {e}")

        # Step 5: Process Attachments (Flat Storage)
        print("\nStep 5: Processing attachments...")
        classifier = DocumentClassifier()
        versioner = DocumentVersioner()
        processed_docs = []
        
        all_attachments = email_data.get('attachments', []) + email_data.get('cloud_files', [])
        os.makedirs("./temp", exist_ok=True)
        
        for i, att in enumerate(all_attachments, 1):
            filename = sanitize_filename(att['filename'])
            temp_path = os.path.join(os.getcwd(), "temp", filename)
            with open(temp_path, 'wb') as f: f.write(att['content'])
            
            analysis = classifier.classify_document(filename, temp_path)
            
            save_result = file_manager.save_file(
                file_data=att['content'],
                tender_id=thread_id,
                category=analysis.get('category', 'General'),
                original_filename=filename
            )
            
            new_att = Attachment(
                thread_id=thread_id,
                category=analysis.get('category', 'General'),
                filename=save_result['versioned_filename'],
                original_filename=filename,
                file_path=save_result['path'],
                file_hash=save_result['hash'],
                file_size_bytes=save_result['size'],
                doc_type=analysis.get('file_type', 'Document'),
                summary=analysis.get('summary', '')
            )
            db_session.add(new_att)
            processed_docs.append({
                "filename": filename,
                "summary": analysis.get('summary', ''),
                "raw_text": analysis.get('raw_text', ''),
                "file_path": save_result['path']
            })
            if os.path.exists(temp_path): os.remove(temp_path)

        db_session.commit()

        # 1. Fetch User Profile for Style Mirroring
        user = db_session.query(User).first() # In multi-tenant, fetch by ID
        writing_style_guide = user.writing_style_guide if user else ""
        custom_instructions = user.custom_instructions if user else ""

        # 2. Fallback to historical analysis if no style guide exists yet
        if not writing_style_guide:
            print("  [!] No Style Guide found. Falling back to historical email analysis...")
            past_sent = db_session.query(Email).filter(Email.is_sent == True).order_by(Email.received_at.desc()).limit(3).all()
            writing_style_guide = "SAMPLE EMAILS FROM USER:\n" + "\n---\n".join([e.body for e in past_sent if e.body])
            print(f"  [+] Pulled {len(past_sent)} past sent emails for Style Mirroring.")

        print("\nStep 6: Executing Multi-Agent Analysis...")
        orchestrator = AgentOrchestrator()
        
        # Run the collaborative workflow with Style Mirroring
        workflow_result = orchestrator.process_inquiry(
            email_data=email_data,
            documents=processed_docs,
            writing_style_guide=writing_style_guide,
            custom_instructions=custom_instructions
        )
        
        if workflow_result.get('status') == 'SKIPPED':
            print(f"  [!] Workflow skipped: {workflow_result.get('reason')}")
            # Fallback to simple draft if needed, or skip
            return {"status": "SKIPPED", "reason": workflow_result.get('reason')}

        analysis_data = workflow_result.get('analysis', {})
        research_data = workflow_result.get('research', {})
        draft_content = workflow_result.get('draft', {})
        
        provider = email_data.get('provider', 'gmail').lower()
        draft_result = draft_manager.create_draft(
            provider=provider,
            to=email_data['sender'],
            subject=draft_content.get('draft_subject', email_data['subject']),
            body=draft_content.get('draft_body', 'Professional response pending.')
        )
        
        if draft_result['success']:
            new_draft = DraftReply(
                thread_id=thread_id,
                draft_type='REPLY',
                recipient=email_data['sender'],
                subject=draft_content.get('draft_subject', email_data['subject']),
                body=draft_content.get('draft_body', ''),
                email_provider=provider,
                provider_draft_id=draft_result['draft_id'],
                status='DRAFT',
                in_reply_to_email_id=email_data['email_id'],
                meta_data={
                    "multi_agent_analysis": analysis_data,
                    "research_findings": research_data.get('findings', [])
                }
            )
            db_session.add(new_draft)
            print("DONE: Draft reply created successfully.")
        
        # Step 7: Apply AI Insights from Multi-Agent Results
        print("\nStep 7: Applying AI Insights (Tags & Strategy)...")
        
        suggested_tag_names = analysis_data.get('suggested_tags', []) # Ensure Manager returns this or fallback
        if not suggested_tag_names:
            suggested_tag_names = [analysis_data.get('business_segment', 'General')]
            
        action_items = research_data.get('technical_notes', [])
        if isinstance(action_items, str):
            action_items = [action_items]
        
        if email_record:
            if suggested_tag_names:
                email_record.tags_suggested = suggested_tag_names
            
            # Combine strategy and findings into meta_data
            meta = email_record.meta_data or {}
            meta["business_segment"] = analysis_data.get('business_segment')
            meta["priority"] = analysis_data.get('priority')
            meta["strategic_plan"] = analysis_data.get('strategic_plan')
            
            if action_items:
                print(f"  [!] Actionable insights detected.")
                meta["action_items"] = action_items
                
            email_record.meta_data = meta
            
            # AUTOMATIC TAGGING: Create and Apply tags automatically (Fyxer Style)
            for tag_name in suggested_tag_names:
                # Clean name
                tag_name = tag_name.strip()
                if not tag_name: continue
                
                # Find or create tag
                tag = db_session.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    # Generate a random pleasant color for new tags
                    import secrets
                    colors = ["#6366f1", "#8b5cf6", "#ec4899", "#f43f5e", "#f59e0b", "#10b981", "#06b6d4"]
                    tag = Tag(name=tag_name, color=secrets.choice(colors))
                    db_session.add(tag)
                    db_session.flush() # Get ID
                
                # Apply to Email
                if tag not in email_record.tags:
                    email_record.tags.append(tag)
                
                # Apply to Thread (Sync)
                if new_thread and tag not in new_thread.tags:
                    new_thread.tags.append(tag)
            
        db_session.commit()
        print(f"DONE: AI Applied Tags: {suggested_tag_names}")
        
        log_progress(db_session, thread_id, "Processing Complete")
        print("\n=== GENERAL EMAIL ASSISTANT COMPLETE ===")
        return {"status": "SUCCESS", "thread_id": thread_id}
        
    finally:
        db_session.close()

if __name__ == "__main__":
    sample_email = {
        "email_id": "test_gen_001",
        "subject": "Inquiry about your services",
        "sender": "client@example.com",
        "body": "Hi, I would like to know more about your construction services. Please see our requirements attached.",
        "attachments": [{"filename": "Requirements.txt", "content": b"Sample business requirements..."}]
    }
    process_incoming_email(sample_email)
