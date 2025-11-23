November 22, 2025
Beat Book Draft II

---

My new beat book can be accessed in the `education_beat_book_refined_v2.md` file.

In this beat book, I adjusted the prompt in the Claude-based refinement step using Copilot to make it more aggressive in excluding certain information. My goal was to shorten the beat book to under 15 pages, which this attempt succeeded at (it's now at 10) — though now I'm wondering if it's not detailed enough? Curious to know your thoughts.

One of the other tweaks I made was to include the current word count of the beat book to Claude by injecting it into its prompt. By giving it this context, it could guage whether it should be focused on cutting things or writing more information. This seemed to be an effective way at controlling the length of the beat book. From what I can tell, it also helped cut out certain parts that were overly focused on one-off stories. This is an improvement over my first attempt, which had references to random stories that weren't that important for a new reporter to learn about the beat.

# Copilot Transcript
clay-ludwig: I'd like to slightly refine our "refinement" prompt with Claude models to be more aggressive about cutting unnescessary details — especially about one-off stories that aren't important to the broader trends of the Eastern Shore and Easton Star-Democrat coverage. Also, can you feed the Claude model the current word count in the prompt and ask it to aim to keep the beat book to 7,000 words or under, taking that word count as its guide on whether to trim or add more?

GitHub Copilot: I'll help you refine the Claude refinement prompt to be more aggressive about cutting unnecessary details and add word count guidance. 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py#85-85), lines 85 to 185

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py#185-185), lines 185 to 265

Now let me look at the regular refinement function to update it: 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py#265-265), lines 265 to 365

Now let me check the review function and update both prompts with word count awareness and more aggressive trimming: 

Using "Multi-Replace String in Files"


```

```
Now I need to update the function calls to calculate and pass the word count: 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py#275-275), lines 275 to 335

Using "Multi-Replace String in Files"


```

```
Let me check the review function more carefully: 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py#360-360), lines 360 to 410

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_draft/build_beat_book.py#410-410), lines 410 to 440

Using "Replace String in File"


```

```
Perfect! I've successfully updated the build_beat_book.py script with the refinements you requested:

## Changes Made:

### 1. **More Aggressive Trimming Guidance**
Both Claude prompts now emphasize cutting one-off stories that don't represent broader trends:

- **Explicitly targets for removal:**
  - One-off stories that don't illustrate broader trends (e.g., a single school's new sign)
  - Minor school-level developments that don't reflect systemic issues
  - Story ideas that are too narrow or time-bound
  - Details about individuals who aren't key decision-makers

- **Focuses on regional/systemic importance:**
  - Issues affecting multiple districts across the Eastern Shore
  - Key decision-makers (superintendents, board chairs, influential advocates)
  - Recurring themes and systemic challenges
  - Story angles with broad applicability

### 2. **Word Count Management (7,000-word target)**
Both prompts now:

- **Calculate and display** the current word count to Claude
- **Provide clear guidance:**
  - If OVER 7,000 words: "You MUST be aggressive about cutting content"
  - If UNDER 7,000 words: "You have room to add valuable content, but still prioritize quality"
- **Frame word count as an editorial responsibility** - emphasizing that conciseness is more valuable than exhaustiveness

### 3. **Enhanced Review Criteria**
The comprehensive review prompt (every 10 batches) now includes a specific question for Claude to ask: *"Would a reporter who starts this job 6 months from now care about this detail? Does it represent a pattern or just a single incident?"*

The prompts will now help Claude maintain a focused, high-value beat book that emphasizes systemic Eastern Shore education issues while staying under the 7,000-word target.

Made changes.