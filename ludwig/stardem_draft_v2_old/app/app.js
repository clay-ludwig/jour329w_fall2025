// Global state
let beatBookContent = "";
let chatHistory = [];

// DOM Elements
const markdownPanel = document.getElementById('markdown-content');
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const modelSelect = document.getElementById('model-select');
const settingsBtn = document.getElementById('settings-btn');
const settingsModal = document.getElementById('settings-modal');
const closeBtn = document.querySelector('.close-btn');
const saveSettingsBtn = document.getElementById('save-settings');

// API Keys
const apiKeys = {
    openai: localStorage.getItem('openai-key') || '',
    anthropic: localStorage.getItem('anthropic-key') || '',
    google: localStorage.getItem('google-key') || ''
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadBeatBook();
    loadSettings();
    setupEventListeners();
});

// Load Markdown Content
async function loadBeatBook() {
    try {
        const response = await fetch('./education_beat_book_refined.md');
        if (!response.ok) throw new Error('Failed to load beat book');
        beatBookContent = await response.text();
        markdownPanel.innerHTML = marked.parse(beatBookContent);
    } catch (error) {
        markdownPanel.innerHTML = `<div class="error">Error loading content: ${error.message}. Make sure you are running this via a local server.</div>`;
        console.error(error);
    }
}

// Settings Management
function loadSettings() {
    document.getElementById('openai-key').value = apiKeys.openai;
    document.getElementById('anthropic-key').value = apiKeys.anthropic;
    document.getElementById('google-key').value = apiKeys.google;
}

function saveSettings() {
    apiKeys.openai = document.getElementById('openai-key').value.trim();
    apiKeys.anthropic = document.getElementById('anthropic-key').value.trim();
    apiKeys.google = document.getElementById('google-key').value.trim();

    localStorage.setItem('openai-key', apiKeys.openai);
    localStorage.setItem('anthropic-key', apiKeys.anthropic);
    localStorage.setItem('google-key', apiKeys.google);

    settingsModal.classList.remove('show');
    addSystemMessage("Settings saved.");
}

// Event Listeners
function setupEventListeners() {
    settingsBtn.addEventListener('click', () => settingsModal.classList.add('show'));
    closeBtn.addEventListener('click', () => settingsModal.classList.remove('show'));
    window.addEventListener('click', (e) => {
        if (e.target === settingsModal) settingsModal.classList.remove('show');
    });
    saveSettingsBtn.addEventListener('click', saveSettings);

    sendBtn.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
}

// Chat Logic
async function handleSendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Add user message
    addMessage(text, 'user');
    userInput.value = '';
    
    // Show loading
    const loadingId = addLoadingIndicator();

    try {
        const model = modelSelect.value;
        let response;

        if (model === 'gpt-5.1') {
            response = await callOpenAI(text);
        } else if (model === 'claude-haiku-4.5') {
            response = await callAnthropic(text);
        } else if (model === 'gemini-3-pro-preview') {
            response = await callGoogle(text);
        }

        removeMessage(loadingId);
        addMessage(response, 'ai');
    } catch (error) {
        removeMessage(loadingId);
        addMessage(`Error: ${error.message}`, 'error');
    }
}

// UI Helpers
function addMessage(text, type) {
    const div = document.createElement('div');
    div.className = `message ${type}`;
    // Parse markdown in AI responses
    div.innerHTML = type === 'ai' ? marked.parse(text) : text.replace(/\n/g, '<br>');
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div.id = 'msg-' + Date.now();
}

