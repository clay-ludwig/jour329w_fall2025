Star-Democrat Topic Classification
November, 2025

---

I chose option 1 (LLM generates topics).

## Generated Topics (created by LLM)
Local Government: 36 stories
Sports: 29 stories
History: 19 stories
Crime: 13 stories
Education: 12 stories
Business: 12 stories
Entertainment: 10 stories
Community Events: 10 stories
Politics: 8 stories
Religion: 6 stories
Local News: 6 stories
Community: 5 stories
Food: 5 stories
Environment: 4 stories
Obituaries: 3 stories
Opinion/Editorial: 3 stories
Health: 2 stories
Lifestyle: 2 stories
Arts: 2 stories
Government: 2 stories
Transportation: 1 stories
Crime/Accident: 1 stories
Energy: 1 stories
Social Issues: 1 stories
Veterans/Military: 1 stories
Obituary: 1 stories
Health Care: 1 stories
State Government: 1 stories
Agriculture: 1 stories
Real Estate: 1 stories
Arts & Entertainment: 1 stories

## Results Analysis
The LLM did an *okay* job generating topics given this sample. Many of the topics feel appropriate given the Star-Democrat's coverage — and the concentration of stories mainly in the local government/sports/history/crime/education topics makes sense too. I also like how the model created dedicated "religion" and "obituary" categories, since they can house the non-article content like we discussed last class.

There is definitely room for improvement though. The model didn't create descriptive-enough  categories for other types of non-articles published in the Star-Democrat (mainly advertisements, op-eds, or letters). For example, its "lifestyle" category contains two advice column stories — I think a better name would've simply been "advice" for these or even fallen into an "other" category (in fact, I think an "other" category is the fastest way to clean this list up). If we add an "other" category, I would likely change the categorization model's prompt to place most non-news content into this other category (perhaps with an exception for obituaries since there will be so many published in a local paper like the Star-Democrat).

Also, the LLM generated 11 topics with only one story in them, which suggests they may be too narrow and could be consolidated. The "health care" topic, for example, can be merged with "health" since there's not enough stories to warrant keeping them separated from each other. On the other hand, I don't see an issue right now with categories being too broad — though I wonder if my opinion on this would change if I saw all of the Star-Democrat's stories get categorized.

As for this approach, I tend to like when an LLM can do work for me! But honestly I think option 2 may have worked better since I could've used the embeddings clusters to inform my list of topics. Since I'm able to visually see the topics the Star-Democrat writes about in the embedding atlas you provided, I'm fairly confident the quality of my topics list could've been higher. The main appeal to option 1, of course, is the time it saves you (though then you have to check the LLM's work).

## GitHub Copilot Conversation
clay-ludwig: Can you follow the instructions inside the stardem_topics.md file about the classify_topics.py file? Please go with option 1 and edit the classify_topics.py file I've created already

GitHub Copilot: I'll help you edit the `classify_topics.py` file following Option 1 (Let the LLM Decide) from the instructions. Let me first read the current file to see what you have. 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_topics/classify_topics.py)

Great! I'll create a complete Python script that implements Option 1. This script will:
1. Read the Star-Democrat JSON file
2. Use the LLM to analyze each story and assign a topic
3. Save results to `stardem_topics_classified.json`
4. Show progress as it processes 

Using "Replace String in File"


```

```
Perfect! I've created a complete Python script for Option 1 that:

## What the script does:

1. **Reads the JSON file**: Loads `stardem_sample.json` from the current directory
2. **Classifies each story**: Uses the LLM to analyze the title and content, assigning a single topic
3. **Uses consistent prompting**: The prompt asks the LLM to create 1-2 word topics and maintain consistency across stories
4. **Shows progress**: Prints each story title and assigned topic as it processes
5. **Saves results**: Writes all classified stories to `stardem_topics_classified.json`
6. **Provides a summary**: Shows a count of stories per topic at the end

## Key features:

- **Model**: Uses `groq/meta-llama/llama-4-scout-17b-16e-instruct` by default (you can change this in the function call)
- **Error handling**: Catches subprocess errors and assigns "Unknown" if classification fails
- **Progress tracking**: Shows which story is being processed (e.g., "Processing story 15/200")
- **Topic summary**: Displays a sorted list of topics and their counts when complete

## To run the script:

Make sure you're in the stardem_topics directory and have the `stardem_sample.json` file there, then run:

```bash
uv run python classify_topics.py
```

The script will process all 200 stories and save the results. It might take a few minutes depending on the LLM response times!

Made changes.

clay-ludwig: Can you modify it to output _v{number} after each run? That way it doesn't override the file and write to it every time

GitHub Copilot: I'll modify the script to automatically version the output files so each run creates a new file instead of overwriting the previous one. 

Using "Replace String in File"


```

```
Perfect! Now the script will:

1. **Check for existing versions**: Looks for any files matching `stardem_topics_classified_v*.json`
2. **Find the highest version number**: Extracts version numbers from existing files
3. **Create the next version**: Automatically uses v1, v2, v3, etc.
4. **Show the output filename**: Prints which file it will save to at the start

So each run will create:
- First run: `stardem_topics_classified_v1.json`
- Second run: `stardem_topics_classified_v2.json`
- Third run: `stardem_topics_classified_v3.json`
- And so on...

This way you can compare different runs and won't lose any previous classification attempts!

Made changes.

clay-ludwig: Can you also modify the prompt so that it tries to consolidate topics instead of creating so many different ones? It seems to create a lot of 1-story topics like "Harriet Tubman" and "baseball" (when they should instead be categorized into things like "history" or "sports"). Try to tweak the language of the prompt to avoid this behavior

GitHub Copilot: I'll modify the prompt to encourage broader, more consolidated topic categories instead of hyper-specific ones. 

Using "Replace String in File"


```

```
Perfect! I've updated the prompt to:

1. **Emphasize "BROAD topic category"** in all caps to stress this requirement
2. **Provide specific examples** of what NOT to do (e.g., "Baseball" → "Sports", "Harriet Tubman" → "History")
3. **Give clear guidance** on thinking about general categories vs. specific subjects
4. **Add the newspaper section analogy** - asking the LLM to think about which section of a newspaper this would appear in (Sports, Business, Local News, etc.)
5. **Reinforce consistency** - reminding it to reuse topic names across similar stories

This should result in fewer, more consolidated topics like:
- **Sports** (instead of Baseball, Lacrosse, Football, etc.)
- **History** (instead of Harriet Tubman, Civil War, etc.)
- **Education** (instead of specific school names)
- **Local Government** (instead of specific officials)
- **Crime** or **Public Safety**
- **Business** or **Economy**

Try running it again and you should see much better topic consolidation!

Made changes.