// Global state
let tagsData = [];
let filteredData = [];
let currentSort = { column: 'count', order: 'desc' };

// Virtual scrolling configuration
const ROW_HEIGHT = 45; // Height of each table row in pixels
const BUFFER_SIZE = 10; // Number of extra rows to render above/below viewport
let virtualScrollState = {
    startIndex: 0,
    endIndex: 0,
    scrollTop: 0,
    viewportHeight: 0
};

// DOM elements
const tagsTableBody = document.getElementById('tagsTableBody');
const searchInput = document.getElementById('searchInput');
const tagCount = document.getElementById('tagCount');
const loadingIndicator = document.getElementById('loadingIndicator');
const tableHeaders = document.querySelectorAll('th[data-column]');
const sidebar = document.querySelector('.sidebar');
const toggleSidebarBtn = document.getElementById('toggleSidebar');
const apiKeyInput = document.getElementById('apiKeyInput');
const saveApiKeyBtn = document.getElementById('saveApiKey');
const apiKeyStatus = document.getElementById('apiKeyStatus');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendMessageBtn = document.getElementById('sendMessage');
let tableContainer = null;

// Chat state
let conversationHistory = [];
let isProcessing = false;

// System prompt for the AI
const SYSTEM_PROMPT = `You are a helpful data analysis and management assistant for the CNS (Capital News Service) Maryland Tag Browser. Your role is to help users understand, explore, and MODIFY a dataset of article tags from CNS Maryland.

The dataset contains tags with the following fields:
- id: Unique identifier for the tag
- count: Number of times this tag has been used on articles
- name: The display name of the tag
- slug: URL-friendly version of the tag name
- description: Optional description of the tag
- taxonomy: Type of taxonomy (usually "post_tag")
- link: URL to view articles with this tag
- meta: Additional metadata (usually empty array)

You have access to powerful tools that let you:
1. ANALYZE the data (search, statistics, distribution, etc.)
2. MODIFY the data (create, update, delete, merge tags)

When users ask you to make changes, you should:
- First analyze the situation using read tools
- Explain what you're going to do
- Execute the modification
- Confirm what was changed

Be careful with destructive operations (delete, merge). When in doubt, ask for confirmation before making changes.

Current dataset contains ${tagsData.length} total tags.`;

