Different Beat Book
December 6, 2025

---

*You can access my beat book by opening the `viewer.html` file.*

*As I write below, I had to do some work offline on my MacBook. I created two Copilot Markdown files: one for my codespace conversation and another for my conversation with Copilot locally on my computer.*

---

For this assignment, I decided to focus on solving the problem of inaccurate in-text citations in our beat books (which affected how I present the beat book to readers). We have seen in class that the Groq models are not good at generating their own links or citations to Star-Democrat articles, so I wanted to take a stab at an alternative method of providing these. The result ended up being a similarly structured beat book on the surface, but one that encourages a different, more methodical and reader-driven way of engaging with it.

![Beat book viewer](beat_book_viewer.png "Beat book viewer")

The system for creating these clickable in-text citations is somewhat simple at first glance: we generate embeddings for each story's content, then generate embeddings for our beat book itself, then semantically compare sentences between our beat book and the source stories and link them together to provide clickable "sources" for key information in our beat book.

To achieve this without sending any of the Star-Democrat's stories to frontier model providers like OpenAI, I moved some of my work offline onto my MacBook and used Google's local `embeddinggemma` model through Ollama to make embeddings. I relied on the `source_stories.json` file inside my stardem_different directory, which contains 629 education stories. With the help of Copilot, I wrote a Python script that generates embeddings for the `content` value inside each story's JSON entry, and then outputs them into a new file called `source_stories_embeddings.json`. I also created a "granular" version of this script, which generates an embedding for each *sentence* within each story's `content` value — this obviously takes much longer, but can be used to improve the accuracy of this whole process.

*(The great thing about these local embeddings models is that they're both high-fidelity, from what I can tell, and very fast. Running the granular version of this script took about 15 minutes on my MacBook Pro with 16GB of RAM. Not too bad for processing every single sentence within every single article!)*

I also generated embeddings for each sentence of the beat book itself, and asked Copilot to write the `md_to_beatbook.py` Python Script, which conducts a similarity check for each sentence in the beat book to find the most similarly-worded sentence within each Star-Democrat article, and returns a similarity score for each one.

To provide the source articles to the reader in an intuitive way, I decided to display our beat book as an HTML webpage. The page is deceivingly simple — it appears to contain a basic article-style layout, but it includes highlighted sentences that will open a readable copy of the "source" article they came from when clicked. I am able to adjust a `similarity` threshold in the Javascript code to determine how "easily" these links appear. If I set the threshold to 0, every single sentence would be hyperlinked (often to stories that weren't very similar to the sentence). In my testing, though, I found ~0.6 to be a good middle ground between over- and under-linking to source material.

Instead of opening the Star-Democrat's website for each link, this beat book viewer also acts as an archive viewer, since the articles open inline on the webpage itself. I have found this interface to be very intuitive while reading through the beat book, since I can click through the source material to optionally "drill in" if I want to learn more about something specific.

I was "inspired" (inspired is definitely the wrong word though) by the Washington Post's AI underlines that I've been seeing more recently, which when used make articles feel more "self-guided," if that makes sense, since you can explore a given topic more if you choose.

![Post AI](post_ai_screenshot.png "Post AI")

The results from this experiment were fairly good in my opinion! There is still definitely room to improve, but I like being able to easily click into certain stories to learn more information. In addition to testing this with my Caroline County education beat book, I also used my old (much larger) v1 beat book that was for the whole Eastern Shore's education beat. The results for both beat books were about the same quality, which suggests this system could likely be ported over to other beat books, including those that cover different topics and are presented in less narrative structures. I tried to design this system to be modular for any beat book structure or topic.

There is definitely room for improvement though, like I said. I really wanted to visually highlight the closest-matching sentence(s) when a reader clicks on a link to a story to indicate where within an article it found a match, but I couldn't figure out how to do that.
