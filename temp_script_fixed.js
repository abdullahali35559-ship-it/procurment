
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');
        const chatMessages = document.getElementById('chatMessages');
        const fileInput = document.getElementById('fileInput');
        const uploadPreview = document.getElementById('uploadPreview');
        const fileNameSpan = document.getElementById('fileName');
        const voiceBtn = document.getElementById('voiceBtn');
        const convList = document.getElementById('convList');

        let currentContext = null;
        let currentConversationId = null;

        document.addEventListener('DOMContentLoaded', async () => {
            console.log('AI Assistant page loaded...');

            // Auto-resize textarea
            chatInput.addEventListener('input', () => {
                chatInput.style.height = 'auto';
                chatInput.style.height = chatInput.scrollHeight + 'px';
            });

            // Handle Enter key
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            sendBtn.addEventListener('click', sendMessage);

            // Init Assistant
            await initAssistant();
        });

        async function initAssistant() {
            await loadConversations();
            // Load latest conversation by default if none selected
            if (convList.querySelector('.conv-item')) {
                const latest = convList.querySelector('.conv-item');
                selectConversation(latest.dataset.id);
            }
        }

        async function loadConversations() {
            try {
                const response = await window.ProcurementAgentAPI.getConversations();
                if (response.success) {
                    convList.innerHTML = '';
                    if (response.data.length === 0) {
                        convList.innerHTML = '<div class="p-4 text-center text-muted">No history yet</div>';
                        return;
                    }
                    response.data.forEach(conv => {
                        const div = document.createElement('div');
                        div.className = `conv-item ${currentConversationId == conv.id ? 'active' : ''}`;
                        div.dataset.id = conv.id;
                        div.onclick = () => selectConversation(conv.id);
                        div.innerHTML = `
                            <span class="conv-title" title="${conv.title}">${conv.title}</span>
                            <button class="btn-del-conv" onclick="event.stopPropagation(); deleteConversation(${conv.id})">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"></polyline>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                </svg>
                            </button>
                        `;
                        convList.appendChild(div);
                    });
                } else {
                    convList.innerHTML = '<div class="p-4 text-center text-muted">Error loading history</div>';
                }
            } catch (error) {
                console.error('Error loading conversations:', error);
                convList.innerHTML = '<div class="p-4 text-center text-muted">Connection error</div>';
            }
        }

        async function selectConversation(id) {
            currentConversationId = id;
            // Update UI
            document.querySelectorAll('.conv-item').forEach(el => {
                el.classList.toggle('active', el.dataset.id == id);
            });
            await loadHistory(id);
        }

        async function startNewChat() {
            currentConversationId = null;
            chatMessages.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon"><svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg></div>
                    <h2>New Conversation</h2>
                    <p>Start typing to begin a new chat thread.</p>
                </div>
            `;
            document.querySelectorAll('.conv-item').forEach(el => el.classList.remove('active'));
            chatInput.focus();
        }

        async function deleteConversation(id) {
            if (!confirm('Are you sure you want to delete this conversation?')) return;
            try {
                const response = await window.ProcurementAgentAPI.deleteConversation(id);
                if (response.success) {
                    if (currentConversationId == id) {
                        startNewChat();
                    }
                    await loadConversations();
                }
            } catch (error) {
                console.error('Error deleting conversation:', error);
            }
        }

        async function loadHistory(id = null) {
            try {
                const response = await window.ProcurementAgentAPI.getChatHistory(id);
                if (response.success) {
                    chatMessages.innerHTML = '';
                    if (response.data.length === 0) {
                        chatMessages.innerHTML = '<div class="empty-state"><h2>Empty chat</h2></div>';
                        return;
                    }
                    response.data.forEach(msg => {
                        appendMessage(msg.role, msg.content, false);
                    });
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            } catch (error) {
                console.error('Error loading history:', error);
            }
        }

        async function sendMessage() {
            const text = chatInput.value.trim();
            if (!text && !currentContext) return;

            // Clear empty state
            if (chatMessages.querySelector('.empty-state')) {
                chatMessages.innerHTML = '';
            }

            // Append user message immediately
            appendMessage('user', text);
            chatInput.value = '';
            chatInput.style.height = 'auto';

            // Show typing indicator
            const typingId = showTypingStatus();

            try {
                const response = await window.ProcurementAgentAPI.askAssistant(text, currentContext, currentConversationId);
                removeTypingStatus(typingId);

                if (response.success) {
                    appendMessage('assistant', response.response);
                    // Update current thread if it's new
                    if (!currentConversationId) {
                        currentConversationId = response.conversation_id;
                        await loadConversations();
                    }
                } else {
                    let errorMsg = response.error || "Could not connect to AI.";
                    if (errorMsg.includes("Read timed out")) {
                        errorMsg = "The request timed out. This often happens with large documents. Please try a simpler question or a smaller document.";
                    }
                    appendMessage('assistant', "Error: " + errorMsg);
                }
            } catch (error) {
                removeTypingStatus(typingId);
                let msg = "Connection error. Please ensure the backend is running.";
                if (error.message && error.message.includes("timeout")) {
                    msg = "The request timed out while processing your document. I've increased the processing limit, but please try again.";
                }
                appendMessage('assistant', msg);
            }
        }

        function appendMessage(role, text, shouldScroll = true) {
            const div = document.createElement('div');
            div.className = `message ${role}`;
            div.innerText = text;
            chatMessages.appendChild(div);
            if (shouldScroll) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }

        function showTypingStatus() {
            const id = 'typing-' + Date.now();
            const div = document.createElement('div');
            div.id = id;
            div.className = 'message assistant typing-indicator';
            div.innerHTML = `
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            `;
            chatMessages.appendChild(div);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            return id;
        }

        function removeTypingStatus(id) {
            const el = document.getElementById(id);
            if (el) el.remove();
        }

        async function handleFile(input) {
            if (input.files && input.files[0]) {
                const file = input.files[0];
                fileNameSpan.innerText = "Extracting text: " + file.name + "...";
                uploadPreview.style.display = 'flex';
                uploadPreview.classList.add('loading');

                try {
                    const result = await window.ProcurementAgentAPI.extractTextAssistant(file);
                    if (result && result.success) {
                        currentContext = result.text;
                        fileNameSpan.innerText = "Context attached: " + file.name;
                        uploadPreview.classList.remove('loading');
                    } else {
                        fileNameSpan.innerText = "Error: " + (result ? result.error : "Unknown error");
                        uploadPreview.style.borderColor = 'var(--accent-red)';
                    }
                } catch (error) {
                    console.error('File extraction error:', error);
                    fileNameSpan.innerText = "Error: Could not read file.";
                }
            }
        }

        function clearUpload() {
            fileInput.value = '';
            uploadPreview.style.display = 'none';
            currentContext = null;
        }

        function exportChat() {
            const content = Array.from(chatMessages.querySelectorAll('.message'))
                .map(m => `${m.classList.contains('user') ? 'User' : 'Assistant'}: ${m.innerText}`)
                .join('\n\n');

            const blob = new Blob([content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chat-history-${currentConversationId || 'new'}.txt`;
            a.click();
        }

        // Voice Input Logic
        let recognition = null;
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onstart = () => {
                voiceBtn.classList.add('active');
                chatInput.placeholder = "Listening...";
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                chatInput.value = transcript;
                chatInput.style.height = 'auto';
                chatInput.style.height = (chatInput.scrollHeight) + 'px';
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                voiceBtn.classList.remove('active');
                chatInput.placeholder = "Error: " + event.error;
            };

            recognition.onend = () => {
                voiceBtn.classList.remove('active');
                chatInput.placeholder = "Write your message here...";
            };
        } else {
            if (voiceBtn) voiceBtn.style.display = 'none';
        }

        voiceBtn?.addEventListener('click', () => {
            if (voiceBtn.classList.contains('active')) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    