Beat Book Draft III
November 30, 2025

---

*My third beat book can be found in the `education_beat_book_refined.md` file. I was able to process roughly 30% of all education stories for this draft.*

For this beat book draft, I chose to focus on Caroline County. The first step I took was creating a new part of the generation process, where Claude Sonnet 4.5 searches the web for demographic and school information about Caroline County. After a bit of back-and-forth with Copilot, I got a working version of this system that consistently generated summaries containing several statistics, including county population totals/trends and the number of schools/students. I also asked Claude to cite its sources with inline URLs, which it mostly seemed to do correctly — though I'm not confident all of its sources are reliable.

Overall, I was pretty happy with how this turned out (at least as a first experiment). I was honestly expecting worse results since the Claude search tool is somewhat of a black box. On one hand, it's really useful that I can essentially get Claude to do a bunch of website scraping for me (that time-save was why I opted for this approach rather than building scrapers through Copilot), but the lack of transparency and predictability surrounding where/how it sources its information makes me slightly nervous about using this in an official capacity.

After creating the web search system, I got Copilot to write code that would automatically append Claude's statistics summary to the bottom of our Markdown file. This works well enough, but in the future I want to figure out a way to insert it in a place that makes logical sense (rather than always placing it at the bottom). One way I could accomplish this would be to actually pass the summary into another LLM and have it incorporate that information somewhere, rather than just programmatically appending it to the file.

In addition to the statistics being helpful for the reporter that reads this beat book, I noticed that the Groq/Claude models that actually wrote the beat book took some of the information (like the number of schools and students in Caroline County) from the summary and wrote about it elsewhere. This was unexpected but an added bonus.

With the help of Copilot, I made some other small tweaks to my prompts to make them more focused on Caroline County (as opposed to the entire Eastern Shore). I specifically wanted the models to exclude and ignore information unrelated to Caroline County — from what I can tell, this seems to mostly work. I like that it tried to localize certain issues to Caroline County, like the Maryland Blueprint plan. It didn't seem to stray far away from Caroline County either, which I was worried about.

I also switched from using Haiku 4.5 to Sonnet 4.5 for all models, which I have to say really didn't make the difference I was expecting. I was disappointed with the style of writing it chose, particularly around the "Reporter's Approach" section it generated. Reading that section made me roll my eyes since it sounded very AI-generated. I also just don't think the model needed to write that much under that section (or even incldue that section at all, arguably), since a lot of it was overgeneralized, bland advice. From my experience with both models, I think I prefer Haiku's writing style. I'd be curious to run this using Haiku instead of Sonnet to see which one I'd prefer.

# Copilot Transcript
clay-ludwig: I'd like to add a new step to my build_beat_book script (inside the stardem_draft directory) — we should use Claude to do web searches about Caroline County in Maryland to find information out about it, and we should include that information in our beat book by appending it to the beat book refined file under a section called "Quick Statistics". We should ask Claude to find out and list bullet point information about caroline county involving its population and education-specific information about the number of schools it has, the people in the schools, etc. (statistics) Please use the anthropic api and the Claude Sonnet 4.5 model to do the web searches — you should run the web search once per build_beat_book.py run. # Web search tool

---

The web search tool gives Claude direct access to real-time web content, allowing it to answer questions with up-to-date information beyond its knowledge cutoff. Claude automatically cites sources from search results as part of its answer.

