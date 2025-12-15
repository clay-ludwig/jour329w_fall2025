# Copilot Conversation Summary

**Date:** December 15, 2025

---

## Task

The user asked me to create a comprehensive guide for building beat books using AI, based on the extensive notes and code from a semester of experimentation. The guide was to be written at a broad level (not overly technical) and placed in the `guide_notes.md` file in the `beat_book_process` directory. The user requested that recent assignments—particularly the "different beat book" and "final beat book"—be weighted more heavily in the guide.

---

## What I Did

### 1. Explored the Workspace

I examined the `beat_book_process` directory, which contained dozens of files including:
- Python scripts (`build_beat_book.py`, `add_entities.py`, `classify_topics.py`, etc.)
- Notes files from each assignment (`stardem_final_notes.md`, `stardem_different_notes.md`, `stardem_nearly_final_notes.md`, etc.)
- A `combined.txt` file containing all the code and notes merged together

### 2. Read the Key Notes Files

I read through the notes from multiple assignments to understand the semester's progression:

- **stardem_topics_notes.md**: Topic classification using LLMs, consolidating broad categories
- **stardem_entities_notes.md**: Entity extraction (people, places, organizations), prompt iteration for consistent formatting
- **stardem_topic_entities_notes.md**: Combining topics and entities, adding screening steps with smaller models
- **notes.md (stardem_choice)**: Early beat book attempts, challenges with Groq rate limits, source list generation
- **stardem_draft_notes.md**: Web search for county statistics, geographic focus on Caroline County
- **stardem_nearly_final_notes.md**: Fact-checking experiments, plagiarism detection, building an archive browser
- **stardem_different_notes.md**: Embeddings-based source citations, HTML viewer for beat book presentation
- **stardem_final_notes.md**: Final refinements including GPT-5.2 with apply_patch, local Ollama models, compacted story inputs, improved prompts and UI

### 3. Created the Guide

I synthesized the lessons from all these notes into a comprehensive guide organized into four phases:

1. **Data Preparation**: Gathering sources, filtering non-news content, narrowing focus
2. **Enrichment**: Topic classification, entity extraction, screening stories
3. **Generation**: Two-stage model approach, batch processing, prompt engineering, managing token limits
4. **Refinement**: Fact-checking, web search verification, word count management

I also included sections on presenting beat books (HTML viewers, embeddings for citations), model selection strategies, and eight key lessons learned.

---

## Key Insights from the Semester's Work

The notes revealed several important discoveries:

- **Two-stage generation works best**: A smaller model reads stories and takes notes; a frontier model refines into polished prose
- **Compacted inputs can improve results**: Summarizing stories before feeding them to the model sometimes produces better beat books than using full article text
- **Embeddings enable source citations**: Generating embeddings for each sentence allows automatic linking of beat book claims to source articles
- **Fact-checking with AI is unreliable**: Claude's web search tool produced many false positives when asked to verify facts
- **Plagiarism is a real risk**: Models sometimes copy sentences verbatim from sources; this needs post-processing detection
- **Geographic focus matters**: Beat books covering a single county produced more useful, consistent results than broader regional guides
- **Prompt iteration is essential**: Most assignments involved 4-7 iterations of prompts before achieving acceptable results

---

## Files Created

- `guide_notes.md`: The comprehensive beat book creation guide (~2,000 words)
- `guide_copilot.md`: This conversation summary
