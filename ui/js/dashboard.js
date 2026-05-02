// Procurement Agent - Executive Dashboard Logic
let forceDisplayUntil = 0;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[Dashboard] Executive Assistant Dashboard Initializing...');

    // Load initial data
    await loadDashboardData();

    // Start polling loops
    setInterval(loadDashboardData, 15000); // Main stats every 15s
    setInterval(checkAgentStatus, 5000);   // Agent status every 5s

    // Welcome message time-awareness
    const hours = new Date().getHours();
    const welcome = document.getElementById('welcomeMessage');
    if (welcome) {
        if (hours < 12) welcome.textContent = "Good morning, Abdullah. Here is your priority list.";
        else if (hours < 18) welcome.textContent = "Good afternoon, Abdullah. Here is your priority list.";
        else welcome.textContent = "Good evening, Abdullah. Here is your priority list.";
    }

    // Initialize Flatpickr for booking modal
    if (typeof flatpickr !== 'undefined') {
        flatpickr('#bookingDate', {
            dateFormat: "Y-m-d",
            minDate: "today",
            defaultDate: "today"
        });
        flatpickr('#bookingTime', {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            defaultDate: "09:00"
        });
    }
});

async function loadDashboardData() {
    try {
        console.log('[Dashboard] Mega-fetching all data...');
        const response = await fetch(`${window.location.origin}/api/dashboard/all`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await response.json();

        if (data.success) {
            // Update Stats
            if (document.getElementById('totalPulledNum')) document.getElementById('totalPulledNum').textContent = data.stats.unprocessedEmails;
            if (document.getElementById('totalMeetingsNum')) document.getElementById('totalMeetingsNum').textContent = data.stats.calendarEvents || 0;

            // Update Brief
            const briefText = document.getElementById('morningBriefText');
            if (briefText) briefText.textContent = data.brief.brief;

            // Update Priority List (Threads)
            renderPriorityList(data.recentThreads);
            
            // Populate others from consolidated if available, or fetch remaining async
            // To keep things moving, we fetch calendar events separately as they are external and slow
            loadAgendaWidget();
            loadHoldQueue();
        }
    } catch (e) {
        console.error('[Dashboard] Consolidated fetch error:', e);
        // Fallback to individual fetches if mega-fetch fails
        await Promise.all([
            loadMorningBrief(),
            loadPriorityList(),
            loadPendingDrafts(),
            loadTasks(),
            loadAgendaWidget(),
            loadHoldQueue(),
            loadPulseStats(),
            loadFollowups()
        ]);
    }
}

function renderPriorityList(threads) {
    const list = document.getElementById('priorityList');
    if (!list) return;
    if (threads.length === 0) {
        list.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);"><p style="font-size: 0.85rem;">No immediate actions required.</p></div>`;
        return;
    }
    list.innerHTML = threads.map(t => `
        <div class="activity-item" onclick="window.location.href='threads.html?id=${t.thread_id}'" style="cursor: pointer;">
            <div style="flex: 1;">
                <div style="font-weight: 600; font-size: 0.9rem;">${t.subject}</div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">From: ${t.contact_name || 'Unknown'}</div>
            </div>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--text-muted);"><polyline points="9 18 15 12 9 6"></polyline></svg>
        </div>
    `).join('');
}

async function loadMorningBrief() {
    const container = document.getElementById('morningBriefContainer');
    const briefText = document.getElementById('morningBriefText');
    if (!container || !briefText) return;

    try {
        const response = await window.ProcurementAgentAPI.getMorningBrief();
        if (response.success && response.brief) {
            briefText.textContent = response.brief;
            container.style.display = 'block';
        }
    } catch (e) { console.error('Morning brief error:', e); }
}