<Note>
Please reach out through our [feedback form](https://forms.gle/sWjBtsrNEY2oKGuE8) to share your experience with the web search tool.
</Note>

## Supported models

Web search is available on:

- Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
- Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- Claude Sonnet 3.7 ([deprecated](/docs/en/about-claude/model-deprecations)) (`claude-3-7-sonnet-20250219`)
- Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
- Claude Haiku 3.5 (`claude-3-5-haiku-latest`)
- Claude Opus 4.5 (`claude-opus-4-5-20251101`)
- Claude Opus 4.1 (`claude-opus-4-1-20250805`)
- Claude Opus 4 (`claude-opus-4-20250514`)

## How web search works

When you add the web search tool to your API request:

1. Claude decides when to search based on the prompt.
2. The API executes the searches and provides Claude with the results. This process may repeat multiple times throughout a single request.
3. At the end of its turn, Claude provides a final response with cited sources.

## How to use web search

<Note>
Your organization's administrator must enable web search in [Console](/settings/privacy).
</Note>

Provide the web search tool in your API request:

<CodeGroup>
```bash Shell
curl https://api.anthropic.com/v1/messages \
    --header "x-api-key: $ANTHROPIC_API_KEY" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --data '{
        "model": "claude-sonnet-4-5",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": "What is the weather in NYC?"
            }
        ],
        "tools": [{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5
        }]
    }'
```

```python Python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "What's the weather in NYC?"
        }
    ],
    tools=[{
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 5
    }]
)
print(response)
```

```typescript TypeScript
import { Anthropic } from '@anthropic-ai/sdk';

const anthropic = new Anthropic();

async function main() {
  const response = await anthropic.messages.create({
    model: "claude-sonnet-4-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: "What's the weather in NYC?"
      }
    ],
    tools: [{
      type: "web_search_20250305",
      name: "web_search",
      max_uses: 5
    }]
  });

  console.log(response);
}

main().catch(console.error);
```
</CodeGroup>

### Tool definition

The web search tool supports the following parameters:

```json JSON
{
  "type": "web_search_20250305",
  "name": "web_search",

  // Optional: Limit the number of searches per request
  "max_uses": 5,

  // Optional: Only include results from these domains
  "allowed_domains": ["example.com", "trusteddomain.org"],

  // Optional: Never include results from these domains
  "blocked_domains": ["untrustedsource.com"],

  // Optional: Localize search results
  "user_location": {
    "type": "approximate",
    "city": "San Francisco",
    "region": "California",
    "country": "US",
    "timezone": "America/Los_Angeles"
  }
}
```

#### Max uses

The `max_uses` parameter limits the number of searches performed. If Claude attempts more searches than allowed, the `web_search_tool_result` will be an error with the `max_uses_exceeded` error code.

#### Domain filtering

When using domain filters:

- Domains should not include the HTTP/HTTPS scheme (use `example.com` instead of `https://example.com`)
- Subdomains are automatically included (`example.com` covers `docs.example.com`)
- Specific subdomains restrict results to only that subdomain (`docs.example.com` returns only results from that subdomain, not from `example.com` or `api.example.com`)
- Subpaths are supported (`example.com/blog`)
- You can use either `allowed_domains` or `blocked_domains`, but not both in the same request.

<Note>
Request-level domain restrictions must be compatible with organization-level domain restrictions configured in the Console. Request-level domains can only further restrict domains, not override or expand beyond the organization-level list. If your request includes domains that conflict with organization settings, the API will return a validation error.
</Note>

#### Localization

The `user_location` parameter allows you to localize search results based on a user's location.

- `type`: The type of location (must be `approximate`)
- `city`: The city name
- `region`: The region or state
- `country`: The country
- `timezone`: The [IANA timezone ID](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

### Response

Here's an example response structure:

```json
{
  "role": "assistant",
  "content": [
    // 1. Claude's decision to search
    {
      "type": "text",
      "text": "I'll search for when Claude Shannon was born."
    },
    // 2. The search query used
    {
      "type": "server_tool_use",
      "id": "srvtoolu_01WYG3ziw53XMcoyKL4XcZmE",
      "name": "web_search",
      "input": {
        "query": "claude shannon birth date"
      }
    },
    // 3. Search results
    {
      "type": "web_search_tool_result",
      "tool_use_id": "srvtoolu_01WYG3ziw53XMcoyKL4XcZmE",
      "content": [
        {
          "type": "web_search_result",
          "url": "https://en.wikipedia.org/wiki/Claude_Shannon",
          "title": "Claude Shannon - Wikipedia",
          "encrypted_content": "EqgfCioIARgBIiQ3YTAwMjY1Mi1mZjM5LTQ1NGUtODgxNC1kNjNjNTk1ZWI3Y...",
          "page_age": "April 30, 2025"
        }
      ]
    },
    {
      "text": "Based on the search results, ",
      "type": "text"
    },
    // 4. Claude's response with citations
    {
      "text": "Claude Shannon was born on April 30, 1916, in Petoskey, Michigan",
      "type": "text",
      "citations": [
        {
          "type": "web_search_result_location",
          "url": "https://en.wikipedia.org/wiki/Claude_Shannon",
          "title": "Claude Shannon - Wikipedia",
          "encrypted_index": "Eo8BCioIAhgBIiQyYjQ0OWJmZi1lNm..",
          "cited_text": "Claude Elwood Shannon (April 30, 1916 – February 24, 2001) was an American mathematician, electrical engineer, computer scientist, cryptographer and i..."
        }
      ]
    }
  ],
  "id": "msg_a930390d3a",
  "usage": {
    "input_tokens": 6039,
    "output_tokens": 931,
    "server_tool_use": {
      "web_search_requests": 1
    }
  },
  "stop_reason": "end_turn"
}
```

#### Search results

Search results include:

- `url`: The URL of the source page
- `title`: The title of the source page
- `page_age`: When the site was last updated
- `encrypted_content`: Encrypted content that must be passed back in multi-turn conversations for citations

#### Citations

Citations are always enabled for web search, and each `web_search_result_location` includes:

- `url`: The URL of the cited source
- `title`: The title of the cited source
- `encrypted_index`: A reference that must be passed back for multi-turn conversations.
- `cited_text`: Up to 150 characters of the cited content

The web search citation fields `cited_text`, `title`, and `url` do not count towards input or output token usage. 

<Note>
  When displaying API outputs directly to end users, citations must be included to the original source. If you are making modifications to API outputs, including by reprocessing and/or combining them with your own material before displaying them to end users, display citations as appropriate based on consultation with your legal team.
</Note>

#### Errors

When the web search tool encounters an error (such as hitting rate limits), the Claude API still returns a 200 (success) response. The error is represented within the response body using the following structure:

```json
{
  "type": "web_search_tool_result",
  "tool_use_id": "servertoolu_a93jad",
  "content": {
    "type": "web_search_tool_result_error",
    "error_code": "max_uses_exceeded"
  }
}
```

These are the possible error codes:

- `too_many_requests`: Rate limit exceeded
- `invalid_input`: Invalid search query parameter
- `max_uses_exceeded`: Maximum web search tool uses exceeded
- `query_too_long`: Query exceeds maximum length
- `unavailable`: An internal error occurred

#### `pause_turn` stop reason

The response may include a `pause_turn` stop reason, which indicates that the API paused a long-running turn. You may provide the response back as-is in a subsequent request to let Claude continue its turn, or modify the content if you wish to interrupt the conversation.

## Prompt caching

Web search works with [prompt caching](/docs/en/build-with-claude/prompt-caching). To enable prompt caching, add at least one `cache_control` breakpoint in your request. The system will automatically cache up until the last `web_search_tool_result` block when executing the tool.

For multi-turn conversations, set a `cache_control` breakpoint on or after the last `web_search_tool_result` block to reuse cached content.

For example, to use prompt caching with web search for a multi-turn conversation:

<CodeGroup>
```python
import anthropic

client = anthropic.Anthropic()

# First request with web search and cache breakpoint
messages = [
    {
        "role": "user",
        "content": "What's the current weather in San Francisco today?"
    }
]

response1 = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=messages,
    tools=[{
        "type": "web_search_20250305",
        "name": "web_search",
        "user_location": {
            "type": "approximate",
            "city": "San Francisco",
            "region": "California",
            "country": "US",
            "timezone": "America/Los_Angeles"
        }
    }]
)

# Add Claude's response to the conversation
messages.append({
    "role": "assistant",
    "content": response1.content
})

# Second request with cache breakpoint after the search results
messages.append({
    "role": "user",
    "content": "Should I expect rain later this week?",
    "cache_control": {"type": "ephemeral"}  # Cache up to this point
})

response2 = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=messages,
    tools=[{
        "type": "web_search_20250305",
        "name": "web_search",
        "user_location": {
            "type": "approximate",
            "city": "San Francisco",
            "region": "California",
            "country": "US",
            "timezone": "America/Los_Angeles"
        }
    }]
)
# The second response will benefit from cached search results
# while still being able to perform new searches if needed
print(f"Cache read tokens: {response2.usage.get('cache_read_input_tokens', 0)}")
```

</CodeGroup>

## Streaming

With streaming enabled, you'll receive search events as part of the stream. There will be a pause while the search executes:

```javascript
event: message_start
data: {"type": "message_start", "message": {"id": "msg_abc123", "type": "message"}}

event: content_block_start
data: {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}

// Claude's decision to search

event: content_block_start
data: {"type": "content_block_start", "index": 1, "content_block": {"type": "server_tool_use", "id": "srvtoolu_xyz789", "name": "web_search"}}

// Search query streamed
event: content_block_delta
data: {"type": "content_block_delta", "index": 1, "delta": {"type": "input_json_delta", "partial_json": "{\"query\":\"latest quantum computing breakthroughs 2025\"}"}}

// Pause while search executes

// Search results streamed
event: content_block_start
data: {"type": "content_block_start", "index": 2, "content_block": {"type": "web_search_tool_result", "tool_use_id": "srvtoolu_xyz789", "content": [{"type": "web_search_result", "title": "Quantum Computing Breakthroughs in 2025", "url": "https://example.com"}]}}

// Claude's response with citations (omitted in this example)
```

## Batch requests

You can include the web search tool in the [Messages Batches API](/docs/en/build-with-claude/batch-processing). Web search tool calls through the Messages Batches API are priced the same as those in regular Messages API requests.

## Usage and pricing

Web search usage is charged in addition to token usage:

```json
"usage": {
  "input_tokens": 105,
  "output_tokens": 6039,
  "cache_read_input_tokens": 7123,
  "cache_creation_input_tokens": 7345,
  "server_tool_use": {
    "web_search_requests": 1
  }
}
```

Web search is available on the Claude API for **$10 per 1,000 searches**, plus standard token costs for search-generated content. Web search results retrieved throughout a conversation are counted as input tokens, in search iterations executed during a single turn and in subsequent conversation turns.

Each web search counts as one use, regardless of the number of results returned. If an error occurs during web search, the web search will not be billed.

GitHub Copilot: I'll help you add a web search step to your beat book script to gather information about Caroline County, Maryland. Let me first examine the existing build_beat_book script. 

Searched for files matching `**/stardem_draft/**/build_beat_book.py`, 1 match

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py)

Now I'll create a comprehensive plan for adding the web search functionality to gather Caroline County statistics. Let me break this down: 

Created 4 todos

Starting: *Create web search function for Caroline County* (1/4)

Now I'll implement the web search functionality. I'll add a new function that uses Claude Sonnet 4.5 with the web search tool to gather information about Caroline County, Maryland. 

Using "Replace String in File"


```

```


Starting: *Integrate web search into build_beat_book flow* (2/4)

Now I need to update the state to include the Caroline County information and modify the build_beat_book function to call the search once at the beginning: 

Using "Replace String in File"


```

```
Now I'll modify the build_beat_book function to call the web search once at the beginning and append the statistics at the end: 

Using "Replace String in File"


```

```
Now I need to also add the Quick Statistics section at the end of the main processing loop when all batches are complete: 

Using "Replace String in File"


```

```


Starting: *Test the implementation* (4/4)

Now let me verify the implementation by checking the complete file and ensuring there are no syntax errors: 

Checked [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py), no problems found

Great! Now let me create a simple test to verify the web search function works correctly: 

Created [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/test_web_search.py)

Now let's test the web search function: 

Ran terminal command: cd /workspaces/jour329w_fall2025/ludwig/stardem_draft && python test_web_search.py

Perfect! The web search is working correctly. Now let me verify the complete implementation by reading the key parts of the updated build_beat_book.py file to ensure everything is properly integrated: 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py#1-1), lines 1 to 51

Let me check where the search function is called in the main flow: 

Searched for regex `search_caroline_county_info|caroline_county_info` (`**/ludwig/stardem_draft/build_beat_book.py`), 9 results

Perfect! Let me verify the logic flow by reading those sections: 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py#785-785), lines 785 to 815

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py#965-965), lines 965 to 995

Excellent! The implementation is complete. Let me now create a simple documentation file to explain the new feature: 

Made changes.

: Nice job - can you ask the Claude model to leave inline citations with links to its sources for each piece of info. it includes? Please also remove the test_web_search file

GitHub Copilot: Using "Replace String in File"


```

```


Ran terminal command: rm /workspaces/jour329w_fall2025/ludwig/stardem_draft/test_web_search.py

Created 4 todos

Perfect! I've successfully updated your build_beat_book.py script with the following changes:

## Summary of Changes

1. **Added web search functionality** using Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) with the web search tool to gather information about Caroline County, Maryland

