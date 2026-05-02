// Procurement Agent - API Client
// Handles all communication with FastAPI backend

const API_BASE_URL = window.location.origin;  // FastAPI server

class ProcurementAgentAPI {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    // Generic request handler
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (response.status === 401) {
                Auth.logout();
                throw new Error('Unauthorized');
            }

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Get system status
    async getSystemStatus() {
        return await this.request('/api/status');
    }

    // Get dashboard stats
    async getDashboardStats() {
        return await this.request('/api/dashboard/stats');
    }

    // Get all threads
    async getThreads(filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.request(`/api/threads?${params}`);
    }

    // Get single thread
    async getThread(threadId) {
        return await this.request(`/api/threads/${threadId}`);
    }

    // Trigger email processing
    async processEmails() {
        return await this.request('/api/process-emails', {
            method: 'POST'
        });
    }

    // Get processing status
    async getAgentStatus() {
        return await this.request('/api/agent/status');
    }

    // Get recent activity
    async getRecentActivity(limit = 10) {
        return await this.request(`/api/activity?limit=${limit}`);
    }

    // Get contacts
    async getContacts() {
        return await this.request('/api/contacts');
    }

    // Get attachments (all or for a specific thread)
    async getAttachments(threadId = null) {
        const endpoint = threadId
            ? `/api/threads/${threadId}/attachments`
            : '/api/attachments';
        return await this.request(endpoint);
    }

    // ===== DRAFT EMAIL METHODS =====

    // Get all drafts
    async getDrafts(threadId = null) {
        const endpoint = threadId
            ? `/api/drafts?thread_id=${threadId}`
            : '/api/drafts';
        return await this.request(endpoint);
    }

    // Get single draft
    async getDraft(draftId) {
        return await this.request(`/api/drafts/${draftId}`);
    }

    // Update draft
    async updateDraft(draftId, { subject, body }) {
        return await this.request(`/api/drafts/${draftId}`, {
            method: 'PUT',
            body: JSON.stringify({ subject, body })
        });
    }

    async toggleAttachmentCorrect(attId) {
        return await this.request(`/api/attachments/${attId}/toggle-correct`, {
            method: 'POST'
        });
    }

    async uploadDraftAttachment(draftId, file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.baseURL}/api/drafts/${draftId}/attachments`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    }

    // Send draft
    async sendDraft(draftId) {
        return await this.request(`/api/drafts/${draftId}/send`, {
            method: 'POST'
        });
    }

    // Delete draft
    async deleteDraft(draftId) {
        return await this.request(`/api/drafts/${draftId}`, {
            method: 'DELETE'
        });
    }

    // Get emails
    async getEmails(filters = {}) {
        const params = new URLSearchParams(filters);
        // Map threadId filter if present
        if (filters.tender_id) {
            params.delete('tender_id');
            params.append('thread_id', filters.tender_id);
        }
        return await this.request(`/api/emails?${params}`);
    }

    // Get single email
    async getEmail(emailId) {
        return await this.request(`/api/emails/${emailId}`);
    }

    // Archive email
    async archiveEmail(emailId) {
        return await this.request(`/api/emails/${emailId}/archive`, {
            method: 'POST'
        });
    }

    // Get single attachment
    async getAttachment(attId) {
        return await this.request(`/api/attachments/${attId}`);
    }

    // Delete attachment
    async deleteAttachment(attId) {
        return await this.request(`/api/attachments/${attId}`, {
            method: 'DELETE'
        });
    }

    // Get single contact
    async getContact(contactId) {
        return await this.request(`/api/contacts/${contactId}`);
    }

    // Tag management
    async getTags() {
        return await this.request('/api/tags');
    }

    async createTag(name, color) {
        return await this.request('/api/tags', {
            method: 'POST',
            body: JSON.stringify({ name, color })
        });
    }

    async deleteTag(tagId) {
        return await this.request(`/api/tags/${tagId}`, {
            method: 'DELETE'
        });
    }

    async addTagToEmail(emailId, tagId) {
        return await this.request(`/api/emails/${emailId}/tags/${tagId}`, {
            method: 'POST'
        });
    }

    async removeTagFromEmail(emailId, tagId) {
        return await this.request(`/api/emails/${emailId}/tags/${tagId}`, {
            method: 'DELETE'
        });
    }

    // Procurement Assistant
    async getConversations(mode = 'enterprise') {
        return await this.request(`/api/assistant/conversations?mode=${mode}`);
    }

    async createConversation(title = "New Conversation") {
        return await this.request('/api/assistant/conversations', {
            method: 'POST',
            body: JSON.stringify({ title })
        });
    }

    async deleteConversation(convId) {
        return await this.request(`/api/assistant/conversations/${convId}`, {
            method: 'DELETE'
        });
    }

    async getChatHistory(conversationId = null) {
        const endpoint = conversationId
            ? `/api/assistant/history?conversation_id=${conversationId}`
            : '/api/assistant/history';
        return await this.request(endpoint);
    }

    async askAssistant(message, context = null, conversationId = null, mode = 'enterprise') {
        return await this.request('/api/assistant/chat', {
            method: 'POST',
            body: JSON.stringify({
                query: message,
                context,
                conversation_id: conversationId,
                mode
            })
        });
    }

    async extractTextAssistant(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.baseURL}/api/assistant/extract-text`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    // OAuth status
    async getOAuthStatus() {
        return await this.request('/api/oauth/status');
    }

