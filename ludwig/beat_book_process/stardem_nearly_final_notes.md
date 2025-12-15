Nearly Final Beat Book
December 5, 2025

---

So sorry for turning this in so late! 100% had a brain fart and thought this was due on Saturday before I realized late Friday afternoon.

---

Fact-check Google Doc:
https://docs.google.com/document/d/1Ibiuy5mY0BCqD1UWPCPsuf-p5ZKFBgtulFX7MmsaCPY/edit?usp=sharing

To start this draft, I played around with a fact-checking system based on Claude's built-in web search capabilities. The way I created this was by replacing one of my previous intermediary "review" steps with a "fact-check" step, where every 10 batches Claude would search the web to fact-check all the info. in the beat book and suggest potential corrections in a separate file, called `education_beat_book_fact_check.md`.

Unfortunately, I chose to abort this beat book draft earlier than the previous two attempts because its "fact checks" were really not that useful or good. Many times Claude focused on semantic things that were overly specific, and it frequently seemed to "overthink" its suggestions. Like we discussed in class, the model is looking for *any* mistake it can possibly find, even when there are none, resulting in several false positives. I don't plan on using this feature for this purpose ever again because of this (and because the web search tool is so unpredictable).

I instead resulted to fact-checking my second iteration of my beat book, which I did on a Google Doc. To assist with fact-checking, I (Copilot) built a very basic archive browser web app, which allowed me to search for keywords across all 600+ education stories in our JSON data. The web app uses a URL system similar to Datasette, with queries stored in the URL so that you can copy/paste a specific search term inside a specific article. (I linked to several of these in my Google Doc comments.)

I resonated a lot with what Miles said in our last class, which is that you get to learn a lot about your beat book (and the models' habits) through this editing process. The model I used, GPT-OSS-120B, seemed overly eager to directly plagiarize from articles it read — there were several sentences in my beat book that were lifted word-for-word from their source articles. I only was able to catch onto this so quickly because of my archive viewer web app, so I wonder if others' beat books contain similar issues and we just haven't realized it yet. Either way, this is something I'd really like to fix for my final beat book, be it through prompting or some other method. One other idea I had (besides prompting) was to programmatically check the beat book for matching phrases to the JSON data, like a mini plagiarism checker. I care a lot about fixing this to avoid Claude (and other frontier models) from ever seeing more content that was directly lifted from Star-Democrat articles. (I wish had noticed this issue sooner, frankly.)

I also noticed similar errors to the ones Miles discussed in class. For some people mentioned in my beat book, such as CCPS' Amy Towers, the model got their titles and roles wrong despite knowing the organization they belonged to. In my specific case, this may be a fundamental problem with my chunk-based approach to generating a beat book. It's entirely possible the model correctly reported on someone's title from an older article, like it did in the case of Amy Towers, simply because it hadn't seen a more up-to-date article in the batches it was fed. I'm not entirely sure how to fix this right now (besides running through 100% of the stories), but I'll keep thinking about this before my last draft.

There was also one major error — the misstatement of Michele Wayman's last name, which the model said was "Weaver" — that was caused entirely by an error in the original source article, rather than the model. The original article contained this mistake without a correction, which was honestly not something I'd considered prior to this happening. I'm not sure what the solution to this problem is, especially since it's (hopefully) very rare. Still, using web search in Claude could maybe assist with this since it could venture beyond the immediate content. There were a few instances when fact-checking that I noticed details that were likely retrieved from Claude doing a web search, which actually worked fairly well from what I saw.

Interestingly, throughout my beat book I also noted a lack of spelling errors. I was expecting to see several mispellings of places like Easton (i.e. calling it "East Easton") or more people's names, but the model unexpectedly did okay here. I'm assuming this had a lot to do with the intermediary Claude "review" steps I added, which helped smooth out problems like these.

Overall, I was mostly impressed by the lack of errors that were made, and I have some confidence that I can improve the final beat book through prompting and adjustments to how I let the model source information from the articles (preventing it from directly plagiarizing).
