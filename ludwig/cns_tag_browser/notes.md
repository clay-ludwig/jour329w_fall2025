CNS Tag Browser
September 29, 2025

---

Command:
```bash
# See tags with the most posts
uv run sqlite-utils memory data/tags.json "SELECT name, count FROM tags ORDER BY count DESC LIMIT 10"
```

Output:
```
[{"name": "Politics", "count": 1172},
 {"name": "maryland", "count": 1127},
 {"name": "CNS TV", "count": 804},
 {"name": "Capital News Service", "count": 756},
 {"name": "hero", "count": 728},
 {"name": "cns", "count": 591},
 {"name": "Sports", "count": 494},
 {"name": "cnstv", "count": 375},
 {"name": "Baltimore", "count": 371},
 {"name": "Donald Trump", "count": 333}]
```

Command:
```bash
# See tags that contain Trump
uv run sqlite-utils memory data/tags.json "SELECT name, count FROM tags where name like '%Trump%' ORDER BY count DESC LIMIT 10"
```

Output:
```
[{"name": "Donald Trump", "count": 333},
 {"name": "president trump", "count": 32},
 {"name": "President Donald Trump", "count": 27},
 {"name": "Melania Trump", "count": 7},
 {"name": "Donald J. Trump", "count": 6},
 {"name": "Ivanka Trump", "count": 5},
 {"name": "Barron Trump", "count": 4},
 {"name": "Donald Trump Jr.", "count": 3},
 {"name": "Eric Trump", "count": 3},
 {"name": "Donald Trump Election", "count": 2}]
```

Command:
```bash
# See tags that contain Baltimore
uv run sqlite-utils memory data/tags.json "SELECT name, count FROM tags where name like '%Baltimore%' ORDER BY count DESC LIMIT 20"
```

Output:
```
[{"name": "Baltimore", "count": 371},
 {"name": "Baltimore", "count": 314},
 {"name": "baltimore ravens", "count": 49},
 {"name": "Baltimore City", "count": 39},
 {"name": "baltimore orioles", "count": 29},
 {"name": "Baltimore County", "count": 25},
 {"name": "Baltimore Bridge Collapse", "count": 15},
 {"name": "Port of Baltimore", "count": 13},
 {"name": "Baltimore Income Featured", "count": 11},
 {"name": "Baltimore County Public Schools", "count": 8},
 {"name": "Baltimore City Police", "count": 7},
 {"name": "Baltimore police", "count": 6},
 {"name": "Baltimore Police Department", "count": 6},
 {"name": "Baltimore Trauma", "count": 6},
 {"name": "baltimore city crime", "count": 5},
 {"name": "baltimore crime", "count": 5},
 {"name": "baltimore trauma", "count": 5},
 {"name": "Baltimore City Public Schools", "count": 4},
 {"name": "Baltimore Colts", "count": 4},
 {"name": "Baltimore City Council", "count": 3}]
```

Evaluation:
Through these commands we can programmatically get a sense of our JSON data, which is otherwise quite unwieldly to sort through by hand. These commands give us small excerpts of the data to help sample things based on the arguments in the command—for example, the last command allows us to see the 20 most-used tags (and their use counts) related to Baltimore.

My biggest takeaway from running these commands was that the CNS tags are definitely a mess! The fact that CNS TV and Capital News Service are top-used tags, and each contain duplicates like "cns" and "cnstv," provides almost no useable data for sorting and searching purposes.

---

### Tagging Feature Wishlist
- After seeing the NY Times' Cheatsheet tool today, I feel like a spreadsheet-like interface for viewing the data seems like a good foundation.
- Since there is a crap ton of data in our JSON, some kind of memory management system that only keeps the visible subset of the spreadsheet loaded in memory would probably be ideal! Don't want to melt my poor MacBook Air.
- Ideally there should be ways to sort different columns by clicking on their headers (similar to, say, the Finder on Mac). For example, I could click on the "count" column header to sort the spreadsheet's rows by ascending or descending order based on that row's values. For non-numeric columns, I would sort alphabetically by ascending or descending order.
- By default, the tags should be sorted by count (in descending order).
- A filtering system that could let me replicate the commands written above would be very useful. I.e. you could set a filter phrase to only display items that contain that phrase in one of their rows.
- Some kind of CMD+F search across the entire spreadsheet would be very handy. In my dreams it'd be more than just a keyword search, so I may attempt to go way too far and try my hand at semantic search using embeddings. We will see if I can vibe code that, but I have a feeling I, uh, won't!
    - I just realized the last two items are basically the same feature.
- Another insanely advanced feature, but a chatbot on the side (like a Copilot inside of my spreadsheet app) would go hard. My goal is to make calls to the Groq or Gemini API (since they're both free) and use one of their models to be an assistant that could summarize data. Almost like a mini Notebook LM.

---

### Copilot Process

Feature: 
Copilot suggestion: 
Accepted/modified: 
How well it worked: 

Feature: 
Copilot suggestion: 
Accepted/modified: 
How well it worked: 

Feature: 
Copilot suggestion: 
Accepted/modified: 
How well it worked: 

---

### Testing
Write about testing here.

---

### Reflection
- What surprised you about working with Copilot?
- Which prompts worked best for getting useful suggestions?
- What was frustrating or challenging?
- How would you change your approach next time?

---

### Copilot Transcript