async function triggerSync() {
    const btn = document.getElementById('btnSyncAll');
    const syncContainer = document.getElementById('syncProgressContainer');
    const syncBar = document.getElementById('syncProgressBar');
    const syncPercent = document.getElementById('syncPercentLabel');

    if (!btn || !syncContainer) return;

    const originalContent = btn.innerHTML;
    btn.disabled = true;

    // Show the progress panel
    syncContainer.style.display = 'block';
    syncContainer.style.animation = 'slideDown 0.4s ease-out';

    // Reset Progress
    syncBar.style.width = '0%';
    syncPercent.textContent = '0%';

    // Start status polling
    const statusInterval = setInterval(async () => {
        try {
            const status = await window.ProcurementAgentAPI.getAgentStatus();
            if (status.active) {
                // Calculate percentage
                let percent = 0;
                if (status.total > 0) {
                    percent = Math.round((status.current / status.total) * 100);
                } else {
                    percent = 5;
                }

                // Update UI
                syncBar.style.width = percent + '%';
                syncPercent.textContent = percent + '%';

                // Update Button Spinner
                btn.innerHTML = `
                    <svg class="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" style="margin-right:8px; animation: spin 1s linear infinite;">
                        <path d="M21 12a9 9 0 11-6.219-8.56"></path>
                    </svg>
                    Syncing ${percent}%
                `;
            }
        } catch (e) {
            console.warn('Backend link lost or error. Hiding sync bar.');
            syncContainer.style.display = 'none';
            // Clear interval if error persists to save resources
        }
    }, 1000);

    try {
        const response = await window.ProcurementAgentAPI.processEmails();

        // Wait a tiny bit for the last 100% to show
        setTimeout(async () => {
            clearInterval(statusInterval);

            if (response.success) {
                syncBar.style.width = '100%';
                syncPercent.textContent = '100%';

                showNotice('Sync Complete: ' + (response.processed || 0) + ' items');

                // Refresh data
                await loadDashboardData();

                // Hide panel after 3 seconds
                setTimeout(() => {
                    syncContainer.style.animation = 'fadeOut 0.5s ease-in forwards';
                    setTimeout(() => {
                        syncContainer.style.display = 'none';
                        btn.disabled = false;
                        btn.innerHTML = originalContent;
                    }, 500);
                }, 3000);
            } else {
                clearInterval(statusInterval);
                syncContainer.style.display = 'none';
                btn.disabled = false;
                btn.innerHTML = originalContent;
                showError('Sync Error: ' + (response.error || 'Unknown error'));
            }
        }, 1000);

    } catch (e) {
        clearInterval(statusInterval);
        syncContainer.style.display = 'none';
        btn.disabled = false;
        btn.innerHTML = originalContent;
        showError('Network Error during sync');
    }
}

