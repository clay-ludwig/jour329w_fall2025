CNS Collections - Education
October 15, 2025

---

I chose the topic "Education," which contains 346 stories.

Metadata for "Education":
- **people**: Array of key people mentioned (names only)
- **geographic_focus**: Primary location (county, city, region, or "statewide")
- **key_institutions**: Organizations, agencies, companies involved
- **story_category**: Whether the story is a feature, breaking news, etc.
    - Documenting this can help give a sense of what types of stories are generally required for the education beat.
- **follow_up_rating**: A rating from 1-10 of the necessity for a follow-up to this story (where 10 means very high potential for a good follow-up).
- **education_level**: Level(s) of education, written as an array (can include pre-k, k-12, higher-ed or general)
    - Documenting this can show which level(s) of education CNS is mostly focusing on for this beat.
- **schools_named**: List of schools that were named in the article (if any), formatted as an array
    - Helps track which schools are being most frequently covered (and just as importantly, which may not be covered enough).
- **topic_overlap**: A rating from 1-10 of the amount of overlap with other CNS topics (where 10 means heavy overlap with the given topic).
    - I'll give the AI model a list of the CNS topics we created (excluding education), and have it assign a value next to each one. This could be super useful in giving us a sense for where education stories closely tie into other beats/topics.

I used Claude to add the metadata, but used OpenAI's Prompt Optimizer to help me clean up the language in certain parts of my prompt: https://platform.openai.com/chat/edit?models=gpt-5&optimize=true

## Creating the Metadata

I ran this command to create the enhanced_beat_stories file:
```bash
uv run python add_metadata.py --model claude-3.5-haiku --input story_summaries_housing.json
```

It worked, though I think in my delirious state last night that I accidentally did CMD + Z after deleting those duplicate lines. It worked fine though after waiting!

## Exploring with Datasette

1. **Key Players**: Who appears most frequently?
These are the top 30 people:
Larry Hogan 9
Jordan McNair 8
DJ Durkin 5
Wallace Loh 4
Wes Moore 4
Betsy DeVos 3
Damon Evans 3
Governor Hogan 3
Jerry Zremski 3
Nelson Mandela 3
April Christina Curley 2
Barack Obama 2
Joe Biden 2
1776 Project PAC 1
A. James Clark 1
Abraham Lincoln 1
Adam Marton 1 (lol)
Adrianne Flynn 1
Alexis Capes 1
Alma Adams 1
Amy Dodson 1
Ann Brittingham Suthowski 1
Anthony Williams 1
Ashley Esposito 1
Ashley Kearney 1
Ben Cardin 1
Ben Kramer 1
Biden 1
Bob Cassilly 1
Branndon D. Jackson 1

2. **Geographic Patterns**: Which areas get the most coverage?
The data here is a little less clear, since the AI didn't do the best job here — we will ignore "Maryland" as the top geographic area. The true top areas seem to be:
- Baltimore city
- "Multiple regions" (which is also mostly useless)
- Montgomery County
- Anne Arundel County
- Baltimore County
- PG County
Etc.

The least covered area in this beat, it says, is Salisbury, Maryland.

3. **Institutional Network**: Which organizations appear in stories?
According to the data it provided, they are:
- School board
- University of Maryland
- Maryland General Assembly
- Maryland Public Schools
- Department of Ed
- Maryland State Department of Ed (good on Claude for separating federal and state there, though I worry slightly about reliability)
- Maryland school board (hmmmm)
- MCPS

These findings make rough sense I would say, despite sometimes imperfect data — for example, I'm not sure what the difference between "school board" and "Maryland school board" is. Still, the fact that this helped give me a more immediate sense of these facets, which each require a good level of semantic understanding to properly create data for, is really useful.

I'm a little unclear right now whether the AI model is running independently each time, like it did when we were playing with LLM in Datasette last week. If it is, it would explain the inconsistent formatting of some results like I just mentioned above. To fix this, we could either adjust our prompt to be very specific and strict about how to categorize and format certain things, or we could try to adjust the code that runs the LLM to give it some short-term memory so it could try to stay consistent.

## Prototype Beat Book
I ran:
```bash
cat prompt.txt enhanced_beat_stories.json | uv run llm -m claude-3.5-haiku > prototype.md
```

I also used Copilot to help me with this prompt - I am pasting the chat transcript at the bottom of this file.

## Reflection
The structured metadata surprisingly revealed a lot about this beat. It allowed me to get a wide (but not very deep) look at what different stories for the education beat involve at CNS. Through facets in Datasette, I was able to get an even clearer idea of what CNS' most and least covered topics are in the education beat.

As for the prototype beat book, I would consider it a failure. It seemed to focus too heavily on a very specific story about the "Blueprint for Maryland's Future." This is almost certainly because I had to cut so many other stories (and their summaries) from the enhanced_beat_stories JSON to properly fit the prompt + json data into Claude's context window limit. Many of the stories at the bottom of the resulting enhanced_beat_stories file were about the "Blueprint for Maryland's Future" topic, which probably made Claude focus too heavily on that. A more useful beat book, I believe, would still give more attention to frequently-covered stories and less to one-offs or otherwise unrelated ones. In this case, Claude definitely focused too heavily on one story.

