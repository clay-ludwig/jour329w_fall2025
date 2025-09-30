# CNS Tag Browser

A user-friendly web application for browsing and analyzing CNS Maryland news tags data.

## Features

### Current Features
- **Sortable Table Interface**: View all tag data in a spreadsheet-like format
  - Click column headers to sort (cycles through ascending, descending, and no sort)
  - Default sort: by `count` in descending order
  - Columns: ID, Count, Name, Slug, Description, Taxonomy, Link, Meta
  
- **Search Functionality**: Real-time search across tag names, slugs, descriptions, and IDs

- **Responsive Design**: Clean, modern interface that works on various screen sizes

- **API Key Management**: Store your Groq API key for future AI chat functionality

- **Right Sidebar**: Dedicated space for upcoming AI chat features

### Upcoming Features
- AI-powered chat interface to query and analyze tag data
- Data visualization and analytics
- Export functionality
- Tag editing capabilities

## Getting Started

### Prerequisites
- Python 3.7 or higher
- A modern web browser (Chrome, Firefox, Safari, Edge)

### Running the Application

1. Navigate to the tag browser directory:
   ```bash
   cd /workspaces/jour329w_fall2025/ludwig/cns_tag_browser
   ```

2. Start the Python server:
   ```bash
   python3 server.py
   ```

3. Open your browser and go to:
   ```
   http://localhost:8000
   ```

4. The app will automatically load the tags data from `data/tags.json`

### Using a Different Port

If port 8000 is already in use, you can specify a different port:

```bash
PORT=8080 python3 server.py
```

## Usage Guide

### Sorting
- Click any column header to sort by that column
- First click: Sort ascending (▲)
- Second click: Sort descending (▼)
- Third click: Remove sort (returns to default count-based sort)

### Searching
- Type in the search box to filter tags in real-time
- Search matches: tag names, slugs, descriptions, and IDs
- Clear the search box to show all tags again

### API Key Setup
1. Click on the API key input field in the right sidebar
2. Enter your Groq API key
3. Click "Save" or press Enter
4. The key is securely stored in your browser's local storage

## File Structure

```
cns_tag_browser/
├── index.html          # Main HTML structure
├── server.py           # Python HTTP server
├── README.md           # This file
├── scripts/
│   └── app.js         # JavaScript application logic
└── styles/
    └── style.css      # CSS styling
```

## Data Source

The application loads tag data from:
```
/workspaces/jour329w_fall2025/data/tags.json
```

This file contains tag information from CNS Maryland news articles, including:
- Tag ID and count
- Tag name and slug
- Description and taxonomy
- Link to tag page
- Associated metadata

## Technical Details

### Frontend
- Pure HTML5, CSS3, and vanilla JavaScript
- No external dependencies or frameworks
- Responsive design with CSS Grid and Flexbox
- Local storage for API key persistence

### Backend
- Python built-in `http.server` module
- RESTful API endpoint: `/api/tags`
- CORS-enabled for development
- Serves static files and JSON data

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

## Future Development

The AI chat sidebar is prepared for integration with Groq's LLM API. Future updates will include:
- Natural language queries about tag data
- Data insights and recommendations
- Automated tag analysis
- Pattern detection and reporting

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Try using a different port: `PORT=8080 python3 server.py`

### Tags not loading
- Verify the `tags.json` file exists at `/workspaces/jour329w_fall2025/data/tags.json`
- Check browser console for error messages
- Ensure the server is running

### Search not working
- Try refreshing the page
- Clear browser cache
- Check browser console for JavaScript errors

## License

Part of the JOUR329W Fall 2025 coursework.
