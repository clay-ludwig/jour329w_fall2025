# Star Democrat Archive Viewer

A simple web-based interface for searching and viewing articles from the Star Democrat archive.

## Features

- **Google-style search interface**: Clean, familiar search experience
- **Keyword search**: Search across article titles, content, and authors
- **Highlighted results**: Search terms are highlighted in yellow throughout
- **Article viewer**: Click on any search result to view the full article
- **Responsive design**: Works on desktop and mobile devices

## How to Use

1. Open `index.html` in a web browser
2. Enter a search term in the search box
3. Click "Search" or press Enter
4. Browse the search results (sorted by relevance)
5. Click on any result to view the full article with highlighted search terms
6. Use the "Back to search" button to return to your results

## Files

- `index.html` - Main search page
- `article.html` - Article display page
- `search.js` - Search functionality and results display
- `article.js` - Article display and highlighting
- `styles.css` - Styling for both pages
- `README.md` - This file

## Data Source

The viewer reads from `../source_stories.json` (one directory up from the archive_viewer folder).

## Requirements

- Modern web browser with JavaScript enabled
- The `source_stories.json` file must be in the parent directory (`/workspaces/jour329w_fall2025/ludwig/stardem_draft/`)