2. **Key features:**
   - Searches once per script run (not per batch) for efficiency
   - Caches the results in the state file to avoid repeated searches
   - Gathers population and education statistics about Caroline County
   - **Now includes inline citations with clickable markdown links** to sources for each piece of information
   - Appends results to the refined beat book under a "Quick Statistics" section

3. **Integration points:**
   - Web search runs at the start of `build_beat_book()` if not already cached
   - Results are stored in `state['caroline_county_info']`
   - Statistics are appended to the refined beat book when all stories are processed
   - Duplicate protection ensures the section isn't added multiple times

4. **Removed** the test file as requested

The script will now automatically gather and include contextual information about Caroline County with properly sourced citations when you run it!

Made changes.

: We need to automatically always append the web search blurb Claude writes under a "Quick Statistics" section in our beat book .md file(s). We need to make sure it is there every time. We should do this programmatically

GitHub Copilot: I'll modify the script to ensure the Quick Statistics section is always appended to the beat book files after every batch processing, not just at the end. This way it's always present and up-to-date. 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py#420-420), lines 420 to 470

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py#355-355), lines 355 to 385

Now let me create helper functions to manage the Quick Statistics section and update the save_beat_book function: 

Using "Replace String in File"


```

```
Now update the save_beat_book function to always append the Quick Statistics: 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py#470-470), lines 470 to 490

