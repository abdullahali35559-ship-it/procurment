let calendar;
let currentEventDetails = null;

document.addEventListener('DOMContentLoaded', async () => {
    const calendarEl = document.getElementById('calendar');

    // Initialize FullCalendar
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        navLinks: true, // Click day/week names to navigate views
        eventDisplay: 'block',
        eventTimeFormat: {
            hour: 'numeric',
            minute: '2-digit',
            meridiem: 'short'
        },
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        height: 550,
        handleWindowResize: true,
        aspectRatio: 2.1,
        dateClick: function (info) {
            // Pre-fill date and open booking modal
            document.getElementById('bookingDate').value = info.dateStr;
            openBookingModal();
        },
        events: async (info, successCallback, failureCallback) => {
            try {
                const response = await window.ProcurementAgentAPI.getCalendarEvents(30);
                if (response.success) {
                    console.log(`[Calendar] Loaded ${response.data.length} events`);

                    // Populate Sidebar
                    renderUpcomingSidebar(response.data);

                    const formattedEvents = response.data.map(ev => {
                        if (!ev.start) return null;
                        return {
                            id: ev.id,
                            title: ev.title || 'No Title',
                            start: ev.start,
                            end: ev.end,
                            backgroundColor: ev.color || '#primary-orange',
                            borderColor: ev.color || '#primary-orange',
                            extendedProps: {
                                source: ev.source || 'unknown',
                                location: ev.location,
                                description: ev.description,
                                attendees: ev.attendees || [],
                                link: ev.link
                            }
                        };
                    }).filter(e => e !== null);
                    successCallback(formattedEvents);
                } else {
                    failureCallback('Failed to fetch events: ' + (response.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Calendar error:', error);
                failureCallback(error);
            }
        },
        eventClick: (info) => {
            openEventModal(info.event);
        }
    });

    window.fc = calendar; // Expose globally for sidebar access
    calendar.render();

    // Check for deep links from threads
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('attendees') || urlParams.get('title')) {
        setTimeout(() => {
            openBookingModal();
            if (urlParams.get('attendees')) document.getElementById('bookingAttendees').value = urlParams.get('attendees');
            if (urlParams.get('title')) document.getElementById('bookingTitle').value = decodeURIComponent(urlParams.get('title'));
        }, 500);
    }

    // Initialize Flatpickr for booking modal
    if (typeof flatpickr !== 'undefined') {
        flatpickr('#bookingDate', {
            dateFormat: "Y-m-d",
            minDate: "today",
            defaultDate: "today"
        });
        flatpickr('#bookingStartTime', {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            defaultDate: "09:00"
        });
    }
});

function renderUpcomingSidebar(events) {
    const container = document.getElementById('upcoming-list');
    if (!container) return;

    const startOfToday = new Date();
    startOfToday.setHours(0, 0, 0, 0);

    // Filter for events from today onwards and sort by start time
    const sorted = events
        .filter(ev => {
            const start = new Date(ev.start);
            return start >= startOfToday;
        })
        .sort((a, b) => new Date(a.start) - new Date(b.start));
    const upcoming = sorted.slice(0, 15); // Show next 15 events

    if (upcoming.length === 0) {
        container.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-muted); font-size: 0.9rem;">No upcoming appointments</div>';
        return;
    }

    container.innerHTML = '';
    upcoming.forEach(ev => {
        const start = new Date(ev.start);
        const dateStr = start.toLocaleString('en-GB', {
            day: 'numeric',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });

        const card = document.createElement('div');
        card.className = 'appointment-card';
        card.onclick = () => {
            const event = window.fc.getEventById(ev.id);
            if (event) openEventModal(event);
        };

        card.innerHTML = `
            <div class="appointment-badge">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="16" y1="2" x2="16" y2="6"></line>
                    <line x1="8" y1="2" x2="8" y2="6"></line>
                    <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                ${dateStr}
            </div>
            <div class="appointment-info">
                <div class="appointment-name">${ev.title}</div>
                <div class="appointment-status">${ev.source === 'google' ? 'Google' : 'Outlook'}</div>
            </div>
            <div class="appointment-footer">
                ${ev.description || 'View business invitation detail'}
            </div>
        `;
        container.appendChild(card);
    });
}