function showNotice(msg) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed; bottom: 20px; right: 20px; 
        background: var(--primary-orange); color: white; 
        padding: 12px 24px; border-radius: 8px; 
        box-shadow: var(--shadow-lg); z-index: 9999;
        font-weight: 600; animation: slideUp 0.3s ease-out;
    `;
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.5s';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

async function loadTasks() {
    const list = document.getElementById('aiTaskList');
    if (!list) return;

    try {
        console.log('[Dashboard] Loading tasks...');
        const response = await window.ProcurementAgentAPI.getTasks();
        console.log('[Dashboard] Tasks response:', response);

        if (!response || !response.success) {
            throw new Error(response ? response.error : 'No response from API');
        }

        if (response.data && response.data.length > 0) {
            list.innerHTML = response.data.map(t => `
                <div class="activity-item" style="padding: 12px 16px; align-items: center;">
                    <div class="activity-icon-wrapper" style="background: rgba(156, 39, 176, 0.05);">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9c27b0" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                    <div class="activity-content">
                        <div class="activity-title" style="font-size: 0.8rem; font-weight: 500;">${t.task}</div>
                        <div class="activity-meta" style="font-size: 0.65rem;">From: ${t.sender} &nbsp;·&nbsp; ${t.subject.substring(0, 30)}...</div>
                    </div>
                </div>
            `).join('');
        } else {
            list.innerHTML = `<div style="text-align: center; padding: 1.5rem; color: var(--text-muted); font-size: 0.8rem;">No action items identified.</div>`;
        }
    } catch (e) { 
        console.error('Tasks load error:', e); 
        list.innerHTML = `<div style="text-align: center; padding: 1rem; color: var(--accent-red); font-size: 0.8rem;">
            Failed to load tasks.<br>
            <small style="opacity: 0.7;">Error: ${e.message}</small>
        </div>`;
    }
}

async function loadPriorityList() {
    const list = document.getElementById('priorityList');
    try {
        const response = await window.ProcurementAgentAPI.getThreads();
        if (response.success) {
            // Filter for Urgent or Meeting Request or any thread with a meeting suggestion
            const priorities = response.data.filter(t =>
                t.tags.some(tag => ['Urgent', 'Meeting Request', 'High Priority'].includes(tag.name)) ||
                (t.meeting_suggestion && t.meeting_suggestion.start_time)
            ).slice(0, 10); // Increase slice to see more

            if (priorities.length === 0) {
                list.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);"><p style="font-size: 0.85rem;">No immediate actions required. You are up to date.</p></div>`;
                return;
            }

            list.innerHTML = priorities.map(t => {
                const sug = t.meeting_suggestion;
                const hasMeeting = sug && sug.start_time;

                // Cross-check with calendar stats if needed or just use the booked flag
                const isBooked = sug && sug.booked;

                return `
                    <div class="activity-item" style="flex-direction: column; align-items: flex-start; gap: 8px;">
                        <div onclick="window.location.href='threads.html?id=${t.thread_id}'" style="cursor: pointer; width: 100%; display: flex; justify-content: space-between;">
                            <div style="flex: 1;">
                                <div style="font-weight: 600; font-size: 0.9rem; display: flex; align-items: center; gap: 8px;">
                                    <span style="color: ${t.status === 'urgent' ? '#f44336' : (hasMeeting && !isBooked ? '#2196f3' : '#6366f1')};">●</span> ${t.subject}
                                </div>
                                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">
                                    From: ${t.contact_name || 'Unknown'} &nbsp;·&nbsp; ${t.tags.map(tag => `<span class="badge" style="font-size: 0.65rem; padding: 2px 6px; background: ${tag.color}22; color: ${tag.color};">${tag.name}</span>`).join(' ')}
                                </div>
                            </div>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--text-muted);"><polyline points="9 18 15 12 9 6"></polyline></svg>
                        </div>
                        
                        ${hasMeeting && !isBooked ? `
                        <div style="width: 100%; background: rgba(33, 150, 243, 0.05); border: 1px dashed rgba(33, 150, 243, 0.3); border-radius: 6px; padding: 8px; margin-top: 4px; display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-size: 0.75rem; color: var(--text-primary);">
                                <span style="font-weight: 600; color: #2196f3;">Suggested Meeting:</span> ${sug.topic} 
                                <br><span style="color: var(--text-muted); font-size: 0.7rem;">
                                    ${(sug.start_time && !isNaN(new Date(sug.start_time).getTime()))
                            ? new Date(sug.start_time).toLocaleString()
                            : 'Time Pending Confirmation'}
                                </span>
                            </div>
                            <button class="btn btn-primary btn-sm" onclick="bookMeeting('${t.thread_id}')" style="font-size: 0.7rem; padding: 4px 12px; background: #2196f3; border-color: #2196f3; box-shadow: 0 2px 4px rgba(33, 150, 243, 0.2);">
                                Book Now
                            </button>
                        </div>
                        ` : (hasMeeting && isBooked ? `
                        <div style="width: 100%; background: rgba(76, 175, 80, 0.05); border: 1px solid rgba(76, 175, 80, 0.2); border-radius: 6px; padding: 8px; margin-top: 4px; display: flex; align-items: center; gap: 8px;">
                            <div style="width: 20px; height: 20px; border-radius: 50%; background: #4caf50; display: flex; align-items: center; justify-content: center;">
                                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="4"><polyline points="20 6 9 17 4 12"></polyline></svg>
                            </div>
                            <div style="font-size: 0.75rem; color: #2e7d32; font-weight: 600;">Meeting successfully on calendar</div>
                        </div>
                        ` : '')}
                    </div>
                `;
            }).join('');
        }
    } catch (e) { console.error('Priority load error:', e); }
}