Searched for text `def save_beat_book` (`**/ludwig/stardem_draft/build_beat_book.py`), 1 result

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py#648-648), lines 648 to 658

Now I need to modify the script to use the new helper functions. Let me update the key places where beat books are saved: 

Using "Multi-Replace String in Files"


```

```
Perfect! Now let me verify there are no syntax errors: 

Checked [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py), no problems found

Excellent! Now let me create a simple test to demonstrate that the Quick Statistics section will be properly managed: 

Created [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/test_quick_stats.py)

Ran terminal command: cd /workspaces/jour329w_fall2025/ludwig/stardem_draft && python test_quick_stats.py

Perfect! Now let me clean up the test file and create a summary: 

Ran terminal command: rm /workspaces/jour329w_fall2025/ludwig/stardem_draft/test_quick_stats.py

Perfect! I've updated the script to **automatically and programmatically** ensure the Quick Statistics section is always present in your beat book files. Here's what I implemented:

## Changes Made

### 1. **New Helper Functions**
- `strip_quick_stats_section()` - Removes any existing Quick Statistics section to prevent duplicates
- `append_quick_stats_section()` - Appends a fresh Quick Statistics section, first stripping any old version

### 2. **Updated `save_beat_book()` Function**
Now accepts an optional `caroline_county_info` parameter. When saving the **refined** beat book, it automatically:
- Strips any old Quick Statistics section
- Appends the current Quick Statistics section
- Ensures only one section exists (no duplicates)

