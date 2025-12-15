Final Beat Book
December 15, 2025

---

My final beat book can be accessed in the `viewer.html` file located inside the `/beatbook_viewer` directory. To open it, run a Python web server in that directory by using `python -m http.server`

---

![Final Beat Book](sc-1.png)

My final beat book was a bit of a happy accident. Going into this assignment, I decided that my goal was to improve my "Different Beat Book" from last week. But I also wanted to redo parts of the core beat book generation process, including the models and prompts I used to generate the beat book Markdown.

I also wanted to make the process fully (or near-fully) automated. Ideally, anyone with the right input data could follow this process without much human intervention to generate their own beat book. I was mostly successful at this, with a couple of exceptions which I'll explain later.

![Final Beat Book](sc-2.png)

I decided to broadly split the creation process into two chunks: the Markdown creation (for the core beat book) and the web viewer (the website to view the beat book Markdown, which includes the embeddings-powered links to source stories).

Here's the full list of things I changed or improved for this beat book:

### 1. Models
I did most of my work on December 14, when Anthropic was having a [really bad day](https://status.claude.com/#:~:text=incidents%20reported%20today.-,Dec%2014%2C%202025,-Elevated%20errors%20across), so I decided to switch to the new `GPT-5.2` model. As an added bonus, I got to use its [newly-added](https://platform.openai.com/docs/guides/tools-apply-patch) `apply_patch` tool so that the model wouldn't have to output the *full* beat book every time it made a change. Instead, it's only required to output smaller structured diffs, which are then applied to the Markdown file.

I also switched away from Groq models after a first attempt that netted mediocre results and several more Groq accounts being banned (whoops). I switched to the `gemma3:4b` local Ollama model by Google. The old Groq script remains (`markdown_creator/build_beat_book_groq.py`) and the new one can be accessed at `markdown_creator/build_beat_book_local.py`. I was able to run this Gemma model locally on my MacBook with 16GB of RAM fairly quickly without problems.

### 2. Prompts
We have three prompts for this beat book:
- One prompt that runs at the start of each generation, which conducts a series of web searches about Caroline County, MD and outputs a list/summary of statistics it finds. Instead of programmatically tacking this summary onto the bottom of the beat book, I opted to feed it into the "refinement" model I talk about below.
- Another prompt that instructs a model to do a "first pass" for articles that are fed to it in batches. The model that runs this prompt is traditionally a Groq model, but in this case was the Gemma Ollama model.
- A final "refinement" prompt, excuted by a frontier model (in this case GPT-5.2), that instructs the model to harmonize the information from the latest batch with the ongoing beat book document. This prompt includes meta information about the process to help the model understand its place and importance in the process.

All three prompts were rewritten for this final assignment to be more concise and direct about each model's role in the process. The old prompts felt like a roundabout way to get to my desired output, whereas these prompts directly give each model their "role play" scenario (i.e. the Ollama model's job is to be a "reporter taking notes," whereas GPT's job is to be an "editor" who harmonizes the notes passed to them by a reporter).

I also spent *a lot* more time trying to get the model's voice to sound more authentic and human. I was trying very hard to avoid the classic "LLM speak," both because it personally annoys of me and because I actually find it distracting when I'm trying to read something. I generally prefer Claude's written voice to GPT's, so I actually asked Opus 4.5 in Copilot to help me write this part of the prompt by asking it to "look internally at its system prompt instructions and guiding documents to form a voice that closely matches yours." The result is actually pretty good in my opinion (albeit maybe lacking some personality).

### 3. "Compacted" stories JSON
Earlier this semester, I generated a "compacted" version of the education beat's `source_stories.json` using another local Ollama model on my computer. This compacted version essentially took the `content` value of each story and distilled it, using some clever prompting, down to its most basic and concise form.

Purely as an experiment, I decided to use *this* as my input JSON for the Gemma model — I assumed this would result in some very bad results. To my absolute surprise and mystery, it worked so well that I didn't even bother attempting one with the normal `source_stories.json` file, which contained the full story content. I have some theories for why this worked better, but I'm honestly not really sure. I think maybe having the "compaction" prompt (which can be found inside the `stardem_final/compaction` directory) focus so much on the key details of each story may have helped "focus" the Gemma model to only write about the most important details. I'm really not sure though and I would love to know your thoughts.

Going forward, I want to explore using this compaction technique because I was shocked at how much the models were able to achieve, given such a limited look at each story's text content.

### 4. Beat book viewer styles
The first iteration of the beat book viewer looked more like a tech demo than a real product, so I really tried to focus on cleaning up the UX/UI of this beat book viewer. I removed all of Claude's purple and blue links and opted for a more muted black/white/blue color scheme. I also changed the typography to be easier to read and refined the spacing between elements.

I also recreated the page's header to contain a section selector dropdown. This section selector works completely automatically, in that it literally reads the source beat book Markdown and identifies any H2 tags ('##' in Markdown) and provides them as options in the dropdown. As you scroll, the section dropdown automatically changes to display the section you're viewing. This system makes it so that you could "plug and play" any other beat book file, as long as it's in the appropriate format (which I write about below).

I also added an image to the top of my beat book that I found by Googling "Caroline County, MD" — it's one of the images inside of the carousel Google provides. This was notably *not* automated — early on this weekend, I experimented with the model inserting Markdown links to images throughout the beat book, but this was a complete failure since all the links were hallucinated. I'll have to keep thinking of ways to automatically add images going forward, since I really think they add something to the beat book (even if it's just purely cosmetic).

Finally, I tweaked tons of small UX things, including button hitbox sizes, hover styles and consistent byline/date formatting for stories. One small issue I kept noticing was that some stories lack line break characters, so I also added a regex algorithm that automatically inserts line breaks after sentences (this is admittedly very brittle, so a better solution is needed here). I also added a progress indicator to the bottom of the header to give readers a sense of place in the beat book.

---

Here are the things I mostly kept the same:

### 1. Embeddings for "source stories"
I built an embeddings system for my Different Beat Book to provide in-text citations to source stories, and it worked so well that I decided to keep it the same for the final beat book. I opted to generate embeddings for each *sentence* within each story and beat book (rather than the full articles) for granular accuracy.

In retrospect, I should've spent some time refining this approach because I identified a few incorrectly-linked stories in the beat book. In this paragraph, for example, there are two links:
```
CCPS calendar decisions are closely tied to winter weather closures and the district’s make-up day plan. For 2025–26, the Board of Education adopted a post–Labor Day start, with students beginning Tuesday, Sept. 2, 2025, and teachers returning Aug. 25. The calendar built in three inclement-weather days.
```
The last sentence, "The calendar built in three inclement-weather days," is linked to a 2024 article that contains the sentence "Two inclement weather days are built into the calendar." It is understandable why the model linked back to that story with such high confidence given its similar wording, but unfortunately it is for the wrong school year (and contains a factual mismatch). I'll need to figure out how to work around errors like these going forward.

### 2. Fully automatic viewer & JSON format
The HTML viewer dynamically loads a custom JSON format (which I called the `embeddings_format`) of the beat book, where each sentence is linked back to a source article with a similarity rating. We generate this format using the `md_to_beatbook_format.py` file inside the `stardem_final/beatbook_viewer/embeddings_format` directory. Here's an example of a sentence outputted in this format:
```
{
    "content": "Caroline County is a rural county on Maryland’s Eastern Shore.",
    "source": "search-hits__hit--3192",
    "source_sentence": "In Caroline County, on the eastern shore of Maryland, public schools have a new pilot program in two middle schools.",
    "source_sentence_index": 2,
    "source_title": "How Maryland schools are cracking down on cell phones this fall",
    "similarity": 0.524,
    "sentence_similarity": 0.6049,
    "article_similarity": 0.3352
}
```
Our HTML viewer could theoretically load *any* beat book in this format, and we are able to adjust our threshold in our code to show links above a certain similarity score. In my beat book, I opted for a score of `0.6` or greater (meaning sentences with similarity >= 0.6 turn into links).

---

I used Copilot a lot during this assignment, and asked it to create a new Markdown file for each chat. They can all be found in the `stardem_final` directory.