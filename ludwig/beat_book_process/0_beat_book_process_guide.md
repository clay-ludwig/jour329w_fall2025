# How to Create a Beat Book Using AI

*A Practical Guide for Journalism Students*

---

## What is a Beat Book?

A beat book is a narrative guide for reporters covering a specific topic or "beat" — such as education, local government, or crime. It introduces key people, institutions, ongoing issues, and potential story angles. Think of it as a comprehensive onboarding document for a journalist who needs to understand their coverage area quickly.

This guide walks you through the process of building a beat book using large language models (LLMs), based on lessons learned over a semester of experimentation.

---

## The High-Level Process

Creating an AI-assisted beat book involves four main phases:

1. **Data Preparation**: Gathering and organizing your source articles
2. **Enrichment**: Extracting entities, topics, and metadata from stories
3. **Generation**: Using LLMs to synthesize information into narrative form
4. **Refinement**: Editing, fact-checking, and improving the output

Each phase builds on the previous one. Rushing through early steps often leads to worse results later.

---

## Phase 1: Data Preparation

### Gathering Source Material

Start with a collection of news stories in a structured format (typically JSON). Your source data should include:

- Article titles
- Full article content
- Publication dates
- Any existing metadata (bylines, sections, etc.)

### Filtering Your Dataset

Not every story belongs in your beat book. Before processing, consider filtering out:

- Calendar listings and event announcements
- Letters to the editor and opinion columns
- Advertisements and sponsored content
- "Today in History" and similar filler content

You can filter programmatically by looking for keywords in titles or content fields. For example, excluding stories with "RELIGION CALENDAR" or "Section: Columns" in their metadata. This saves tokens and keeps your beat book focused on actual news.

### Narrowing Your Geographic or Topical Focus

Beat books work best when they're focused. Rather than covering "education across the entire state," consider narrowing to a specific county or school district. This makes the resulting guide more useful and helps the LLM maintain consistency.

---

## Phase 2: Enrichment

### Topic Classification

Before building a beat book, you may want to classify your stories by topic. You have two main approaches:

**Option 1: Let the LLM decide topics**
- Faster and requires less upfront work
- Risk of inconsistent or overly specific categories ("Harriet Tubman" instead of "History")
- Prompt the model to think in terms of newspaper sections (Sports, Business, Local News) to get broader categories

**Option 2: Define topics using embeddings**
- Generate embeddings for each story and cluster similar ones
- More work upfront but often produces more coherent groupings
- Lets you visually explore the topic landscape before committing to categories

Either way, consolidate your topics. Aim for 10-15 broad categories rather than dozens of narrow ones. Categories with only one or two stories should probably be merged.

### Entity Extraction

Extracting people, places, and organizations from your stories creates structured data you can analyze and feed into your beat book generation.

Key lessons for entity extraction:

- **Be specific about formatting**: Tell the model exactly how you want names formatted (e.g., "First Last, Title" or "City, State")
- **Exclude production staff**: Your prompt should explicitly exclude reporters, photographers, and the news organization itself
- **Provide examples**: Including example outputs in your prompt dramatically improves consistency
- **Iterate on your prompt**: Expect to run multiple versions before getting good results

A well-tuned entity extraction pass produces valuable context: who appears most frequently, which organizations dominate coverage, and how people's roles connect across stories.

### Screening Low-Relevance Stories

Even after initial filtering, some stories may not fit your beat. Consider adding a "screening" step where a smaller, faster model reviews each story and decides whether it truly belongs in your topic category.

For example, a story might be tagged as "Education" but actually focus on a school's sports team with minimal educational content. A screening model can catch these edge cases and exclude them before your main processing begins.

---

## Phase 3: Generation

### The Two-Stage Approach

The most effective beat book generation uses two models working together:

1. **First-pass model** (often smaller/cheaper): Reads stories in batches and takes notes, extracting key information
2. **Refinement model** (typically a frontier model): Synthesizes notes into polished prose, maintains consistency, and improves writing quality

This division of labor works because:
- Smaller models are good at extraction and summarization
- Larger models excel at synthesis, style, and coherence
- Processing in batches avoids token limits on any single request

### Batch Processing

Process stories in batches (typically 10-20 stories at a time) rather than all at once. This approach:

- Stays within token limits
- Allows the beat book to grow incrementally
- Lets you monitor quality as you go
- Makes it easier to recover from errors

Your script should track which stories have been processed and maintain state between runs.

### Prompting for Beat Books

Your prompts should establish:

- **Role**: Who is the model pretending to be? (e.g., "You are a senior editor onboarding a new reporter")
- **Audience**: Who will read this? (e.g., "an early-career journalist who knows the basics")
- **Geographic focus**: What area does this cover? Be explicit about excluding other regions
- **Temporal focus**: Emphasize recent coverage and ongoing issues over historical events
- **Style requirements**: Narrative prose vs. bullet points, plain language vs. formal

Include explicit instructions about what to preserve when updating an existing beat book. Without these, models tend to rewrite everything from scratch, losing valuable accumulated information.

### Managing Token Limits

Working with models that have strict token limits (like many Groq models) requires creativity:

- **Compact your input**: Consider summarizing or "compacting" stories before feeding them to the model
- **Limit context per person/topic**: Instead of all articles about someone, provide the most relevant excerpts
- **Use progressive building**: Start with high-level summaries, then add detail in subsequent passes

Surprisingly, compacted input sometimes produces better results — forcing the model to focus on key details rather than getting lost in full article text.

### Avoiding Common Pitfalls

**Plagiarism**: Models sometimes copy sentences verbatim from source articles. Consider adding a post-processing check that flags exact matches with your source data.

**Hallucination**: Particularly with contact information, phone numbers, and specific details. Never include "suggested" emails or phone numbers without verification.

**Outdated information**: Models may use training data over article content. Someone's title might be listed as "former" or "current" based on when articles were written, not their actual current status.

**LLM voice**: The tell-tale signs of AI writing — "In a time when..." or "This is a beat where..." — make your beat book less useful. Prompt for plain, direct language and consider having the refinement model specifically address this.

---

## Phase 4: Refinement

### Editing and Fact-Checking

No AI-generated beat book should go unedited. Your review should check:

- **Names and titles**: Are people's roles accurately described? Do titles match what the source articles say?
- **Institutional details**: Are organizations named correctly and consistently?
- **Ongoing vs. resolved**: Are "ongoing" issues actually still ongoing, or have they been resolved?
- **Geographic accuracy**: Did information from other regions sneak in despite your filtering?

Consider building a simple archive browser tool that lets you search your source articles by keyword. This makes fact-checking dramatically faster.

### Web Search for Verification

Some teams experimented with having Claude use web search for fact-checking. Results were mixed:

- Helpful for verifying current positions and contact information
- Prone to false positives (finding "errors" that aren't really errors)
- The model tends to overthink and flag semantic issues rather than factual ones

Web search works better for enrichment (finding additional context) than for systematic fact-checking.

### Word Count Management

Beat books tend to grow unwieldy. Set a target word count (around 5,000-7,000 words) and aggressively trim:

- One-off stories that don't represent broader trends
- Minor developments at individual schools
- Tangential details about non-key figures
- Redundant information covered elsewhere

A focused, navigable beat book is far more valuable than an exhaustive one.

---

## Presenting Your Beat Book

### Beyond Markdown

While Markdown is great for generation, consider how reporters will actually use the beat book:

- **HTML viewer**: A web-based viewer with section navigation and search
- **Linked sources**: Clickable citations that open the original articles
- **Visual hierarchy**: Clear headers, progress indicators, and readable typography

### Embeddings for Source Links

One powerful technique uses embeddings to create automatic source citations:

1. Generate embeddings for each sentence in your source articles
2. Generate embeddings for each sentence in your beat book
3. Compare similarity scores to link beat book sentences to their likely source articles
4. Display these as clickable citations in your viewer

This approach provides transparency (readers can verify claims) and creates a more interactive reading experience. Be careful with similarity thresholds — too low and you'll link everything; too high and you'll miss valid connections.

---

## Model Selection

### Frontier Models (Claude, GPT-4, etc.)

Best for:
- Final refinement and synthesis
- Complex narrative generation
- Maintaining consistent style and voice

Drawbacks:
- More expensive
- May have longer response times

### Open-Source/Groq Models

Best for:
- Batch processing of many stories
- Simple extraction tasks
- When you need fast iteration

Drawbacks:
- Stricter token limits
- Less reliable tool use
- May require more prompt engineering

### Local Models (Ollama)

Best for:
- Processing that involves sensitive source material
- Embedding generation (keeping data local)
- Situations where you need unlimited runs

Drawbacks:
- Depends on your hardware
- Generally less capable than cloud models

### Practical Recommendation

Use a combination: local or open-source models for heavy lifting (entity extraction, embeddings, first-pass reading) and frontier models for refinement and final synthesis.

---

## Key Lessons Learned

1. **Iterate on prompts**: Your first prompt won't be your best. Plan to revise multiple times based on output quality.

2. **Preserve progress**: When updating a beat book with new information, explicitly tell the model to preserve existing content. Otherwise, it will rewrite from scratch.

3. **Focus beats better results**: A beat book about one county's education system will be more useful than one covering an entire region.

4. **Fact-check everything**: AI models confidently state incorrect information. Build verification into your workflow.

5. **Style matters**: Prompt specifically for the writing style you want. Generic instructions like "write well" don't work.

6. **Build tools to help yourself**: Simple utilities (archive searchers, entity counters, embedding viewers) make the process much smoother.

7. **Token limits require creativity**: When you can't send all your data at once, think about what information is most valuable and how to compress it effectively.

8. **The two-stage approach works**: Having one model read and one model write produces better results than asking a single model to do everything.

---

## Conclusion

Building a beat book with AI is an iterative, experimental process. No single approach works perfectly for every dataset or topic. The key is to break the problem into manageable pieces, monitor quality at each stage, and be willing to adjust your approach based on what you observe.

The goal isn't to remove human judgment from journalism — it's to help reporters get up to speed faster on complex beats. A well-crafted beat book, even one built with AI assistance, still requires editorial oversight and verification. The AI handles the synthesis; you provide the judgment.

---

*This guide was created based on a semester of experimentation with AI-assisted beat book creation for the Easton Star-Democrat's coverage of Caroline County, Maryland.*