Putting the obvious failure aside, as a whole, I did like how Claude decided to format the info. in its first draft. It wrote its beat book in markdown and formatted everything into different sections to be easier to skim — I really like this and would like to continue down this path for our real beat book (or at least not force a reporter to read a wall of text). That said, I really think a more interactive beat book would be ideal here, since shortened summaries of things often only create more questions.

I was very stretched for time for this assignment, but if I had more time I would spend more time experimenting with ways to give the LLM the entire context of the CNS education beat without sacrificing on details. One of my ideas was to break the JSON into slices that Claude could interpret and use, collectively, to form one cohesive beat book. I could imagine doing this through some combination of clever prompting and code written to help break the data into chunks and have the LLM process each chunk. One of the challenges with this idea would definitely be having Claude be aware of the info. from other chunks of the JSON — we don't want it to independently process each excerpt of data.

I also didn't have much time to adjust my prompt today — I really wanted to dig into that and spend more time tweaking different things. I relied on LLMs to form my prompt, and while I liked what I saw overall, I would definitely have spent more time tailoring it to this task.

## Copilot Transcript
clay-ludwig: Can you help create me a concise but detailed prompt for this? We are basically going to try to explain the ins and outs of a specific reporting beat given metadata from the enhanced_beat_stories file, like it says. We need to give the reporter covering this beat enough detail to know what is required of the beat, while being concise enough to not overwhelm the reporter.

GitHub Copilot: ````text
You are an expert news editor building a compact, actionable beat guide for a reporter. Use the JSON records in enhanced_beat_stories.json and the evaluation notes.md to produce a single Markdown guide that fits on roughly 2–4 pages but is rich with actionable detail.

Requirements:
- Start with a one-paragraph beat summary (1–3 sentences) that explains the beat's scope and why it matters.
- Provide a 3-line "daily checklist" of tasks the reporter should perform each workday.
- List 6–10 prioritized reporting priorities/themes (bulleted), with one sentence explaining why each matters and one data field or metadata facet to watch for (use metadata_people, metadata_geographic_focus, metadata_key_institutions, and any beat_specific_field present in the JSON).
- Provide a short source map: 8–12 named potential sources or institutions, each with a one-line description of their role and one practical tip on how to contact/monitor them (e.g., public calendar, FOIA office, social feed).
- Include 4 common story templates the reporter can use (headline + 2–3 bullet lede/angle ideas for each): e.g., watchdog/FOIA, service story, Q&A profile, explainers using data.
- Provide 5 focused interview questions tailored to the beat and 3 suggested data/records to request (with exact document names or search terms where possible).
- Offer a 30/60/90-day reporting plan with concrete milestones and suggested sample story ideas keyed to metadata signals.
- Add 5 short example search/analysis commands the reporter can run locally to reproduce common queries (use sqlite-utils, jq, or simple grep/jq patterns) referencing enhanced_beat_stories.json and the metadata_* fields.
- Include 3 representative story citations drawn from enhanced_beat_stories.json (title + link if available + one-sentence note on why it’s useful as a model).
- End with 3 quick tips for verification/ethics/legal issues specific to this beat.

Formatting and style:
- Output as Markdown with clear section headings and short bullet lists.
- Keep language concise and actionable; avoid long background essays.
- If a required metadata field is missing in the dataset, note that and suggest an alternate signal to use.
- Do not include raw JSON in the guide; reference fields by name only.

Produce the guide now.// filepath: /workspaces/jour329w_fall2025/assignments/cns_collections/prompt.txt
You are an expert news editor building a compact, actionable beat guide for a reporter. Use the JSON records in enhanced_beat_stories.json and the evaluation notes.md to produce a single Markdown guide that fits on roughly 2–4 pages but is rich with actionable detail.

Requirements:
- Start with a one-paragraph beat summary (1–3 sentences) that explains the beat's scope and why it matters.
- Provide a 3-line "daily checklist" of tasks the reporter should perform each workday.
- List 6–10 prioritized reporting priorities/themes (bulleted), with one sentence explaining why each matters and one data field or metadata facet to watch for (use metadata_people, metadata_geographic_focus, metadata_key_institutions, and any beat_specific_field present in the JSON).
- Provide a short source map: 8–12 named potential sources or institutions, each with a one-line description of their role and one practical tip on how to contact/monitor them (e.g., public calendar, FOIA office, social feed).
- Include 4 common story templates the reporter can use (headline + 2–3 bullet lede/angle ideas for each): e.g., watchdog/FOIA, service story, Q&A profile, explainers using data.
- Provide 5 focused interview questions tailored to the beat and 3 suggested data/records to request (with exact document names or search terms where possible).
- Offer a 30/60/90-day reporting plan with concrete milestones and suggested sample story ideas keyed to metadata signals.
- Add 5 short example search/analysis commands the reporter can run locally to reproduce common queries (use sqlite-utils, jq, or simple grep/jq patterns) referencing enhanced_beat_stories.json and the metadata_* fields.
- Include 3 representative story citations drawn from enhanced_beat_stories.json (title + link if available + one-sentence note on why it’s useful as a model).
- End with 3 quick tips for verification/ethics/legal issues specific to this beat.

Formatting and style:
- Output as Markdown with clear section headings and short bullet lists.
- Keep language concise and actionable; avoid long background essays.
- If a required metadata field is missing in the dataset, note that and suggest an alternate signal to use.
- Do not include raw JSON in the guide; reference fields by name only.

Produce the guide now.