function openEventModal(event) {
    const props = event.extendedProps;
    const modal = document.getElementById('eventModal');

    // Track current event for deletion
    currentEventDetails = {
        id: event.id,
        provider: props.source
    };

    document.getElementById('modalEventTitle').innerText = event.title;
    document.getElementById('modalEventSource').innerText = props.source.toUpperCase();
    document.getElementById('modalEventSource').className = `badge badge-${props.source === 'google' ? 'info' : 'success'}`;

    // Time formatting
    const start = event.start.toLocaleString([], { weekday: 'long', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    const end = event.end ? ' - ' + event.end.toLocaleString([], { hour: '2-digit', minute: '2-digit' }) : '';
    document.getElementById('modalEventTime').innerText = start + end;

    // Location
    const locRow = document.getElementById('locationRow');
    if (props.location) {
        locRow.style.display = 'block';
        document.getElementById('modalEventLocation').innerText = props.location;
    } else {
        locRow.style.display = 'none';
    }

    // Attendees
    const attContainer = document.getElementById('modalEventAttendees');
    attContainer.innerHTML = '';
    if (props.attendees && props.attendees.length > 0) {
        document.getElementById('attendeesSection').style.display = 'block';
        props.attendees.forEach(att => {
            const span = document.createElement('span');
            span.className = 'badge';
            span.style.cssText = 'background: rgba(107, 114, 128, 0.08); color: var(--text-primary); border: 1px solid var(--border-light); text-transform: none; display: flex; align-items: center; gap: 6px; padding: 6px 10px; font-weight: 500; font-size: 0.8rem;';

            // Status Icon
            let statusIcon = '<div style="width: 8px; height: 8px; border-radius: 50%; background: #9CA3AF;"></div>';
            if (att.response === 'accepted') statusIcon = '<div style="width: 8px; height: 8px; border-radius: 50%; background: #10B981;"></div>';
            if (att.response === 'declined') statusIcon = '<div style="width: 8px; height: 8px; border-radius: 50%; background: #EF4444;"></div>';
            if (att.response === 'needsAction' || att.response === 'tentative') statusIcon = '<div style="width: 8px; height: 8px; border-radius: 50%; background: #F59E0B;"></div>';

            span.innerHTML = `
                ${statusIcon}
                ${att.name || att.email}
                <span style="font-size: 0.65rem; opacity: 0.6; margin-left: 2px;">(${att.response || 'pending'})</span>
            `;
            attContainer.appendChild(span);
        });
    } else {
        document.getElementById('attendeesSection').style.display = 'none';
    }

    // Description
    const descSection = document.getElementById('descriptionSection');
    if (props.description) {
        descSection.style.display = 'block';
        document.getElementById('modalEventDescription').innerText = props.description;
    } else {
        descSection.style.display = 'none';
    }

    // Join Link
    const linkBtn = document.getElementById('modalEventLink');
    const copyBtn = document.getElementById('modalCopyLink');
    if (props.link) {
        linkBtn.style.display = 'inline-flex';
        linkBtn.href = props.link;
        if (copyBtn) {
            copyBtn.style.display = 'inline-flex';
            copyBtn.setAttribute('data-link', props.link);
        }
    } else {
        linkBtn.style.display = 'none';
        if (copyBtn) copyBtn.style.display = 'none';
    }

    modal.classList.add('active');
}

function copyCurrentMeetingLink() {
    const copyBtn = document.getElementById('modalCopyLink');
    const link = copyBtn ? copyBtn.getAttribute('data-link') : null;

    if (link) {
        navigator.clipboard.writeText(link).then(() => {
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = 'Copied! ✅';
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy link:', err);
            showToast('Failed to copy link.', 'error');
        });
    }
}

function closeEventModal() {
    document.getElementById('eventModal').classList.remove('active');
    currentEventDetails = null;
}

async function deleteCurrentEvent() {
    if (!currentEventDetails) return;

    if (!confirm('Are you sure you want to delete this meeting? This will remove it from your calendar.')) {
        return;
    }

    const btn = document.getElementById('deleteEventBtn');
    const originalText = btn.innerText;

    try {
        btn.innerText = 'Deleting...';
        btn.disabled = true;

        const response = await window.ProcurementAgentAPI.deleteCalendarEvent(
            currentEventDetails.provider,
            currentEventDetails.id
        );

        if (response.success) {
            closeEventModal();
            calendar.refetchEvents();
            showToast('Meeting deleted.', 'success');
        } else {
            showToast('Error deleting event: ' + response.error, 'error');
        }
    } catch (err) {
        console.error('Delete error:', err);
        showToast('Failed to delete meeting. Please try again.', 'error');
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

function openBookingModal() {
    // Set default time if not set
    if (!document.getElementById('bookingStartTime').value) {
        document.getElementById('bookingStartTime').value = '09:00';
    }
    // Set default date to today if not set
    if (!document.getElementById('bookingDate').value) {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('bookingDate').value = today;
    }
    const modal = document.getElementById('bookingModal');
    if (modal) {
        modal.classList.add('active');
        modal.style.display = 'flex';
    }
}

function closeBookingModal() {
    const modal = document.getElementById('bookingModal');
    if (modal) {
        modal.classList.remove('active');
        modal.style.display = 'none';
    }
}

async function handleBookingSubmit(event) {
    event.preventDefault();
    const btn = document.getElementById('btnConfirmBooking') || event.target.querySelector('button[type="submit"]');
    if (!btn) return;
    const originalText = btn.textContent;

    try {
        btn.textContent = 'Creating...';
        btn.disabled = true;

        const date = document.getElementById('bookingDate').value;
        const startTime = document.getElementById('bookingStartTime').value;
        const duration = parseInt(document.getElementById('bookingDuration').value);

        // Construct ISO strings
        const start = new Date(`${date}T${startTime}:00`);
        const end = new Date(start.getTime() + duration * 60000);

        const payload = {
            provider: document.getElementById('bookingProvider').value,
            title: document.getElementById('bookingTitle').value,
            start_time: start.toISOString().replace('.000Z', 'Z'),
            end_time: end.toISOString().replace('.000Z', 'Z'),
            description: document.getElementById('bookingDescription').value,
            attendees: document.getElementById('bookingAttendees').value.split(',').map(e => e.trim()).filter(e => e),
            notify_guests: document.getElementById('bookingNotifyGuests').checked
        };

        const response = await window.ProcurementAgentAPI.createCalendarEvent(payload);
        if (response.success) {
            showToast('Meeting confirmed! The client has been notified.', 'success');
            closeBookingModal();
            setTimeout(() => location.reload(), 1500);
        } else {
            showToast('Error: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Booking error:', error);
        showToast('Failed to book meeting: ' + error.message, 'error');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}
