# Agent Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Beat Book Agent                             │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Anthropic Claude                        │   │
│  │              (claude-3-5-sonnet-20241022)                │   │
│  │                                                           │   │
│  │  System Prompt: Generate comprehensive beat book...      │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                            │
│                     │ Tool Calls                                 │
│                     ▼                                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Tool Executor                            │   │
│  │                                                           │   │
│  │  • Receives tool requests from Claude                    │   │
│  │  • Executes functions on StoryDatabase                   │   │
│  │  • Returns results back to Claude                        │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                            │
│                     │ Function Calls                             │
│                     ▼                                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 Story Database                            │   │
│  │                                                           │   │
│  │  In-memory JSON data (346 stories)                       │   │
│  │                                                           │   │
│  │  Tools Available:                                        │   │
│  │  ├─ get_stats()                                          │   │
│  │  ├─ search_by_keyword()                                  │   │
│  │  ├─ filter_by_topic()                                    │   │
│  │  ├─ filter_by_tag()                                      │   │
│  │  ├─ filter_by_location()                                 │   │
│  │  ├─ get_story_details()                                  │   │
│  │  ├─ filter_by_category()                                 │   │
│  │  ├─ filter_by_follow_up_rating()                         │   │
│  │  └─ get_related_stories()                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Workflow

```
┌─────────────┐
│   Start     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Agent receives initial prompt:         │
│  "Generate beat book for Education"     │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Phase 1: Discovery                     │
│                                          │
│  Tool: get_stats()                      │
│  → Total stories: 346                   │
│  → Topics: Education (87), Health...    │
│  → Top tags: Baltimore, Policy...       │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Phase 2: Exploration                   │
│                                          │
│  Tool: filter_by_topic("Education")     │
│  → Returns 87 story summaries           │
│                                          │
│  Tool: filter_by_follow_up_rating(7)    │
│  → Returns 23 high-value stories        │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Phase 3: Deep Dive                     │
│                                          │
│  Tool: get_story_details(story1_link)   │
│  → Full content of promising story      │
│                                          │
│  Tool: get_story_details(story2_link)   │
│  → Full content of another story        │
│                                          │
│  Tool: get_related_stories(story1_link) │
│  → Find coverage patterns               │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Phase 4: Synthesis                     │
│                                          │
│  Agent generates beat book:             │
│  • Introduction to Education beat       │
│  • Key people and institutions          │
│  • Recent coverage examples             │
│  • Story ideas and angles               │
│  • Sources and citations                │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Output saved to:                       │
│  • beat_book_YYYYMMDD_HHMMSS.md        │
│  • tool_log_YYYYMMDD_HHMMSS.json       │
└─────────────────────────────────────────┘
```

## Data Flow

```
┌────────────────────┐         ┌────────────────────┐
│  enhanced_beat_    │         │     prompt.txt     │
│  stories.json      │         │                    │
│                    │         │  System prompt for │
│  346 stories with: │         │  beat book gen     │
│  • Title           │         └─────────┬──────────┘
│  • Summary         │                   │
│  • Content         │                   │
│  • Tags            │         ┌─────────▼──────────┐
│  • Metadata        │         │                    │
└─────────┬──────────┘         │   Agent Script     │
          │                    │   beat_book_       │
          │                    │   agent.py         │
          │                    │                    │
          │    Loaded once     │   • StoryDatabase  │
          └────────────────────►   • Agent logic    │
                               │   • Tool executor  │
                               │                    │
                               └─────────┬──────────┘
                                         │
                                         │ Makes API calls
                                         │ with tool definitions
                                         │
                                         ▼
                               ┌─────────────────────┐
                               │                     │
                               │  Anthropic API      │
                               │  (Claude 3.5)       │
                               │                     │
                               └─────────┬───────────┘
                                         │
                                         │ Returns tool
                                         │ call requests
                                         │
                                         ▼
                               ┌─────────────────────┐
                               │                     │
                               │  Tool Results       │
                               │  (JSON data)        │
                               │                     │
                               └─────────┬───────────┘
                                         │
                                         │ Sent back
                                         │ to API
                                         │
                                         ▼
                               ┌─────────────────────┐
                               │                     │
                               │  Final Beat Book    │
                               │  (Markdown)         │
                               │                     │
                               └─────────────────────┘
```