### 3. **Automatic Application**
The Quick Statistics section is now appended **every time** the refined beat book is saved:
- After each batch refinement with Claude
- After checkpoint reviews (every 10 batches)
- At final completion

### 4. **Source Citations**
The web search prompt now requests inline markdown citations with clickable links for each piece of information, e.g., `Population: 33,406 ([source](https://example.com))`

## How It Works
1. Web search runs once at the start and results are cached
2. Every time `save_beat_book()` is called for the refined beat book file, it automatically appends the Quick Statistics
3. Duplicate protection ensures the section is never repeated
4. The section is always at the end of the file, properly formatted

The Quick Statistics section will now be **automatically maintained** throughout the entire build process without any manual intervention!

Made changes.

: In the web search prompt can you ask it not to add any additional commentary? It keeps adding little summaries like "Based on my search results, I found ..."

GitHub Copilot: Using "Replace String in File"


```

```
Done! I've updated the prompt to explicitly instruct Claude to:
1. NOT include any commentary, introductions, or summaries
2. Start immediately with the category heading and bullet points
3. Provide ONLY the factual statistics with citations

This should eliminate the "Based on my search results..." type preambles.

Made changes.

: I'm seeing this in the end result. this is still not ideal. we need to ask it to form a "report" or something in a way that makes it aware this will need to be clean

