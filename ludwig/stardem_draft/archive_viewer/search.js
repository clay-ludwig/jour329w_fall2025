// Load stories from JSON file
let stories = [];

// Load the data
fetch('../source_stories.json')
    .then(response => response.json())
    .then(data => {
        stories = data;
        console.log(`Loaded ${stories.length} stories`);
    })
    .catch(error => {
        console.error('Error loading stories:', error);
        document.getElementById('results').innerHTML = '<div class="no-results">Error loading stories. Please make sure source_stories.json is in the parent directory.</div>';
    });

// Search functionality
function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    
    if (!query) {
        document.getElementById('results').innerHTML = '';
        document.getElementById('searchStats').innerHTML = '';
        return;
    }

    const results = searchStories(query);
    displayResults(results, query);
}

function searchStories(query) {
    const queryLower = query.toLowerCase();
    const results = [];

    stories.forEach((story, index) => {
        const title = story.title || '';
        const content = story.content || '';
        const author = story.author || '';
        
        const titleLower = title.toLowerCase();
        const contentLower = content.toLowerCase();
        const authorLower = author.toLowerCase();

        if (titleLower.includes(queryLower) || 
            contentLower.includes(queryLower) || 
            authorLower.includes(queryLower)) {
            
            // Calculate relevance score
            let score = 0;
            if (titleLower.includes(queryLower)) score += 10;
            if (authorLower.includes(queryLower)) score += 5;
            
            // Count occurrences in content
            const matches = contentLower.split(queryLower).length - 1;
            score += matches;

            results.push({
                story: story,
                index: index,
                score: score
            });
        }
    });

    // Sort by relevance score
    results.sort((a, b) => b.score - a.score);
    
    return results;
}

function displayResults(results, query) {
    const resultsContainer = document.getElementById('results');
    const statsContainer = document.getElementById('searchStats');

    if (results.length === 0) {
        statsContainer.innerHTML = '';
        resultsContainer.innerHTML = '<div class="no-results">No results found for "' + escapeHtml(query) + '"</div>';
        return;
    }

    statsContainer.innerHTML = `About ${results.length} result${results.length === 1 ? '' : 's'}`;

    let html = '';
    results.forEach(result => {
        const story = result.story;
        const snippet = createSnippet(story.content, query);
        
        html += `
            <div class="result-item" onclick="viewArticle(${result.index}, '${escapeHtml(query).replace(/'/g, "\\'")}')">
                <div class="result-title">${highlightText(escapeHtml(story.title), query)}</div>
                <div class="result-url">Article ID: ${escapeHtml(story.article_id || result.index)}</div>
                <div class="result-meta">${escapeHtml(story.author || 'Unknown author')} • ${escapeHtml(story.date || 'No date')}</div>
                <div class="result-snippet">${snippet}</div>
            </div>
        `;
    });

    resultsContainer.innerHTML = html;
}

function createSnippet(content, query) {
    if (!content) return '';
    
    const queryLower = query.toLowerCase();
    const contentLower = content.toLowerCase();
    const index = contentLower.indexOf(queryLower);
    
    if (index === -1) {
        // If query not found in content, show beginning
        const snippet = content.substring(0, 200);
        return escapeHtml(snippet) + (content.length > 200 ? '...' : '');
    }

    // Show context around the match
    const start = Math.max(0, index - 100);
    const end = Math.min(content.length, index + query.length + 100);
    
    let snippet = content.substring(start, end);
    if (start > 0) snippet = '...' + snippet;
    if (end < content.length) snippet = snippet + '...';
    
    return highlightText(escapeHtml(snippet), query);
}

function highlightText(text, query) {
    if (!query) return text;
    
    const regex = new RegExp('(' + escapeRegex(query) + ')', 'gi');
    return text.replace(regex, '<span class="highlight">$1</span>');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeRegex(text) {
    return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function viewArticle(index, query) {
    // Create a permanent URL with parameters
    const params = new URLSearchParams();
    params.set('id', index);
    if (query) {
        params.set('q', query);
    }
    window.location.href = 'article.html?' + params.toString();
}

// Event listeners
document.getElementById('searchButton').addEventListener('click', performSearch);

document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        performSearch();
    }
});

// Check if returning from article view with a search or if there's a query in URL
window.addEventListener('load', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q');
    if (query) {
        document.getElementById('searchInput').value = query;
        performSearch();
    }
});