// Define tools available to the AI
const TOOLS = [
    {
        type: "function",
        function: {
            name: "get_tag_statistics",
            description: "Get overall statistics about the tag dataset including total count, average usage, most/least used tags, etc.",
            parameters: {
                type: "object",
                properties: {},
                required: []
            }
        }
    },
    {
        type: "function",
        function: {
            name: "search_tags",
            description: "Search for tags by name, slug, or description. Returns total_matches (total found) and a limited sample of tags. Use this to count how many tags match a search term.",
            parameters: {
                type: "object",
                properties: {
                    query: {
                        type: "string",
                        description: "The search term to look for in tag names, slugs, or descriptions"
                    },
                    limit: {
                        type: "number",
                        description: "Maximum number of tag details to return (default 10, max 50). Note: total_matches will show the actual count.",
                        default: 10
                    }
                },
                required: ["query"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "get_top_tags",
            description: "Get the most frequently used tags sorted by usage count",
            parameters: {
                type: "object",
                properties: {
                    limit: {
                        type: "number",
                        description: "Number of top tags to return (default 10, max 100)",
                        default: 10
                    }
                },
                required: []
            }
        }
    },
    {
        type: "function",
        function: {
            name: "get_tags_by_count_range",
            description: "Get tags within a specific usage count range",
            parameters: {
                type: "object",
                properties: {
                    min_count: {
                        type: "number",
                        description: "Minimum usage count (inclusive)"
                    },
                    max_count: {
                        type: "number",
                        description: "Maximum usage count (inclusive)"
                    },
                    limit: {
                        type: "number",
                        description: "Maximum number of results to return (default 20, max 100)",
                        default: 20
                    }
                },
                required: ["min_count", "max_count"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "analyze_tag_distribution",
            description: "Analyze the distribution of tag usage counts and return statistical insights",
            parameters: {
                type: "object",
                properties: {},
                required: []
            }
        }
    },
    {
        type: "function",
        function: {
            name: "get_tag_by_id",
            description: "Get detailed information about a specific tag by its ID",
            parameters: {
                type: "object",
                properties: {
                    tag_id: {
                        type: "number",
                        description: "The ID of the tag to retrieve"
                    }
                },
                required: ["tag_id"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "find_similar_tags",
            description: "Find tags with similar names or topics based on a search term. Returns total_matches (total found) and a limited sample with similarity scores.",
            parameters: {
                type: "object",
                properties: {
                    reference_tag: {
                        type: "string",
                        description: "The tag name or topic to find similar tags for"
                    },
                    limit: {
                        type: "number",
                        description: "Maximum number of tag details to return (default 10, max 30). Note: total_matches will show the actual count.",
                        default: 10
                    }
                },
                required: ["reference_tag"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "create_tag",
            description: "Create a new tag entry in the dataset. Use this to add a completely new tag that doesn't exist yet.",
            parameters: {
                type: "object",
                properties: {
                    name: {
                        type: "string",
                        description: "The display name for the new tag"
                    },
                    slug: {
                        type: "string",
                        description: "URL-friendly slug for the tag (lowercase, hyphens instead of spaces)"
                    },
                    description: {
                        type: "string",
                        description: "Optional description of what this tag is for",
                        default: ""
                    },
                    count: {
                        type: "number",
                        description: "Initial usage count (default 0)",
                        default: 0
                    }
                },
                required: ["name", "slug"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "update_tag",
            description: "Update an existing tag's properties (name, slug, description, or count). Use this to modify tag details.",
            parameters: {
                type: "object",
                properties: {
                    tag_id: {
                        type: "number",
                        description: "The ID of the tag to update"
                    },
                    name: {
                        type: "string",
                        description: "New name for the tag (optional)"
                    },
                    slug: {
                        type: "string",
                        description: "New slug for the tag (optional)"
                    },
                    description: {
                        type: "string",
                        description: "New description for the tag (optional)"
                    },
                    count: {
                        type: "number",
                        description: "New count value for the tag (optional)"
                    }
                },
                required: ["tag_id"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "delete_tag",
            description: "Delete a tag from the dataset. Use this to remove unwanted or duplicate tags. Use with caution!",
            parameters: {
                type: "object",
                properties: {
                    tag_id: {
                        type: "number",
                        description: "The ID of the tag to delete"
                    }
                },
                required: ["tag_id"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "merge_tags",
            description: "Merge multiple tags into a single tag. The source tags are deleted and their counts are added to the target tag. Use this to consolidate similar or duplicate tags.",
            parameters: {
                type: "object",
                properties: {
                    target_tag_id: {
                        type: "number",
                        description: "The ID of the tag to merge into (this tag will be kept and updated)"
                    },
                    source_tag_ids: {
                        type: "array",
                        items: {
                            type: "number"
                        },
                        description: "Array of tag IDs to merge into the target (these will be deleted)"
                    }
                },
                required: ["target_tag_id", "source_tag_ids"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "bulk_delete_tags",
            description: "Delete multiple tags at once based on criteria. Use this to clean up the dataset by removing tags with low usage or specific patterns.",
            parameters: {
                type: "object",
                properties: {
                    tag_ids: {
                        type: "array",
                        items: {
                            type: "number"
                        },
                        description: "Array of specific tag IDs to delete"
                    }
                },
                required: ["tag_ids"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "rename_tags_batch",
            description: "Rename multiple tags at once using find-and-replace pattern. Useful for standardizing naming conventions.",
            parameters: {
                type: "object",
                properties: {
                    find_pattern: {
                        type: "string",
                        description: "Text pattern to find in tag names"
                    },
                    replace_with: {
                        type: "string",
                        description: "Text to replace the pattern with"
                    },
                    case_sensitive: {
                        type: "boolean",
                        description: "Whether the search should be case-sensitive (default false)",
                        default: false
                    }
                },
                required: ["find_pattern", "replace_with"]
            }
        }
    }
];

// Initialize app
async function init() {
    loadingIndicator.classList.add('active');
    tableContainer = document.querySelector('.table-container');
    
    try {
        // Fetch tags data
        const response = await fetch('/api/tags');
        if (!response.ok) throw new Error('Failed to load tags data');
        
        tagsData = await response.json();
        filteredData = [...tagsData];
        
        // Apply default sort (by count, descending)
        sortData('count', 'desc');
        
        // Initialize virtual scrolling
        initVirtualScroll();
        updateTagCount();
        
        loadingIndicator.classList.remove('active');
        
        console.log(`Loaded ${tagsData.length} tags with virtual scrolling enabled`);
    } catch (error) {
        console.error('Error loading tags:', error);
        loadingIndicator.textContent = 'Error loading tags. Please refresh the page.';
    }
    
    // Load saved API key
    loadApiKey();
    
    // Setup event listeners
    setupEventListeners();
}

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    searchInput.addEventListener('input', handleSearch);
    
    // Table header sorting
    tableHeaders.forEach(header => {
        header.addEventListener('click', () => handleSort(header));
    });
    
    // Sidebar toggle
    toggleSidebarBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });
    
    // API key management
    saveApiKeyBtn.addEventListener('click', saveApiKey);
    apiKeyInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') saveApiKey();
    });
    
    // Chat functionality
    sendMessageBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });
    
    // Auto-resize chat input
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 150) + 'px';
    });
    
    // Virtual scroll listener
    if (tableContainer) {
        tableContainer.addEventListener('scroll', handleScroll, { passive: true });
    }
    
    // Handle window resize
    window.addEventListener('resize', () => {
        if (filteredData.length > 0) {
            updateVirtualScroll();
        }
    });
}

// Handle search
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    
    if (searchTerm === '') {
        filteredData = [...tagsData];
    } else {
        filteredData = tagsData.filter(tag => {
            return (
                tag.name.toLowerCase().includes(searchTerm) ||
                tag.slug.toLowerCase().includes(searchTerm) ||
                tag.description.toLowerCase().includes(searchTerm) ||
                tag.id.toString().includes(searchTerm)
            );
        });
    }
    
    // Reapply current sort
    sortData(currentSort.column, currentSort.order);
    
    // Reset scroll and re-render with virtual scrolling
    if (tableContainer) {
        tableContainer.scrollTop = 0;
    }
    initVirtualScroll();
    updateTagCount();
}

// Handle column sorting
function handleSort(header) {
    const column = header.dataset.column;
    let currentOrder = header.dataset.sort;
    let newOrder;
    
    // Cycle through: none -> asc -> desc -> none
    if (currentOrder === 'none') {
        newOrder = 'asc';
    } else if (currentOrder === 'asc') {
        newOrder = 'desc';
    } else {
        newOrder = 'none';
    }
    
    // Reset all headers
    tableHeaders.forEach(h => {
        h.dataset.sort = 'none';
        h.querySelector('.sort-indicator').textContent = '';
    });
    
    // Update clicked header
    header.dataset.sort = newOrder;
    const indicator = header.querySelector('.sort-indicator');
    
    if (newOrder === 'asc') {
        indicator.textContent = '▲';
    } else if (newOrder === 'desc') {
        indicator.textContent = '▼';
    } else {
        indicator.textContent = '';
    }
    
    // Sort data
    currentSort = { column, order: newOrder };
    sortData(column, newOrder);
    
    // Reset scroll and re-render with virtual scrolling
    if (tableContainer) {
        tableContainer.scrollTop = 0;
    }
    initVirtualScroll();
}

// Sort data
function sortData(column, order) {
    if (order === 'none') {
        // Reset to original order (by count descending)
        filteredData = [...filteredData].sort((a, b) => b.count - a.count);
        return;
    }
    
    filteredData.sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];
        
        // Handle meta array
        if (column === 'meta') {
            aVal = Array.isArray(aVal) ? aVal.length : 0;
            bVal = Array.isArray(bVal) ? bVal.length : 0;
        }
        
        // Handle null/undefined/empty values - push to end
        const aIsEmpty = aVal == null || aVal === '';
        const bIsEmpty = bVal == null || bVal === '';
        
        if (aIsEmpty && bIsEmpty) return 0;
        if (aIsEmpty) return 1; // Empty values go to end
        if (bIsEmpty) return -1;
        
        // Numeric comparison for id and count
        if (typeof aVal === 'number' && typeof bVal === 'number') {
            return order === 'asc' ? aVal - bVal : bVal - aVal;
        }
        
        // String comparison with proper alphabetical sorting
        const aStr = String(aVal).toLowerCase().trim();
        const bStr = String(bVal).toLowerCase().trim();
        
        // Use localeCompare with numeric option for natural sorting
        const compareResult = aStr.localeCompare(bStr, undefined, {
            numeric: true,
            sensitivity: 'base'
        });
        
        return order === 'asc' ? compareResult : -compareResult;
    });
}

// Virtual Scrolling Functions

function initVirtualScroll() {
    if (!tableContainer || filteredData.length === 0) return;
    
    // Calculate viewport dimensions
    virtualScrollState.viewportHeight = tableContainer.clientHeight;
    
    // Create spacer rows for virtual scrolling
    createVirtualScrollStructure();
    
    // Initial render
    updateVirtualScroll();
}

function createVirtualScrollStructure() {
    // Clear existing content
    tagsTableBody.innerHTML = '';
    
    // Create top spacer
    const topSpacer = document.createElement('tr');
    topSpacer.id = 'virtual-scroll-top-spacer';
    topSpacer.style.height = '0px';
    tagsTableBody.appendChild(topSpacer);
    
    // Create content container
    const contentContainer = document.createElement('tbody');
    contentContainer.id = 'virtual-scroll-content';
    tagsTableBody.appendChild(contentContainer);
    
    // Create bottom spacer
    const bottomSpacer = document.createElement('tr');
    bottomSpacer.id = 'virtual-scroll-bottom-spacer';
    bottomSpacer.style.height = '0px';
    tagsTableBody.appendChild(bottomSpacer);
}

function handleScroll() {
    if (!tableContainer) return;
    requestAnimationFrame(updateVirtualScroll);
}

function updateVirtualScroll() {
    if (!tableContainer || filteredData.length === 0) return;
    
    const scrollTop = tableContainer.scrollTop;
    const viewportHeight = tableContainer.clientHeight;
    
    // Calculate visible range with buffer
    const startIndex = Math.max(0, Math.floor(scrollTop / ROW_HEIGHT) - BUFFER_SIZE);
    const visibleCount = Math.ceil(viewportHeight / ROW_HEIGHT) + (BUFFER_SIZE * 2);
    const endIndex = Math.min(filteredData.length, startIndex + visibleCount);
    
    // Update state
    virtualScrollState = {
        startIndex,
        endIndex,
        scrollTop,
        viewportHeight
    };
    
    // Render visible rows
    renderVirtualRows(startIndex, endIndex);
    
    // Update spacers
    updateSpacers(startIndex, endIndex);
}

function renderVirtualRows(startIndex, endIndex) {
    const contentContainer = document.getElementById('virtual-scroll-content');
    if (!contentContainer) return;
    
    // Clear existing rows
    contentContainer.innerHTML = '';
    
    // Render only visible rows
    for (let i = startIndex; i < endIndex; i++) {
        const tag = filteredData[i];
        if (!tag) continue;
        
        const row = document.createElement('tr');
        
        // Format meta display
        const metaDisplay = Array.isArray(tag.meta) && tag.meta.length > 0
            ? `Array(${tag.meta.length})`
            : '';
        
        row.innerHTML = `
            <td>${tag.id}</td>
            <td>${tag.count}</td>
            <td>${escapeHtml(tag.name)}</td>
            <td>${escapeHtml(tag.slug)}</td>
            <td title="${escapeHtml(tag.description)}">${escapeHtml(tag.description)}</td>
            <td>${escapeHtml(tag.taxonomy)}</td>
            <td><a href="${escapeHtml(tag.link)}" target="_blank" rel="noopener">View</a></td>
            <td>${metaDisplay}</td>
        `;
        
        contentContainer.appendChild(row);
    }
}

function updateSpacers(startIndex, endIndex) {
    const topSpacer = document.getElementById('virtual-scroll-top-spacer');
    const bottomSpacer = document.getElementById('virtual-scroll-bottom-spacer');
    
    if (!topSpacer || !bottomSpacer) return;
    
    // Calculate spacer heights
    const topHeight = startIndex * ROW_HEIGHT;
    const bottomHeight = (filteredData.length - endIndex) * ROW_HEIGHT;
    
    topSpacer.style.height = `${topHeight}px`;
    bottomSpacer.style.height = `${bottomHeight}px`;
}

// Update tag count display
function updateTagCount() {
    const total = tagsData.length;
    const filtered = filteredData.length;
    
    if (total === filtered) {
        tagCount.textContent = `Showing ${total.toLocaleString()} tags`;
    } else {
        tagCount.textContent = `Showing ${filtered.toLocaleString()} of ${total.toLocaleString()} tags`;
    }
}

// API Key Management
function saveApiKey() {
    const apiKey = apiKeyInput.value.trim();
    
    if (!apiKey) {
        showApiKeyStatus('Please enter an API key', 'error');
        return;
    }
    
    // Save to localStorage
    localStorage.setItem('groqApiKey', apiKey);
    
    // Show success message
    showApiKeyStatus('API key saved successfully!', 'success');
    
    // Clear input for security
    apiKeyInput.value = '';
}

function loadApiKey() {
    const savedKey = localStorage.getItem('groqApiKey');
    if (savedKey) {
        showApiKeyStatus('API key loaded from storage', 'success');
    }
}

function showApiKeyStatus(message, type) {
    apiKeyStatus.textContent = message;
    apiKeyStatus.className = `api-key-status ${type}`;
    
    // Clear message after 3 seconds
    setTimeout(() => {
        apiKeyStatus.textContent = '';
        apiKeyStatus.className = 'api-key-status';
    }, 3000);
}

// Chat Functions

async function sendChatMessage() {
    const message = chatInput.value.trim();
    
    if (!message || isProcessing) return;
    
    // Check for API key
    const apiKey = localStorage.getItem('groqApiKey');
    if (!apiKey) {
        addMessage('error', 'Please save your Groq API key first!');
        return;
    }
    
    // Clear input
    chatInput.value = '';
    chatInput.style.height = 'auto';
    
    // Add user message to UI
    addMessage('user', message);
    
    // Add to conversation history (ensure system prompt is first)
    if (conversationHistory.length === 0 || conversationHistory[0].role !== 'system') {
        conversationHistory.unshift({
            role: 'system',
            content: SYSTEM_PROMPT
        });
    }
    
    conversationHistory.push({
        role: 'user',
        content: message
    });
    
    // Show typing indicator
    isProcessing = true;
    updateChatControls();
    showTypingIndicator();
    
    try {
        // Process message with potential tool calls
        await processMessageWithTools(apiKey);
        
    } catch (error) {
        removeTypingIndicator();
        console.error('Chat error:', error);
        
        // Check if it's a rate limit error
        if (error.message && error.message.includes('Rate limit reached')) {
            await handleRateLimitError(error.message, apiKey);
        } else {
            addMessage('error', `Error: ${error.message}`);
        }
    } finally {
        isProcessing = false;
        updateChatControls();
    }
}

async function processMessageWithTools(apiKey) {
    let maxIterations = 5; // Prevent infinite loops
    let iteration = 0;
    
    while (iteration < maxIterations) {
        iteration++;
        
        // Call Groq API with tools
        const response = await callGroqAPI(apiKey, conversationHistory, TOOLS);
        
        // Check if AI wants to use tools
        if (response.tool_calls && response.tool_calls.length > 0) {
            // Add assistant message with tool calls to history
            conversationHistory.push({
                role: 'assistant',
                content: response.content || '',
                tool_calls: response.tool_calls
            });
            
            // Execute each tool call
            for (const toolCall of response.tool_calls) {
                const toolName = toolCall.function.name;
                const toolArgs = JSON.parse(toolCall.function.arguments);
                
                console.log(`Executing tool: ${toolName}`, toolArgs);
                
                // Show tool execution in UI
                updateTypingIndicator(`🔧 Using tool: ${formatToolName(toolName)}...`);
                
                // Execute the tool
                const toolResult = await executeToolCall(toolName, toolArgs);
                
                // Add tool result to conversation
                conversationHistory.push({
                    role: 'tool',
                    tool_call_id: toolCall.id,
                    name: toolName,
                    content: JSON.stringify(toolResult)
                });
            }
            
            // Update typing indicator back to normal
            updateTypingIndicator('🤖 Analyzing results...');
            
            // Continue loop to let AI process tool results
            continue;
        } else {
            // No more tool calls, show final response
            removeTypingIndicator();
            
            if (response.content) {
                addMessage('assistant', response.content);
                
                conversationHistory.push({
                    role: 'assistant',
                    content: response.content
                });
            }
            
            break;
        }
    }
    
    if (iteration >= maxIterations) {
        removeTypingIndicator();
        addMessage('error', 'Maximum tool call iterations reached. The AI may need to simplify its approach.');
    }
}

async function callGroqAPI(apiKey, messages, tools = null) {
    const requestBody = {
        model: 'openai/gpt-oss-120b',
        messages: messages,
        temperature: 0.7,
        max_tokens: 8192,
        top_p: 1,
        stream: false
    };
    
    // Add tools if provided
    if (tools && tools.length > 0) {
        requestBody.tools = tools;
        requestBody.tool_choice = 'auto';
    }
    
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify(requestBody)
    });
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.error?.message || `API request failed: ${response.status}`;
        throw new Error(errorMessage);
    }
    
    const data = await response.json();
    const message = data.choices[0].message;
    
    // Return the full message object (may include tool_calls)
    return {
        content: message.content,
        tool_calls: message.tool_calls || null
    };
}

async function handleRateLimitError(errorMessage, apiKey) {
    // Extract wait time from error message using regex
    // Example: "Please try again in 11.9225s"
    const waitTimeMatch = errorMessage.match(/try again in ([\d.]+)s/);
    
    if (!waitTimeMatch) {
        // Couldn't parse wait time, show error
        addMessage('error', `Rate limit error: ${errorMessage}`);
        return;
    }
    
    const waitSeconds = Math.ceil(parseFloat(waitTimeMatch[1]));
    
    // Show rate limit message with countdown
    const rateLimitMessageId = showRateLimitMessage(waitSeconds);
    
    // Wait for the specified time with countdown
    await countdownWait(waitSeconds, rateLimitMessageId);
    
    // Remove the rate limit message
    removeRateLimitMessage(rateLimitMessageId);
    
    // Show typing indicator and retry
    showTypingIndicator('🤖 Retrying request...');
    
    try {
        // Retry the request
        await processMessageWithTools(apiKey);
    } catch (retryError) {
        removeTypingIndicator();
        console.error('Retry error:', retryError);
        
        // Check if it's another rate limit error
        if (retryError.message && retryError.message.includes('Rate limit reached')) {
            await handleRateLimitError(retryError.message, apiKey);
        } else {
            addMessage('error', `Error: ${retryError.message}`);
        }
    }
}

function showRateLimitMessage(waitSeconds) {
    const messageDiv = document.createElement('div');
    const messageId = 'rate-limit-' + Date.now();
    messageDiv.id = messageId;
    messageDiv.className = 'message system';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content rate-limit-message';
    contentDiv.innerHTML = `
        ⏳ Rate limit exceeded. Retrying in <strong><span class="countdown">${waitSeconds}</span></strong> seconds...
    `;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageId;
}

async function countdownWait(seconds, messageId) {
    for (let i = seconds; i > 0; i--) {
        // Update countdown display
        const countdownElement = document.querySelector(`#${messageId} .countdown`);
        if (countdownElement) {
            countdownElement.textContent = i;
        }
        
        // Wait 1 second
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
}

function removeRateLimitMessage(messageId) {
    const messageElement = document.getElementById(messageId);
    if (messageElement) {
        messageElement.remove();
    }
}

// Execute tool calls
async function executeToolCall(toolName, args) {
    console.log(`Executing ${toolName} with args:`, args);
    
    switch (toolName) {
        // Read-only tools
        case 'get_tag_statistics':
            return getTagStatistics();
        
        case 'search_tags':
            return searchTags(args.query, args.limit || 10);
        
        case 'get_top_tags':
            return getTopTags(args.limit || 10);
        
        case 'get_tags_by_count_range':
            return getTagsByCountRange(args.min_count, args.max_count, args.limit || 20);
        
        case 'analyze_tag_distribution':
            return analyzeTagDistribution();
        
        case 'get_tag_by_id':
            return getTagById(args.tag_id);
        
        case 'find_similar_tags':
            return findSimilarTags(args.reference_tag, args.limit || 10);
        
        // Modification tools
        case 'create_tag':
            return createTag(args.name, args.slug, args.description || '', args.count || 0);
        
        case 'update_tag':
            return updateTag(args.tag_id, args);
        
        case 'delete_tag':
            return deleteTag(args.tag_id);
        
        case 'merge_tags':
            return mergeTags(args.target_tag_id, args.source_tag_ids);
        
        case 'bulk_delete_tags':
            return bulkDeleteTags(args.tag_ids);
        
        case 'rename_tags_batch':
            return renameTagsBatch(args.find_pattern, args.replace_with, args.case_sensitive || false);
        
        default:
            return { error: `Unknown tool: ${toolName}` };
    }
}

// Tool Implementation Functions

function getTagStatistics() {
    const counts = tagsData.map(tag => tag.count);
    const total = tagsData.length;
    const totalUsage = counts.reduce((sum, count) => sum + count, 0);
    const avgUsage = totalUsage / total;
    
    const sorted = [...tagsData].sort((a, b) => b.count - a.count);
    const mostUsed = sorted.slice(0, 5).map(t => ({ id: t.id, name: t.name, count: t.count }));
    const leastUsed = sorted.slice(-5).reverse().map(t => ({ id: t.id, name: t.name, count: t.count }));
    
    const singleUse = tagsData.filter(t => t.count === 1).length;
    const multiUse = tagsData.filter(t => t.count > 1).length;
    
    return {
        total_tags: total,
        total_usage: totalUsage,
        average_usage: avgUsage.toFixed(2),
        most_used_tags: mostUsed,
        least_used_tags: leastUsed,
        single_use_tags: singleUse,
        multi_use_tags: multiUse,
        median_usage: counts.sort((a, b) => a - b)[Math.floor(counts.length / 2)]
    };
}

function searchTags(query, limit = 10) {
    const searchLower = query.toLowerCase();
    const allMatches = tagsData.filter(tag => 
        tag.name.toLowerCase().includes(searchLower) ||
        tag.slug.toLowerCase().includes(searchLower) ||
        (tag.description && tag.description.toLowerCase().includes(searchLower))
    );
    
    const limitedMatches = allMatches.slice(0, Math.min(limit, 50));
    
    return {
        query: query,
        total_matches: allMatches.length,
        returned_count: limitedMatches.length,
        tags: limitedMatches.map(t => ({
            id: t.id,
            name: t.name,
            slug: t.slug,
            count: t.count,
            description: t.description
        }))
    };
}

function getTopTags(limit = 10) {
    const sorted = [...tagsData].sort((a, b) => b.count - a.count);
    const topTags = sorted.slice(0, Math.min(limit, 100));
    
    return {
        count: topTags.length,
        tags: topTags.map(t => ({
            id: t.id,
            name: t.name,
            slug: t.slug,
            count: t.count,
            link: t.link
        }))
    };
}

function getTagsByCountRange(minCount, maxCount, limit = 20) {
    const filtered = tagsData.filter(t => t.count >= minCount && t.count <= maxCount);
    const limited = filtered.slice(0, Math.min(limit, 100));
    
    return {
        min_count: minCount,
        max_count: maxCount,
        total_matches: filtered.length,
        returned_count: limited.length,
        tags: limited.map(t => ({
            id: t.id,
            name: t.name,
            count: t.count,
            slug: t.slug
        }))
    };
}

function analyzeTagDistribution() {
    const counts = tagsData.map(t => t.count).sort((a, b) => a - b);
    const total = counts.length;
    
    // Calculate percentiles
    const p25 = counts[Math.floor(total * 0.25)];
    const p50 = counts[Math.floor(total * 0.50)];
    const p75 = counts[Math.floor(total * 0.75)];
    const p90 = counts[Math.floor(total * 0.90)];
    const p95 = counts[Math.floor(total * 0.95)];
    const p99 = counts[Math.floor(total * 0.99)];
    
    const max = counts[total - 1];
    const min = counts[0];
    
    // Count distribution
    const countBuckets = {
        '1': tagsData.filter(t => t.count === 1).length,
        '2-5': tagsData.filter(t => t.count >= 2 && t.count <= 5).length,
        '6-10': tagsData.filter(t => t.count >= 6 && t.count <= 10).length,
        '11-50': tagsData.filter(t => t.count >= 11 && t.count <= 50).length,
        '51-100': tagsData.filter(t => t.count >= 51 && t.count <= 100).length,
        '100+': tagsData.filter(t => t.count > 100).length
    };
    
    return {
        total_tags: total,
        min_count: min,
        max_count: max,
        percentiles: {
            '25th': p25,
            '50th (median)': p50,
            '75th': p75,
            '90th': p90,
            '95th': p95,
            '99th': p99
        },
        distribution: countBuckets
    };
}

function getTagById(tagId) {
    const tag = tagsData.find(t => t.id === tagId);
    
    if (!tag) {
        return { error: `Tag with ID ${tagId} not found` };
    }
    
    return {
        id: tag.id,
        name: tag.name,
        slug: tag.slug,
        count: tag.count,
        description: tag.description,
        taxonomy: tag.taxonomy,
        link: tag.link,
        meta: tag.meta
    };
}

function findSimilarTags(referenceName, limit = 10) {
    const refLower = referenceName.toLowerCase();
    const words = refLower.split(/\s+/).filter(w => w.length > 2);
    
    // Score tags based on word overlap
    const allScored = tagsData.map(tag => {
        const tagLower = tag.name.toLowerCase();
        let score = 0;
        
        // Exact match gets highest score
        if (tagLower === refLower) {
            score = 1000;
        } else if (tagLower.includes(refLower) || refLower.includes(tagLower)) {
            score = 500;
        } else {
            // Count matching words
            for (const word of words) {
                if (tagLower.includes(word)) {
                    score += 100;
                }
            }
        }
        
        return { tag, score };
    }).filter(item => item.score > 0)
      .sort((a, b) => b.score - a.score);
    
    const limitedScored = allScored.slice(0, Math.min(limit, 30));
    
    return {
        reference: referenceName,
        total_matches: allScored.length,
        returned_count: limitedScored.length,
        tags: limitedScored.map(item => ({
            id: item.tag.id,
            name: item.tag.name,
            slug: item.tag.slug,
            count: item.tag.count,
            similarity_score: item.score
        }))
    };
}

function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    if (role !== 'system' && role !== 'error') {
        const header = document.createElement('div');
        header.className = 'message-header';
        
        const roleSpan = document.createElement('span');
        roleSpan.className = `message-role ${role}`;
        roleSpan.textContent = role === 'user' ? '👤 You' : '🤖 Assistant';
        
        header.appendChild(roleSpan);
        messageDiv.appendChild(header);
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Render markdown for assistant messages, plain text for others
    if (role === 'assistant') {
        contentDiv.innerHTML = renderMarkdown(content);
    } else {
        contentDiv.textContent = content;
    }
    
    messageDiv.appendChild(contentDiv);
    
    // Remove welcome message if it exists
    const welcome = chatMessages.querySelector('.chat-welcome');
    if (welcome) {
        welcome.remove();
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Simple markdown renderer
function renderMarkdown(text) {
    if (!text) return '';
    
    // Escape HTML first
    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    // Code blocks (```)
    html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code class="language-${lang || 'text'}">${code.trim()}</code></pre>`;
    });
    
    // Inline code (`)
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Bold (**text** or __text__)
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');
    
    // Italic (*text* or _text_)
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/_(.+?)_/g, '<em>$1</em>');
    
    // Headers
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    
    // Links [text](url)
    html = html.replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    
    // Unordered lists
    html = html.replace(/^\* (.+)$/gm, '<li>$1</li>');
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    
    // Ordered lists
    html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
    
    // Line breaks (double newline = paragraph)
    html = html.replace(/\n\n/g, '</p><p>');
    html = '<p>' + html + '</p>';
    
    // Single line breaks
    html = html.replace(/\n/g, '<br>');
    
    // Clean up empty paragraphs
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p>\s*<\/p>/g, '');
    
    return html;
}

function showTypingIndicator(text = '🤖 Assistant is typing') {
    const indicator = document.createElement('div');
    indicator.id = 'typingIndicator';
    indicator.className = 'typing-indicator';
    
    indicator.innerHTML = `
        <span id="typingText">${text}</span>
        <div class="dots">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
        </div>
    `;
    
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateTypingIndicator(text) {
    const textElement = document.getElementById('typingText');
    if (textElement) {
        textElement.textContent = text;
    } else {
        // Create new indicator if it doesn't exist
        showTypingIndicator(text);
    }
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function formatToolName(toolName) {
    return toolName
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function updateChatControls() {
    chatInput.disabled = isProcessing;
    sendMessageBtn.disabled = isProcessing;
}

// Helper function to reapply search and update display
function reapplySearchAndUpdate() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    
    if (searchTerm === '') {
        filteredData = [...tagsData];
    } else {
        filteredData = tagsData.filter(tag => {
            return (
                tag.name.toLowerCase().includes(searchTerm) ||
                tag.slug.toLowerCase().includes(searchTerm) ||
                tag.description.toLowerCase().includes(searchTerm) ||
                tag.id.toString().includes(searchTerm)
            );
        });
    }
    
    // Reapply current sort
    sortData(currentSort.column, currentSort.order);
    
    // Reset scroll and re-render
    if (tableContainer) {
        tableContainer.scrollTop = 0;
    }
    initVirtualScroll();
    updateTagCount();
}

// Tag Modification Functions

function createTag(name, slug, description = '', count = 0) {
    // Generate a new unique ID
    const maxId = Math.max(...tagsData.map(t => t.id), 0);
    const newId = maxId + 1;
    
    // Create new tag object
    const newTag = {
        id: newId,
        count: count,
        description: description,
        link: `https://cnsmaryland.org/tag/${slug}/`,
        name: name,
        slug: slug,
        taxonomy: 'post_tag',
        meta: []
    };
    
    // Add to dataset
    tagsData.push(newTag);
    
    // Reapply current search filter
    reapplySearchAndUpdate();
    
    return {
        success: true,
        message: `Created new tag: "${name}" (ID: ${newId})`,
        tag: newTag
    };
}

function updateTag(tagId, updates) {
    const tagIndex = tagsData.findIndex(t => t.id === tagId);
    
    if (tagIndex === -1) {
        return { success: false, error: `Tag with ID ${tagId} not found` };
    }
    
    const tag = tagsData[tagIndex];
    const oldValues = { ...tag };
    
    // Update fields
    if (updates.name !== undefined) tag.name = updates.name;
    if (updates.slug !== undefined) {
        tag.slug = updates.slug;
        tag.link = `https://cnsmaryland.org/tag/${updates.slug}/`;
    }
    if (updates.description !== undefined) tag.description = updates.description;
    if (updates.count !== undefined) tag.count = updates.count;
    
    // Reapply current search filter
    reapplySearchAndUpdate();
    
    return {
        success: true,
        message: `Updated tag ID ${tagId}`,
        old_values: oldValues,
        new_values: tag
    };
}

function deleteTag(tagId) {
    const tagIndex = tagsData.findIndex(t => t.id === tagId);
    
    if (tagIndex === -1) {
        return { success: false, error: `Tag with ID ${tagId} not found` };
    }
    
    const deletedTag = tagsData[tagIndex];
    
    // Remove from dataset
    tagsData.splice(tagIndex, 1);
    
    // Reapply current search filter
    reapplySearchAndUpdate();
    
    return {
        success: true,
        message: `Deleted tag: "${deletedTag.name}" (ID: ${tagId})`,
        deleted_tag: deletedTag
    };
}

function mergeTags(targetTagId, sourceTagIds) {
    const targetTag = tagsData.find(t => t.id === targetTagId);
    
    if (!targetTag) {
        return { success: false, error: `Target tag with ID ${targetTagId} not found` };
    }
    
    const mergedTags = [];
    let totalCount = targetTag.count;
    
    // Process each source tag
    for (const sourceId of sourceTagIds) {
        const sourceTag = tagsData.find(t => t.id === sourceId);
        
        if (!sourceTag) {
            continue; // Skip if not found
        }
        
        if (sourceId === targetTagId) {
            continue; // Skip if trying to merge into itself
        }
        
        // Add count to target
        totalCount += sourceTag.count;
        mergedTags.push({
            id: sourceTag.id,
            name: sourceTag.name,
            count: sourceTag.count
        });
    }
    
    // Update target tag count
    targetTag.count = totalCount;
    
    // Remove source tags
    for (const sourceId of sourceTagIds) {
        if (sourceId !== targetTagId) {
            const index = tagsData.findIndex(t => t.id === sourceId);
            if (index !== -1) {
                tagsData.splice(index, 1);
            }
        }
    }
    
    // Reapply current search filter
    reapplySearchAndUpdate();
    
    return {
        success: true,
        message: `Merged ${mergedTags.length} tags into "${targetTag.name}"`,
        target_tag: {
            id: targetTag.id,
            name: targetTag.name,
            new_count: targetTag.count
        },
        merged_tags: mergedTags
    };
}

function bulkDeleteTags(tagIds) {
    const deletedTags = [];
    const notFoundIds = [];
    
    for (const tagId of tagIds) {
        const index = tagsData.findIndex(t => t.id === tagId);
        
        if (index !== -1) {
            const deleted = tagsData[index];
            deletedTags.push({
                id: deleted.id,
                name: deleted.name,
                count: deleted.count
            });
            tagsData.splice(index, 1);
        } else {
            notFoundIds.push(tagId);
        }
    }
    
    // Reapply current search filter
    reapplySearchAndUpdate();
    
    return {
        success: true,
        message: `Deleted ${deletedTags.length} tags`,
        deleted_count: deletedTags.length,
        deleted_tags: deletedTags,
        not_found_ids: notFoundIds
    };
}

function renameTagsBatch(findPattern, replaceWith, caseSensitive = false) {
    const modifiedTags = [];
    const flags = caseSensitive ? 'g' : 'gi';
    const regex = new RegExp(findPattern, flags);
    
    for (const tag of tagsData) {
        if (regex.test(tag.name)) {
            const oldName = tag.name;
            const newName = tag.name.replace(regex, replaceWith);
            
            if (oldName !== newName) {
                tag.name = newName;
                
                // Update slug too if it matches
                const oldSlug = tag.slug;
                const newSlug = tag.slug.replace(regex, replaceWith);
                if (oldSlug !== newSlug) {
                    tag.slug = newSlug;
                    tag.link = `https://cnsmaryland.org/tag/${newSlug}/`;
                }
                
                modifiedTags.push({
                    id: tag.id,
                    old_name: oldName,
                    new_name: newName,
                    old_slug: oldSlug,
                    new_slug: newSlug
                });
            }
        }
    }
    
    // Reapply current search filter
    reapplySearchAndUpdate();
    
    return {
        success: true,
        message: `Renamed ${modifiedTags.length} tags`,
        pattern: findPattern,
        replacement: replaceWith,
        modified_count: modifiedTags.length,
        modified_tags: modifiedTags
    };
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}