async function loadPendingDrafts() {
    const list = document.getElementById('pendingDraftsList');
    try {
        const response = await window.ProcurementAgentAPI.getDrafts();
        if (response.success && response.data) {
            const drafts = (response.data || []).slice(0, 3);
            if (drafts.length === 0) {
                list.innerHTML = `<div style="text-align: center; padding: 1.5rem; color: var(--text-muted); font-size: 0.85rem;">No drafts pending approval.</div>`;
                return;
            }

            list.innerHTML = drafts.map(d => `
                <div class="activity-item" onclick="window.location.href='drafts.html'" style="cursor: pointer;">
                    <div style="flex: 1;">
                        <div style="font-weight: 500; font-size: 0.85rem;">Draft for: ${d.subject}</div>
                        <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 2px;">Recipient: ${d.to}</div>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) { console.error('Drafts load error:', e); }
}

async function loadAgendaWidget() {
    const list = document.getElementById('agendaWidgetList');
    try {
        // Fetch next 7 days to show coming up meetings
        const response = await window.ProcurementAgentAPI.getCalendarEvents(7);
        if (response.success) {
            const now = new Date();
            const upcomingEvents = response.data.filter(ev => {
                if (!ev.start) return false;
                const evDate = new Date(ev.start);
                if (isNaN(evDate.getTime())) return false;
                // Show meetings from today onwards
                const diff = (evDate - now) / (1000 * 60 * 60 * 24);
                return diff >= -0.5 && diff <= 7;
            }).sort((a, b) => new Date(a.start) - new Date(b.start)).slice(0, 5);

            const titleEl = document.querySelector('#agendaWidgetList').previousElementSibling.querySelector('.card-title');
            if (titleEl) titleEl.textContent = "Coming Up on Calendar";

            if (upcomingEvents.length === 0) {
                list.innerHTML = `<div style="text-align: center; padding: 1.5rem; color: var(--text-muted);">
                    <p style="font-size: 0.85rem;">No meetings scheduled for this week.</p>
                </div>`;
                return;
            }

            list.innerHTML = upcomingEvents.map(ev => {
                const startDate = new Date(ev.start);
                const timeStr = startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                const isToday = startDate.toDateString() === now.toDateString();
                const dayStr = isToday ? 'Today' : startDate.toLocaleDateString([], { weekday: 'short', day: 'numeric', month: 'short' });
                const isHold = ev.title.includes('[HOLD]');

                const attendees = ev.attendees || [];
                const attendeeText = attendees.length > 0 ? `<div style="font-size: 0.65rem; color: var(--text-muted); margin-top: 2px;">With: ${attendees.map(a => a.name || a.email.split('@')[0]).join(', ')}</div>` : '';

                return `
                    <div class="activity-item" style="padding: 12px 16px; ${isHold ? 'background: rgba(14, 165, 233, 0.04);' : ''}">
                        <div style="width: 70px; font-weight: 700; font-size: 0.75rem; color: ${isHold ? 'var(--text-muted)' : 'var(--primary-orange)'}; line-height: 1.2;">
                            <div>${timeStr}</div>
                            <div style="font-size: 0.65rem; color: var(--text-muted); font-weight: 400;">${dayStr}</div>
                        </div>
                        <div style="flex: 1;">
                            <div style="font-weight: 600; font-size: 0.85rem; color: var(--text-primary);">
                                ${isHold ? '<span style="color: var(--primary-orange); font-size: 0.65rem; background: #FFF4F0; padding: 1px 4px; border-radius: 4px; margin-right: 4px;">HOLD</span>' : ''}
                                ${ev.title.replace('[HOLD]', '')}
                            </div>
                            ${attendeeText}
                            <div style="font-size: 0.65rem; color: var(--text-muted); display: flex; align-items: center; gap: 4px; margin-top: 4px;">
                                <div style="width: 6px; height: 6px; border-radius: 50%; background: ${ev.color}; opacity: 0.8;"></div>
                                ${ev.source}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }
    } catch (e) { console.error('Agenda load error:', e); }
}

async function loadHoldQueue() {
    const card = document.getElementById('approvalCenterCard');
    const list = document.getElementById('holdQueueList');
    const badge = document.getElementById('holdCountBadge');
    if (!card || !list) return;

    try {
        const response = await window.ProcurementAgentAPI.getCalendarEvents(7);
        if (response.success) {
            const holds = response.data.filter(ev => ev.title.includes('[HOLD]'));

            if (badge) badge.textContent = `${holds.length} Pending`;
            card.style.display = holds.length > 0 ? 'block' : 'none';

            if (holds.length === 0) {
                list.innerHTML = '';
                return;
            }

            list.innerHTML = holds.map(h => {
                const attendees = h.attendees || [];
                const attendeeLabel = attendees.length > 0
                    ? `<div style="font-size:0.75rem; color:var(--text-secondary); background:rgba(0,0,0,0.03); padding:4px 8px; border-radius:6px; margin-top:8px; display:inline-block;">
                        <strong>Participants:</strong> ${attendees.map(a => a.name || a.email.split('@')[0]).join(', ')}
                       </div>`
                    : '<div style="font-size:0.7rem; color:var(--text-muted); margin-top:8px; font-style:italic;">No other participants added</div>';

                return `
                <div class="activity-item" style="padding: 16px; flex-direction: column; align-items: flex-start; gap: 10px; border-left: 3px solid var(--primary-orange);">
                    <div style="display: flex; justify-content: space-between; width: 100%; align-items: flex-start;">
                        <div style="flex: 1;">
                            <div style="font-weight: 700; font-size: 0.95rem; color: var(--text-primary);">${h.title.replace('[HOLD]', '').trim()}</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">
                                Scheduled: ${new Date(h.start).toLocaleString()} (${h.source})
                            </div>
                            ${attendeeLabel}
                        </div>
                        <div class="badge" style="background: rgba(14, 165, 233, 0.1); color: var(--primary-orange); font-weight: 700; letter-spacing: 0.5px;">PENDING APPROVAL</div>
                    </div>
                    <div style="display: flex; gap: 8px; width: 100%; margin-top: 5px;">
                        <button class="btn btn-primary btn-sm" onclick="confirmHold('${h.source}', '${h.id}')" style="flex: 1; font-size: 0.78rem; padding: 10px; font-weight: 600;">
                            Approve & Notify Client
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="ProcurementAgentAPI.deleteCalendarEvent('${h.source}', '${h.id}').then(() => loadDashboardData())" style="padding: 10px; border-color: #fecaca; background: #fef2f2; color: #ef4444;">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path></svg>
                        </button>
                    </div>
                </div>
                `;
            }).join('');
        }
    } catch (e) {
        console.error('[HoldQueue] Error loading:', e);
    }
}

async function confirmHold(provider, eventId) {
    try {
        showLoading('Confirming meeting & sending notifications...');
        const resp = await fetch(`${window.location.origin}/api/calendar/events/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ provider, event_id: eventId })
        });
        const result = await resp.json();
        hideLoading();

        if (result.success) {
            showToast('Meeting confirmed! The client has been notified.', 'success');
            loadDashboardData();
        } else {
            showError('Confirmation failed: ' + result.error);
        }
    } catch (e) {
        hideLoading();
        showError('Network error during confirmation.');
    }
}

async function loadPulseStats() {
    try {
        const response = await window.ProcurementAgentAPI.getDashboardStats();
        if (response.success) {
            console.log('[Dashboard] Pulse Stats updated:', response.data);
            if (document.getElementById('totalPulledNum')) {
                document.getElementById('totalPulledNum').textContent = response.data.unprocessedEmails || 0;
            }
            if (document.getElementById('totalMeetingsNum')) {
                document.getElementById('totalMeetingsNum').textContent = response.data.calendarEvents || 0;
            }
        }
    } catch (e) { }
}

async function loadFollowups() {
    const list = document.getElementById('followupList');
    const badge = document.getElementById('followupCountBadge');
    if (!list) return;

    try {
        console.log('[Dashboard] Loading follow-ups...');
        const response = await window.ProcurementAgentAPI.getFollowups();
        console.log('[Dashboard] Follow-ups response:', response);

        if (!response || !response.success) {
            throw new Error(response ? response.error : 'No response from API');
        }

        const followups = response.data || [];

        if (badge) {
            badge.textContent = `${followups.length} Pending`;
            badge.style.display = followups.length > 0 ? 'inline-block' : 'none';
        }

        if (followups.length === 0) {
            list.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted); font-size: 0.85rem;">
                <p>No stale threads detected. All threads are current.</p>
            </div>`;
            return;
        }

        list.innerHTML = followups.map(f => `
            <div class="activity-item" style="flex-direction: column; align-items: flex-start; gap: 8px; padding: 16px;">
                <div style="width: 100%; display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 0.9rem; color: var(--text-primary);">${f.subject}</div>
                        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">To: ${f.recipient}</div>
                    </div>
                    <div style="font-size: 0.7rem; color: #9c27b0; font-weight: 600; background: rgba(156, 39, 176, 0.05); padding: 2px 8px; border-radius: 4px;">
                        No reply in 3 days
                    </div>
                </div>
                
                <div style="background: var(--bg-light); padding: 12px; border-radius: 8px; width: 100%; font-size: 0.8rem; border: 1px solid var(--border-light); line-height: 1.4; color: var(--text-secondary);">
                    "${f.suggested_body.substring(0, 150)}${f.suggested_body.length > 150 ? '...' : ''}"
                </div>
                
                <div style="display: flex; gap: 8px; margin-top: 4px; width: 100%;">
                    <button class="btn btn-primary btn-sm" onclick="approveFollowup(${f.id})" style="background: #9c27b0; border-color: #9c27b0; font-size: 0.75rem; padding: 6px 12px;">
                        Approve Draft
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="dismissFollowup(${f.id})" style="font-size: 0.75rem; padding: 6px 12px;">
                        Dismiss
                    </button>
                </div>
            </div>
        `).join('');

    } catch (e) {
        console.error('[Dashboard] Follow-up load error:', e);
        list.innerHTML = `<div style="text-align: center; padding: 1rem; color: var(--accent-red); font-size: 0.8rem;">
            Failed to load follow-up suggestions.<br>
            <small style="opacity: 0.7;">Error: ${e.message}</small>
        </div>`;
    }
}

async function approveFollowup(id) {
    try {
        showLoading('Creating draft...');
        const result = await window.ProcurementAgentAPI.approveFollowup(id);
        hideLoading();

        if (result.status === 'success') {
            showSuccess('Follow-up draft created in your mailbox!');
            loadDashboardData(); // Refresh UI
        } else {
            showError('Failed to create draft.');
        }
    } catch (e) {
        hideLoading();
        showError('Error creating follow-up draft: ' + e.message);
    }
}

let currentBookingThreadId = null;

async function bookMeeting(threadId) {
    currentBookingThreadId = threadId;
    try {
        showLoading('Loading suggestion details...');
        const response = await window.ProcurementAgentAPI.getThreads();
        hideLoading();

        const thread = response.data.find(t => t.thread_id === threadId);

        if (thread && thread.meeting_suggestion) {
            const sug = thread.meeting_suggestion;

            document.getElementById('bookingTitle').value = sug.topic || thread.subject;
            document.getElementById('bookingAttendees').value = thread.sender_email || "";

            const start = new Date(sug.start_time);
            if (!isNaN(start.getTime())) {
                document.getElementById('bookingDate').value = start.toISOString().split('T')[0];
                document.getElementById('bookingTime').value = start.toTimeString().split(' ')[0].substring(0, 5);
            } else {
                // Fallback to today if invalid
                const today = new Date();
                document.getElementById('bookingDate').value = today.toISOString().split('T')[0];
                document.getElementById('bookingTime').value = "10:00";
            }

            if (document.getElementById('bookingProvider')) {
                document.getElementById('bookingProvider').value = 'google'; // Default
            }

            openBookingModal();
        } else {
            showError('No meeting suggestion found for this thread.');
        }
    } catch (e) {
        hideLoading();
        showError('Could not load suggestion: ' + e.message);
    }
}

function openBookingModal() {
    console.log("DEBUG: Opening Booking Modal");
    const modal = document.getElementById('bookingModal');
    if (modal) {
        modal.classList.add('active');
        modal.style.display = 'flex';
        // Add one-time listener for outside click
        const outsideClickListener = (e) => {
            if (e.target === modal) {
                closeBookingModal();
                modal.removeEventListener('click', outsideClickListener);
            }
        };
        modal.addEventListener('click', outsideClickListener);
    }
}

function closeBookingModal() {
    console.log("DEBUG: Closing Booking Modal (Force)");
    const modal = document.getElementById('bookingModal');
    if (modal) {
        modal.classList.remove('active');
        // Force hide with style if class removal fails to trigger CSS
        modal.style.display = 'none';

        // Remove 'active' class from all other potential modals just in case
        document.querySelectorAll('.modal').forEach(m => {
            m.classList.remove('active');
            m.style.display = 'none';
        });
    }
    currentBookingThreadId = null;

    // Also reset form fields
    const fields = ['bookingTitle', 'bookingAttendees', 'bookingDate', 'bookingTime'];
    fields.forEach(f => {
        const el = document.getElementById(f);
        if (el) el.value = '';
    });
}

// Global escape key listener
window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeBookingModal();
    }
});