## Tool Call Example

```
┌──────────────────────────────────────────────────────┐
│  Agent's Request to API                              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  {                                                   │
│    "model": "claude-3-5-sonnet-20241022",           │
│    "messages": [...],                               │
│    "tools": [                                       │
│      {                                              │
│        "name": "search_by_keyword",                 │
│        "description": "Search for stories...",      │
│        "input_schema": {                            │
│          "type": "object",                          │
│          "properties": {                            │
│            "keyword": {"type": "string"},           │
│            "limit": {"type": "integer"}             │
│          }                                          │
│        }                                            │
│      },                                             │
│      ...                                            │
│    ]                                                │
│  }                                                  │
└──────────────────────────────────────────────────────┘
                        │
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│  API Response                                        │
├──────────────────────────────────────────────────────┤
│                                                      │
│  {                                                   │
│    "stop_reason": "tool_use",                       │
│    "content": [                                     │
│      {                                              │
│        "type": "tool_use",                          │
│        "name": "search_by_keyword",                 │
│        "input": {                                   │
│          "keyword": "cellphone ban",                │
│          "limit": 20                                │
│        }                                            │
│      }                                              │
│    ]                                                │
│  }                                                  │
└──────────────────────────────────────────────────────┘
                        │
                        │ Execute tool locally
                        ▼
┌──────────────────────────────────────────────────────┐
│  Tool Execution                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  db.search_by_keyword(                              │
│    keyword="cellphone ban",                         │
│    limit=20                                         │
│  )                                                  │
│                                                      │
│  Returns: [                                         │
│    {                                                │
│      "title": "This school banned cellphones...",   │
│      "summary": "San Mateo High School...",         │
│      "link": "https://...",                         │
│      ...                                            │
│    },                                               │
│    ...                                              │
│  ]                                                  │
└──────────────────────────────────────────────────────┘
                        │
                        │ Send result back
                        ▼
┌──────────────────────────────────────────────────────┐
│  Next API Request with Tool Result                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  {                                                   │
│    "role": "user",                                  │
│    "content": [                                     │
│      {                                              │
│        "type": "tool_result",                       │
│        "tool_use_id": "...",                        │
│        "content": "[{...}, {...}]"                  │
│      }                                              │
│    ]                                                │
│  }                                                  │
└──────────────────────────────────────────────────────┘
```

## Context Window Comparison

### Traditional Approach (Context Overflow)
```
┌─────────────────────────────────────────┐
│  Single API Call                        │
├─────────────────────────────────────────┤
│                                          │
│  System Prompt: 1,000 tokens            │
│  Full JSON Data: 200,000 tokens ❌      │
│  User Message: 100 tokens               │
│                                          │
│  Total: 201,100 tokens                  │
│  Model Limit: 200,000 tokens            │
│  Result: OVERFLOW ERROR                 │
└─────────────────────────────────────────┘
```

### Tool-Based Approach (Success)
```
┌─────────────────────────────────────────┐
│  API Call 1                             │
├─────────────────────────────────────────┤
│  System Prompt: 1,000 tokens            │
│  Tool Definitions: 2,000 tokens         │
│  User Message: 100 tokens               │
│  Total: 3,100 tokens ✅                 │
└─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  API Call 2 (with tool result)          │
├─────────────────────────────────────────┤
│  Previous context: 3,100 tokens         │
│  Tool result: 5,000 tokens              │
│  Total: 8,100 tokens ✅                 │
└─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  API Call 3-10 (iterative)              │
├─────────────────────────────────────────┤
│  Each call adds ~5,000 tokens           │
│  Agent explores incrementally           │
│  Never exceeds context window ✅        │
└─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  Final API Call (generation)            │
├─────────────────────────────────────────┤
│  Condensed insights: 15,000 tokens      │
│  Generates beat book: 8,000 tokens      │
│  Total: 23,000 tokens ✅                │
└─────────────────────────────────────────┘
```

## Key Advantages

1. **No Context Overflow**: Only loads relevant data chunks
2. **Intelligent Exploration**: Agent decides what to investigate
3. **Transparent Process**: Every tool call is logged
4. **Scalable**: Works with datasets of any size
5. **Cost Efficient**: Fewer tokens per API call