GitHub Copilot: Using "Replace String in File"


```

```
I've restructured the prompt to emphasize that Claude is creating a "reference report" that will be directly inserted into a publication-ready document. Key changes:

1. **Framed as a professional report** - not just answering a question
2. **Explicitly states the output will be inserted directly** into a markdown document
3. **Instructs to silently resolve ambiguities** rather than commenting on them
4. **Emphasizes "publication-ready"** to set expectations for polish
5. **Lists critical formatting requirements** at the top for clarity

This should eliminate the meta-commentary about search challenges and produce clean, ready-to-publish statistics.

Made changes.

: While I'm thinking of it, can you also switch to using Claude Sonnet 4.5 instead of Claude Haiku 4.5 for the claude refinement steps>

GitHub Copilot: Using "Multi-Replace String in Files"


```

```


Checked [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py), no problems found

Perfect! I've successfully switched the script from Claude Haiku 4.5 to **Claude Sonnet 4.5** for all refinement and review steps. This will provide higher quality editorial refinement of your beat book. The changes include:

1. **`refine_with_claude()`** - Now uses `claude-sonnet-4-5-20250929`
2. **`review_with_claude()`** - Now uses `claude-sonnet-4-5-20250929` 
3. Updated all docstrings and print statements to reflect Sonnet instead of Haiku
4. The main script docstring now correctly states it uses Claude Sonnet 4.5

The web search for Caroline County statistics already uses Claude Sonnet 4.5, so now all Claude operations in the script use the more powerful Sonnet model for better quality outputs.

Made changes.

: Good. Finally, I'd like to adjust all the prompts (except the web search one) to focus on creating a beat book about education in **Caroline County, MD** — it should ignore and exclude information about other counties covered by the Star-Democrat.

GitHub Copilot: Using "Multi-Replace String in Files"


```

```


Checked [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py), no problems found

Perfect! I've updated all the prompts (except the web search one) to focus exclusively on **Caroline County, Maryland** education. The changes include:

## Updated Prompts:

1. **BEAT_BOOK_PROMPT** - Now explicitly states the beat book is ONLY about Caroline County and instructs to EXCLUDE/IGNORE information about other counties (Dorchester, Kent, Queen Anne's, Talbot, etc.)

2. **CLAUDE_REFINE_PROMPT** - Updated to focus on Caroline County education, with new editorial priority #1 emphasizing "Caroline County focus" and instructions to remove any information about other counties

3. **CLAUDE_REVIEW_PROMPT** - Changed to cover "education in Caroline County, Maryland" with review criteria emphasizing Caroline County-specific information and aggressively cutting any content about other counties

4. **INITIAL_BEAT_BOOK & INITIAL_REFINED_BEAT_BOOK** - Headers now say "Caroline County, Maryland" instead of "Maryland's Eastern Shore"

The script will now build a beat book focused specifically on Caroline County schools, officials, and education issues, filtering out information about the other Eastern Shore counties.

Made changes.