// Expose to window for inline onclicks
window.closeBookingModal = closeBookingModal;
window.openBookingModal = openBookingModal;
window.bookMeeting = bookMeeting;
window.handleBookingSubmit = handleBookingSubmit;

async function handleBookingSubmit(event) {
    event.preventDefault();
    const btn = document.getElementById('btnConfirmBooking');
    const originalText = btn.textContent;

    const attendeesRaw = document.getElementById('bookingAttendees').value;
    const attendees = attendeesRaw.split(',').map(e => e.trim()).filter(e => e);

    // Email Validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    for (const email of attendees) {
        if (!emailRegex.test(email)) {
            showError(`Invalid email address: ${email}`);
            return;
        }
    }

    btn.disabled = true;
    btn.textContent = 'Scheduling...';

    try {
        const date = document.getElementById('bookingDate').value;
        const time = document.getElementById('bookingTime').value;
        const start = new Date(`${date}T${time}:00`);
        const end = new Date(start.getTime() + 60 * 60000); // Default 1 hour

        const meetingData = {
            title: document.getElementById('bookingTitle').value,
            attendees: document.getElementById('bookingAttendees').value.split(',').map(e => e.trim()).filter(e => e),
            start_time: start.toISOString(),
            end_time: end.toISOString(),
            provider: document.getElementById('bookingProvider').value,
            description: `Booked via Dashboard Suggestion for Thread: ${currentBookingThreadId}`,
            thread_id: currentBookingThreadId,
            notify_guests: document.getElementById('bookingNotifyGuests').checked
        };

        const result = await window.ProcurementAgentAPI.createCalendarEvent(meetingData);
        if (result.success) {
            showSuccess('Meeting scheduled successfully.');
            closeBookingModal();
            loadDashboardData();
        } else {
            showError('Failed: ' + (result.error || 'Unknown error'));
        }
    } catch (e) {
        showError('Error: ' + e.message);
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

// Load recent activity - empty for compat
async function loadRecentActivity() { }

// ── SESSION SUMMARY WIDGET ────────────────────────────────────────────────

function toLocalISOString(d) {
    // Returns YYYY-MM-DDTHH:MM suitable for datetime-local input
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function applyPreset(preset) {
    const now = new Date();
    let from, to;

    if (preset === 'today') {
        from = new Date(now); from.setHours(0, 0, 0, 0);
        to = new Date(now); to.setHours(23, 59, 59, 999);
    } else if (preset === '8h') {
        from = new Date(now.getTime() - 8 * 60 * 60 * 1000);
        to = now;
    } else if (preset === '24h') {
        from = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        to = now;
    } else if (preset === 'week') {
        from = new Date(now); from.setDate(now.getDate() - 7); from.setHours(0, 0, 0, 0);
        to = now;
    }

    document.getElementById('sessionFrom').value = toLocalISOString(from);
    document.getElementById('sessionTo').value = toLocalISOString(to);

    // Highlight active preset button
    document.querySelectorAll('[id^="preset-"]').forEach(b => {
        b.classList.remove('btn-primary');
        b.classList.add('btn-secondary');
    });
    const btn = document.getElementById(`preset-${preset}`);
    if (btn) { btn.classList.remove('btn-secondary'); btn.classList.add('btn-primary'); }

    loadSessionSummary();
}

async function loadSessionSummary() {
    const fromValRaw = document.getElementById('sessionFrom').value;
    const toValRaw = document.getElementById('sessionTo').value;
    const results = document.getElementById('sessionResults');

    if (!fromValRaw || !toValRaw) {
        results.innerHTML = `<p style="color:var(--accent-red);padding:1rem;">Please select both From and To times.</p>`;
        return;
    }

    results.innerHTML = `<div style="text-align:center;padding:1.5rem;color:var(--text-muted);">
        <div style="width:28px;height:28px;border:3px solid #e5e7eb;border-top-color:var(--primary-orange);border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 8px;"></div>
        Loading...
    </div>`;

    try {
        // Convert local HTML input values to standard UTC ISO strings for backend
        const fromVal = new Date(fromValRaw).toISOString();
        const toVal = new Date(toValRaw).toISOString();

        const resp = await fetch(`${window.location.origin}/api/session-summary?from_time=${encodeURIComponent(fromVal)}&to_time=${encodeURIComponent(toVal)}`);
        const data = await resp.json();

        if (!data.success) throw new Error(data.detail || 'API error');

        if (data.count === 0) {
            results.innerHTML = `
                <div style="text-align:center;padding:2rem;color:var(--text-muted);">
                    <svg width="36" height="36" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" style="margin:0 auto 8px;display:block;opacity:0.4"><path d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7"/><path d="M4 13h16v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6z"/></svg>
                    <p style="font-size:0.9rem;">No communication threads processed in this time window.</p>
                </div>`;
            return;
        }

        const rows = data.data.map(e => `
            <div class="activity-item" style="display:grid;grid-template-columns:1fr auto;gap:12px;align-items:center;padding:12px 16px;">
                <div>
                    <div style="font-weight:600;font-size:0.88rem;color:var(--text-primary);">${e.subject || '(No Subject)'}</div>
                    <div style="font-size:0.78rem;color:var(--text-muted);margin-top:2px;">
                        From: ${e.sender || '—'} &nbsp;·&nbsp;
                        Processed: ${e.processed_at ? new Date(e.processed_at).toLocaleString() : '—'}
                    </div>
                </div>
                <div style="display:flex;gap:8px;align-items:center;flex-shrink:0;">
                    ${e.thread_id ? `<span style="background:#FFF4F0;color:var(--primary-orange);font-size:0.72rem;font-weight:700;padding:3px 8px;border-radius:20px;border:1px solid #FFD5CC;">${e.thread_id}</span>` : ''}
                    <span style="background:#D1FAE5;color:#065F46;font-size:0.72rem;font-weight:600;padding:3px 8px;border-radius:20px;">${e.att_count} file${e.att_count !== 1 ? 's' : ''}</span>
                </div>
            </div>`).join('');

        results.innerHTML = `
            <div style="font-size:0.78rem;color:var(--text-muted);padding:8px 16px;border-bottom:1px solid var(--border-light);background:var(--bg-light);border-radius:var(--radius-md) var(--radius-md) 0 0;">
                Found <strong>${data.count}</strong> thread${data.count !== 1 ? 's' : ''} processed between
                <strong>${new Date(fromVal).toLocaleString()}</strong> and <strong>${new Date(toVal).toLocaleString()}</strong>
            </div>
            ${rows}`;
    } catch (err) {
        results.innerHTML = `<p style="color:var(--accent-red);padding:1rem;">Error: ${err.message}</p>`;
        console.error('Session summary error:', err);
    }
}

// Note: applyPreset('today') is now handled in the main DOMContentLoaded listener

// Quick Action: Process Emails
// Note: This is now handled in the main checkAgentStatus loop and processEmails trigger below.
async function processEmails() {
    try {
        // Show progress panel immediately and force it to stay for 30s
        const panel = document.getElementById('progressPanel');
        if (panel) {
            panel.style.display = 'block';
            document.getElementById('progressStatus').textContent = 'Starting agent...';
            document.getElementById('progressBar').style.width = '5%';
            document.getElementById('progressPercent').textContent = '5%';
            document.getElementById('progressLogs').innerHTML = '<div style="color:var(--primary-orange);font-style:italic;">Initializing connection...</div>';
        }

        forceDisplayUntil = Date.now() + 30000;

        await window.ProcurementAgentAPI.processEmails();
        showSuccess(`Processing started!`);

    } catch (error) {
        showError('Failed to start processing. Make sure backend is running.');
        console.error(error);
    }
}

async function checkAgentStatus() {
    try {
        const response = await window.ProcurementAgentAPI.getAgentStatus();
        const premiumBadge = document.getElementById('premiumStatus');
        const premiumText = document.getElementById('premiumStatusText');

        if (!premiumBadge) return;

        const isTriggered = Date.now() < forceDisplayUntil;

        if (response.success && (response.is_active || isTriggered)) {
            premiumBadge.style.display = 'flex';

            const logs = response.latest_logs || [];
            if (logs.length > 0) {
                const latest = logs[0];
                let statusText = "AI is Working...";

                const actionLower = latest.action.toLowerCase();
                if (actionLower.includes('processing file')) {
                    const match = latest.action.match(/(\d+)\/(\d+)/);
                    if (match) statusText = `AI Indexing... ${Math.floor((match[1] / match[2]) * 100)}%`;
                } else if (actionLower.includes('classifying')) {
                    statusText = "AI Classifying...";
                } else if (actionLower.includes('complete')) {
                    statusText = "AI Sync Complete";
                    forceDisplayUntil = 0;
                    setTimeout(() => premiumBadge.style.display = 'none', 5000);
                }

                premiumText.textContent = statusText;
            }
        } else {
            premiumBadge.style.display = 'none';
        }
    } catch (err) {
        console.error('Error checking agent status:', err);
    }
}

// Quick Action: View Threads
function viewThreads() {
    window.location.href = 'threads.html';
}

// Quick Action: Check System Status
async function checkSystem() {
    try {
        showLoading('Checking system status...');

        const status = await window.ProcurementAgentAPI.getSystemStatus();

        hideLoading();

        // Show status modal
        showSystemStatus(status);

    } catch (error) {
        hideLoading();
        showError('Could not reach backend server. Make sure FastAPI is running on port 8000.');
        console.error(error);
    }
}

// Quick Action: Open Settings
function openSettings() {
    window.location.href = 'settings.html';
}

// Show system status modal
function showSystemStatus(status) {
    const modal = `
        <div class="modal">
            <div class="modal-content">
                <h2>System Status</h2>
                <div class="status-grid">
                    <div class="status-item">
                        <span class="status-indicator ${status.database ? 'status-online' : 'status-offline'}"></span>
                        <span>Database: ${status.database ? 'Connected' : 'Disconnected'}</span>
                    </div>
                    <div class="status-item">
                        <span class="status-indicator ${status.gmail ? 'status-online' : 'status-offline'}"></span>
                        <span>Gmail: ${status.gmail ? 'Connected' : 'Not configured'}</span>
                    </div>
                    <div class="status-item">
                        <span class="status-indicator ${status.outlook ? 'status-online' : 'status-offline'}"></span>
                        <span>Outlook: ${status.outlook ? 'Connected' : 'Not configured'}</span>
                    </div>
                    <div class="status-item">
                        <span class="status-indicator ${status.llm ? 'status-online' : 'status-offline'}"></span>
                        <span>LLM: ${status.llm ? 'Online' : 'Offline'}</span>
                    </div>
                </div>
                <button class="btn btn-primary" onclick="closeModal()">Close</button>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modal);
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
                    border: 4px solid #E5E7EB;
                    border-top-color: #2563EB;
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

function showSuccess(message) {
    showToast(message, 'success');
}

function showError(message) {
    showToast(message, 'error');
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

function closeModal() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
    }
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .modal {
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
    }
    
    .modal-content {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        min-width: 400px;
        max-width: 90%;
    }
    
    .status-grid {
        display: grid;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        background: var(--bg-light);
        border-radius: 8px;
    }
`;
document.head.appendChild(style);

console.log('📊 Dashboard script loaded');