function addSystemMessage(text) {
    const div = document.createElement('div');
    div.className = 'message system';
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addLoadingIndicator() {
    const div = document.createElement('div');
    div.className = 'message ai';
    div.innerHTML = '<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>';
    const id = 'loading-' + Date.now();
    div.id = id;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// --- API Implementations ---

// 1. OpenAI (GPT 5.1)
async function callOpenAI(userMessage) {
    if (!apiKeys.openai) throw new Error("OpenAI API Key is missing.");

    const messages = [
        { role: "system", content: "You are an expert on the education beat for the Easton Star-Democrat. You do not have the beat book content in your initial context. You MUST use the `read_beat_book` or `search_beat_book` tools to retrieve information. Be extremely concise and straightforward in your responses." },
        ...chatHistory,
        { role: "user", content: userMessage }
    ];

    const tools = [
        {
            type: "function",
            function: {
                name: "read_beat_book",
                description: "Reads the full content of the education beat book markdown file.",
                parameters: { type: "object", properties: {} }
            }
        },
        {
            type: "function",
            function: {
                name: "search_beat_book",
                description: "Searches for a string in the beat book and returns matching lines with context.",
                parameters: {
                    type: "object",
                    properties: {
                        query: { type: "string", description: "The string to search for." }
                    },
                    required: ["query"]
                }
            }
        }
    ];

    const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${apiKeys.openai}`
        },
        body: JSON.stringify({
            model: "gpt-5.1", // Hypothetical model
            messages: messages,
            tools: tools,
            tool_choice: "auto"
        })
    });

    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error?.message || "OpenAI API Error");
    }

    const data = await response.json();
    let message = data.choices[0].message;

    // Handle Tool Calls
    if (message.tool_calls) {
        messages.push(message); // Add assistant's tool call request
        
        for (const toolCall of message.tool_calls) {
            let content = "";
            if (toolCall.function.name === "read_beat_book") {
                content = beatBookContent;
            } else if (toolCall.function.name === "search_beat_book") {
                const args = JSON.parse(toolCall.function.arguments);
                content = searchBeatBook(args.query);
            }

            messages.push({
                role: "tool",
                tool_call_id: toolCall.id,
                content: content
            });
        }

        // Second call to get final answer
        const secondResponse = await fetch("https://api.openai.com/v1/chat/completions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${apiKeys.openai}`
            },
            body: JSON.stringify({
                model: "gpt-5.1",
                messages: messages
            })
        });

        if (!secondResponse.ok) throw new Error("OpenAI API Error on tool return");
        const secondData = await secondResponse.json();
        message = secondData.choices[0].message;
    }

    chatHistory.push({ role: "user", content: userMessage });
    chatHistory.push({ role: "assistant", content: message.content });
    
    return message.content;
}

// 2. Anthropic (Claude Haiku 4.5)
async function callAnthropic(userMessage) {
    if (!apiKeys.anthropic) throw new Error("Anthropic API Key is missing.");

    // Convert chat history to Anthropic format
    const messages = chatHistory.map(msg => ({
        role: msg.role === 'assistant' ? 'assistant' : 'user',
        content: msg.content
    }));
    messages.push({ role: "user", content: userMessage });

    const tools = [
        {
            name: "read_beat_book",
            description: "Reads the full content of the education beat book markdown file.",
            input_schema: { type: "object", properties: {} }
        },
        {
            name: "search_beat_book",
            description: "Searches for a string in the beat book and returns matching lines with context.",
            input_schema: {
                type: "object",
                properties: {
                    query: { type: "string", description: "The string to search for." }
                },
                required: ["query"]
            }
        }
    ];

    const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
            "x-api-key": apiKeys.anthropic,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "dangerously-allow-browser": "true" // Required for client-side
        },
        body: JSON.stringify({
            model: "claude-haiku-4.5", // Hypothetical model
            max_tokens: 1024,
            system: "You are an expert on the education beat for the Easton Star-Democrat. You do not have the beat book content in your initial context. You MUST use the `read_beat_book` or `search_beat_book` tools to retrieve information. Be extremely concise and straightforward in your responses.",
            messages: messages,
            tools: tools
        })
    });

    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error?.message || "Anthropic API Error");
    }

    const data = await response.json();
    let content = data.content;
    
    // Check for tool use
    const toolUse = content.find(c => c.type === 'tool_use');
    
    if (toolUse) {
        messages.push({ role: "assistant", content: content });
        
        let toolResult = "";
        if (toolUse.name === 'read_beat_book') {
            toolResult = beatBookContent;
        } else if (toolUse.name === 'search_beat_book') {
            toolResult = searchBeatBook(toolUse.input.query);
        }

        if (toolResult) {
            messages.push({
                role: "user",
                content: [
                    {
                        type: "tool_result",
                        tool_use_id: toolUse.id,
                        content: toolResult
                    }
                ]
            });

            // Second call
            const secondResponse = await fetch("https://api.anthropic.com/v1/messages", {
                method: "POST",
                headers: {
                    "x-api-key": apiKeys.anthropic,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                    "dangerously-allow-browser": "true"
                },
                body: JSON.stringify({
                    model: "claude-haiku-4.5",
                    max_tokens: 1024,
                    system: "You are an expert on the education beat for the Easton Star-Democrat.",
                    messages: messages,
                    tools: tools
                })
            });

            if (!secondResponse.ok) throw new Error("Anthropic API Error on tool return");
            const secondData = await secondResponse.json();
            content = secondData.content;
        }
    }

    const textResponse = content.find(c => c.type === 'text')?.text || "No text response";
    
    chatHistory.push({ role: "user", content: userMessage });
    chatHistory.push({ role: "assistant", content: textResponse });

    return textResponse;
}