    // ===== CALENDAR METHODS =====
    async getCalendarEvents(days = 7) {
        return await this.request(`/api/calendar/events?days=${days}`);
    }

    async createCalendarEvent(data) {
        return await this.request('/api/calendar/events', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async deleteCalendarEvent(provider, eventId) {
        return await this.request(`/api/calendar/events/${provider}/${eventId}`, {
            method: 'DELETE'
        });
    }

    // ===== FOLLOW-UP ASSISTANT METHODS =====
    async getFollowups() {
        return await this.request('/api/followups');
    }

    async approveFollowup(taskId) {
        return await this.request(`/api/followups/${taskId}/approve`, {
            method: 'POST'
        });
    }

    async dismissFollowup(taskId) {
        return await this.request(`/api/followups/${taskId}/dismiss`, {
            method: 'POST'
        });
    }

    async bookSuggestedMeeting(threadId, provider = 'google') {
        return await this.request('/api/meetings/book-suggested', {
            method: 'POST',
            body: JSON.stringify({ thread_id: threadId, provider })
        });
    }

    async getTasks() {
        return await this.request('/api/tasks');
    }

    async getMorningBrief() {
        return await this.request('/api/morning-brief');
    }

    async getContactIntelligence(contactId) {
        return await this.request(`/api/contacts/${contactId}/intelligence`);
    }
}

// Create singleton instance
const api = new ProcurementAgentAPI();

// Export for use in other files
window.ProcurementAgentAPI = api;

// Professional Page Loader Logic
window.showLoader = function() {
    const loader = document.getElementById('top-loader');
    if (loader) {
        loader.style.display = 'block';
        loader.style.width = '30%';
        setTimeout(() => { if(loader.style.width === '30%') loader.style.width = '70%'; }, 200);
    }
};

window.hideLoader = function() {
    const loader = document.getElementById('top-loader');
    if (loader) {
        loader.style.width = '100%';
        setTimeout(() => {
            loader.style.display = 'none';
            loader.style.width = '0%';
        }, 300);
    }
};

// Intercept all link clicks for a smoother transition feel
document.addEventListener('click', e => {
    const link = e.target.closest('a');
    if (link && link.href && link.href.startsWith(window.location.origin) && !link.target && !e.ctrlKey && !e.shiftKey) {
        window.showLoader();
    }
});
