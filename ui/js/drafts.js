// Procurement Agent - Draft Email Management

const API_BASE = window.location.origin;

document.addEventListener('DOMContentLoaded', async () => {
    console.log('[Drafts] Loading draft emails...');
    await loadDrafts();
});

async function loadDrafts() {
    try {
        const response = await window.ProcurementAgentAPI.getDrafts();
        if (response.success && response.data && response.data.length > 0) {
            displayDrafts(response.data);
        } else {
            console.log('No drafts found');
        }
    } catch (error) {
        console.error('Error loading drafts:', error);
        showToast('Failed to load drafts.', 'error');
    }
}

function displayDrafts(drafts) {
    const container = document.getElementById('draftsList');

    container.innerHTML = drafts.map(draft => `
        <div class="draft-card" data-draft-id="${draft.id}">
            <div class="draft-header">
                <div class="draft-meta">
                    <span class="draft-type">${draft.draft_type || 'DRAFT'}</span>
                    <div class="draft-recipient">To: ${draft.recipient}</div>
                </div>
            </div>
            
            ${draft.meta_data && draft.meta_data.multi_agent_analysis ? `
                <div class="executive-insights" style="background: linear-gradient(135deg, #1e1e2d 0%, #151521 100%); border-radius: 8px; padding: 16px; margin: 12px 0; border-left: 4px solid #6366f1; color: white;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
                        <span style="font-weight: 600; font-size: 14px; display: flex; align-items: center; gap: 8px;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                            Multi-Agent Executive Insights
                        </span>
                        <span style="font-size: 11px; padding: 4px 8px; background: rgba(99, 102, 241, 0.2); border-radius: 12px; color: #a5b4fc; text-transform: uppercase; font-weight: bold;">
                            ${draft.meta_data.multi_agent_analysis.business_segment || 'General'} | 
                            Priority: ${draft.meta_data.multi_agent_analysis.priority || 'Normal'}
                        </span>
                    </div>
                    
                    <div style="font-size: 13px; margin-bottom: 12px;">
                        <strong style="color: #a5b4fc; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">Manager's Strategy:</strong>
                        <p style="margin: 4px 0 0 0; color: #e2e8f0; line-height: 1.5;">${draft.meta_data.multi_agent_analysis.strategic_plan || 'Process standard inquiry.'}</p>
                    </div>

                    ${draft.meta_data.research_findings && draft.meta_data.research_findings.length > 0 ? `
                    <div style="font-size: 13px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px;">
                        <strong style="color: #10B981; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">Researcher Facts Verified:</strong>
                        <ul style="margin: 6px 0 0 0; padding-left: 20px; color: #e2e8f0; list-style-type: disc;">
                            ${draft.meta_data.research_findings.map(f => `<li style="margin-bottom:4px;">${f.fact} <span style="color: #64748b; font-size: 10px;">(Source: ${f.source})</span></li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                </div>
            ` : ''}

            <div 
                class="draft-subject" 
                contenteditable="true" 
                data-field="subject"
                spellcheck="false"
            >${draft.subject}</div>
            
            <div 
                class="draft-body" 
                contenteditable="true"
                data-field="body"
                spellcheck="false"
            >${draft.body}</div>
            
            

            <!-- AI Enhancement Area -->
            <div class="ai-enhance-trigger">
                <button class="btn-ai-toggle" onclick="toggleAI(${draft.id})">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    Enhance with AI
                </button>
            </div>

            <div id="aiContainer-${draft.id}" class="ai-enhance-container">
                <div class="ai-input-wrapper">
                    <input type="text" id="aiInput-${draft.id}" class="ai-input" placeholder="e.g., 'Make it more formal'">
                    <button class="btn-ai-submit" onclick="enhanceDraft(${draft.id})">
                        Enhance
                    </button>
                </div>
                <div class="ai-quick-actions" style="margin-top: 8px; display: flex; gap: 6px;">
                    <button class="btn-ai-toggle" style="background: white; border-color: #DDD6FE; font-size: 10px;" onclick="setAIPrompt(${draft.id}, 'Make it more professional and formal')">Formal</button>
                    <button class="btn-ai-toggle" style="background: white; border-color: #DDD6FE; font-size: 10px;" onclick="setAIPrompt(${draft.id}, 'Make it shorter and direct')">Shorten</button>
                    <button class="btn-ai-toggle" style="background: white; border-color: #DDD6FE; font-size: 10px;" onclick="setAIPrompt(${draft.id}, 'Improve grammar and polish tone')">Polish</button>
                </div>
                <div id="aiReasoning-${draft.id}" class="ai-reasoning" style="display: none;"></div>
            </div>
            
            <div class="draft-attachments-${draft.id}" style="margin-top: 12px; display: flex; flex-wrap: wrap; gap: 8px;">
                <!-- Attachments will be listed here after upload -->
            </div>

            <div class="draft-timestamp">
                Created: ${formatDate(draft.created_at)} | Last updated: ${formatDate(draft.updated_at)}
            </div>

            <div class="draft-actions">
                <button class="btn btn-save" onclick="saveDraft(${draft.id})" style="display: inline-flex !important;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                        <polyline points="17 21 17 13 7 13 7 21"></polyline>
                        <polyline points="7 3 7 8 15 8"></polyline>
                    </svg>
                    Save
                </button>

                <button class="btn btn-ai-toggle" onclick="uploadAttachment(${draft.id})" style="border-radius: var(--radius-md); padding: 8px 16px; border-color: var(--border-light); color: var(--text-secondary);">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
                    </svg>
                    Attach File
                </button>
                
                <button class="btn btn-send" onclick="sendDraft(${draft.id})">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="22" y1="2" x2="11" y2="13"></line>
                        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                    </svg>
                    Send
                </button>
                
                <button class="btn btn-delete" onclick="deleteDraft(${draft.id})">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                </button>
            </div>
        </div>
    `).join('');

    // Add input listeners for auto-save indication
    addEditListeners();
}

async function uploadAttachment(draftId) {
    const input = document.createElement('input');
    input.type = 'file';
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            showLoading(`Attaching ${file.name}...`);
            const result = await window.ProcurementAgentAPI.uploadDraftAttachment(draftId, file);
            hideLoading();

            if (result.success) {
                showToast('File attached successfully!', 'success');
                // Show attachment in UI
                const container = document.querySelector(`.draft-attachments-${draftId}`);
                const badge = document.createElement('span');
                badge.className = 'badge badge-info';
                badge.style.display = 'flex';
                badge.style.alignItems = 'center';
                badge.style.gap = '4px';
                badge.innerHTML = `
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
                    ${file.name}
                `;
                container.appendChild(badge);
            } else {
                showToast('Attachment failed: ' + (result.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            hideLoading();
            console.error('Upload error:', error);
            showToast('Error uploading attachment', 'error');
        }
    };
    input.click();
}

async function saveDraft(draftId) {
    try {
        const card = document.querySelector(`[data-draft-id="${draftId}"]`);
        const subject = card.querySelector('[data-field="subject"]').textContent.trim();
        const body = card.querySelector('[data-field="body"]').textContent.trim();

        showLoading('Saving draft...');
        const result = await window.ProcurementAgentAPI.updateDraft(draftId, { subject, body });
        hideLoading();

        if (result.success) {
            showToast('Draft saved successfully!', 'success');
            await loadDrafts();
        } else {
            showToast(result.error || 'Failed to save draft', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('Error saving draft:', error);
        showToast('Error saving draft', 'error');
    }
}

async function sendDraft(draftId) {
    if (!confirm('Are you sure you want to send this email?')) return;

    try {
        showLoading('Sending email...');
        const result = await window.ProcurementAgentAPI.sendDraft(draftId);
        hideLoading();

        if (result.success) {
            showToast('Email sent successfully!', 'success');
            setTimeout(() => loadDrafts(), 1000);
        } else {
            showToast(result.error || result.detail || 'Failed to send email', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('Error sending draft:', error);
        showToast('Error sending email', 'error');
    }
}

async function deleteDraft(draftId) {
    if (!confirm('Are you sure you want to delete this draft?')) return;

    try {
        showLoading('Deleting draft...');
        const result = await window.ProcurementAgentAPI.deleteDraft(draftId);
        hideLoading();

        if (result.success) {
            showToast('Draft deleted', 'success');
            await loadDrafts();
        } else {
            showToast(result.error || 'Failed to delete draft', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('Error deleting draft:', error);
        showToast('Error deleting draft', 'error');
    }
}

function toggleAI(draftId) {
    const container = document.getElementById(`aiContainer-${draftId}`);
    container.classList.toggle('active');
    if (container.classList.contains('active')) {
        document.getElementById(`aiInput-${draftId}`).focus();
    }
}

function setAIPrompt(draftId, prompt) {
    const input = document.getElementById(`aiInput-${draftId}`);
    input.value = prompt;
    enhanceDraft(draftId);
}

async function enhanceDraft(draftId) {
    const input = document.getElementById(`aiInput-${draftId}`);
    const instructions = input.value.trim();
    if (!instructions) return;

    try {
        const btn = event.currentTarget;
        const originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Working...';

        const response = await fetch(`${API_BASE}/api/drafts/${draftId}/enhance`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({ instructions })
        });

        const data = await response.json();
        btn.disabled = false;
        btn.innerHTML = originalHtml;

        if (data.success) {
            const card = document.querySelector(`[data-draft-id="${draftId}"]`);
            card.querySelector('[data-field="subject"]').textContent = data.subject;
            card.querySelector('[data-field="body"]').textContent = data.body;

            const reasoning = document.getElementById(`aiReasoning-${draftId}`);
            reasoning.style.display = 'flex';
            reasoning.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg> ${data.reasoning}`;

            showToast('Draft enhanced by AI!', 'success');
            input.value = '';
        } else {
            showToast('AI enhancement failed: ' + (data.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error enhancing draft:', error);
        showToast('Error connecting to AI service', 'error');
    }
}

function addEditListeners() {
    const editableElements = document.querySelectorAll('[contenteditable="true"]');

    editableElements.forEach(el => {
        el.addEventListener('input', () => {
            // Visual feedback that content has changed
            el.style.borderColor = 'var(--primary-orange)';
        });

        el.addEventListener('blur', () => {
            // Reset border when not focused
            if (el.textContent.trim()) {
                el.style.borderColor = 'transparent';
            }
        });
    });
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';

    // Ensure UTC interpretation if no offset is present
    let normalized = dateString;
    if (typeof dateString === 'string' && !dateString.includes('Z') && !dateString.includes('+')) {
        normalized += 'Z';
    }

    const date = new Date(normalized);

    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

// UI Helper Functions
function showLoading(message = 'Loading...') {
    const loader = `
        <div id="loading-overlay" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        ">
            <div style="
                background: white;
                padding: 2rem 3rem;
                border-radius: 12px;
                text-align: center;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    border: 4px solid #E2E8F0;
                    border-top-color: #0EA5E9;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 1rem;
                "></div>
                <div>${message}</div>
            </div>
        </div>
        <style>
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    `;
    document.body.insertAdjacentHTML('beforeend', loader);
}

function hideLoading() {
    const loader = document.getElementById('loading-overlay');
    if (loader) {
        loader.remove();
    }
}

function showToast(message, type = 'info') {
    const colors = {
        success: '#10B981',
        error: '#EF4444',
        info: '#0EA5E9'
    };

    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: white;
        color: ${colors[type]};
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border-left: 4px solid ${colors[type]};
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

console.log('[Drafts] Draft management script loaded');