// 3. Google (Gemini 3 Pro Preview)
async function callGoogle(userMessage) {
    if (!apiKeys.google) throw new Error("Google API Key is missing.");

    // Gemini format is slightly different (parts)
    const contents = chatHistory.map(msg => ({
        role: msg.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: msg.content }]
    }));
    contents.push({ role: "user", parts: [{ text: userMessage }] });

    const tools = {
        function_declarations: [
            {
                name: "read_beat_book",
                description: "Reads the full content of the education beat book markdown file.",
            },
            {
                name: "search_beat_book",
                description: "Searches for a string in the beat book and returns matching lines with context.",
                parameters: {
                    type: "OBJECT",
                    properties: {
                        query: { type: "STRING", description: "The string to search for." }
                    },
                    required: ["query"]
                }
            }
        ]
    };

    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-preview:generateContent?key=${apiKeys.google}`;

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            contents: contents,
            tools: [tools],
            system_instruction: { parts: [{ text: "You are an expert on the education beat for the Easton Star-Democrat. You do not have the beat book content in your initial context. You MUST use the `read_beat_book` or `search_beat_book` tools to retrieve information. Be extremely concise and straightforward in your responses." }] }
        })
    });

    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error?.message || "Google API Error");
    }

    const data = await response.json();
    let candidate = data.candidates[0];
    let parts = candidate.content.parts;

    // Check for function call
    const functionCall = parts.find(p => p.functionCall);

    if (functionCall) {
        let toolResponse = "";
        if (functionCall.functionCall.name === 'read_beat_book') {
            toolResponse = beatBookContent;
        } else if (functionCall.functionCall.name === 'search_beat_book') {
            toolResponse = searchBeatBook(functionCall.functionCall.args.query);
        }

        if (toolResponse) {
            // Add the model's request to history
            contents.push(candidate.content);

            // Add the function response
            contents.push({
                role: "function",
                parts: [{
                    functionResponse: {
                        name: functionCall.functionCall.name,
                        response: { content: toolResponse }
                    }
                }]
            });

            // Second call
            const secondResponse = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    contents: contents,
                    tools: [tools]
                })
            });

            if (!secondResponse.ok) throw new Error("Google API Error on tool return");
            const secondData = await secondResponse.json();
            parts = secondData.candidates[0].content.parts;
        }
    }

    const textResponse = parts.find(p => p.text)?.text || "No text response";

    chatHistory.push({ role: "user", content: userMessage });
    chatHistory.push({ role: "assistant", content: textResponse });

    return textResponse;
}

function searchBeatBook(query) {
    if (!beatBookContent) return "Beat book content not loaded yet.";
    const lines = beatBookContent.split('\n');
    const results = [];
    for (let i = 0; i < lines.length; i++) {
        if (lines[i].toLowerCase().includes(query.toLowerCase())) {
            const start = Math.max(0, i - 2);
            const end = Math.min(lines.length, i + 3);
            results.push(`Line ${i+1}:\n` + lines.slice(start, end).join('\n'));
        }
    }
    return results.length > 0 ? results.join('\n---\n') : "No matches found.";
}
