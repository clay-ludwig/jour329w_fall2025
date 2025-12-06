// Load and display article
let stories = [];

// Load the data
fetch('../source_stories.json')
    .then(response => response.json())
    .then(data => {
        stories = data;
        displayArticle();
    })
    .catch(error => {
        console.error('Error loading stories:', error);
        document.getElementById('articleContent').innerHTML = '<div class="no-results">Error loading article.</div>';
    });

function displayArticle() {
    const urlParams = new URLSearchParams(window.location.search);
    const index = urlParams.get('id');
    const query = urlParams.get('q');
    
    if (index === null || !stories[index]) {
        document.getElementById('articleContent').innerHTML = '<div class="no-results">Article not found.</div>';
        return;
    }

    const story = stories[index];
    
    // Set title with highlighting if there's a search query
    document.getElementById('articleTitle').innerHTML = query ? 
        highlightText(escapeHtml(story.title), query) : 
        escapeHtml(story.title);
    
    // Set author
    document.getElementById('articleAuthor').textContent = story.author || 'Unknown author';
    
    // Set date
    document.getElementById('articleDate').textContent = story.date || 'No date';
    
    // Set content with highlighting
    let content = story.content || 'No content available.';
    if (query) {
        content = highlightText(escapeHtml(content), query);
    } else {
        content = escapeHtml(content);
    }
    document.getElementById('articleBody').innerHTML = content;
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

// Update back button to preserve search in URL
window.addEventListener('load', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q');
    const backButton = document.querySelector('.back-button');
    
    if (query) {
        backButton.href = 'index.html?q=' + encodeURIComponent(query);
    }
});
