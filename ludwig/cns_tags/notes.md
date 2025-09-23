CNS Tags
September 22, 2025


## Tag Exploration

The tags.json file contains all of the tags used on the CNS site, and includes data like the number of uses and URL slug for each tag.

The most used tag appears to be "Politics," which was counted 1,172 times. To find this, I ran the command given in class:

**Command:**
```{bash}
uv run sqlite-utils memory data/tags.json "select name, count from tags order by count desc limit 20"
```

**Output:**
```
[{"name": "Politics", "count": 1172},
 {"name": "maryland", "count": 1127},
 {"name": "CNS TV", "count": 804},
 {"name": "Capital News Service", "count": 756},
 {"name": "hero", "count": 728},
 {"name": "cns", "count": 591},
 {"name": "Sports", "count": 494},
 {"name": "cnstv", "count": 375},
 {"name": "Baltimore", "count": 371},
 {"name": "Donald Trump", "count": 333},
 {"name": "annapolis", "count": 329},
 {"name": "Maryland Capital News Service", "count": 327},
 {"name": "Baltimore", "count": 314},
 {"name": "cns maryland", "count": 234},
 {"name": "Larry Hogan", "count": 199},
 {"name": "Chris Van Hollen", "count": 193},
 {"name": "education", "count": 183},
 {"name": "Ben Cardin", "count": 182},
 {"name": "Maryland Newsline", "count": 179},
 {"name": "Congress", "count": 172}]
```

**Evaluation:**
This command, from my understanding, places the data from tags.json into a temporary SQLite database so that it can be counted/ordered based on certain criteria (in this case, tag count in descending order).

This is super useful, and I like how it returned the output as an array of JSON, since it's readable to humans, computers and LLMs. We could easily pass arrays like this to an LLM to do further analysis on it (maybe having it return its own JSON as well), and for us humans it's glanceable enough that I can immediately tell what the highest-counted tags are on CNS. If we wanted to convert this JSON into some kind of more structured file, like a CSV, we could also write code that iterates through it and pipes it into a CSV. Because it's so versatile, I'm sure this type of command is used frequently.

## CNS Story

I chose this story to read for the tag "Chris Van Hollen":
Returning from El Salvador, Van Hollen says ‘we need to bring Mr. Abrego García home’ (https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/)

**Command:**
```{bash}
uv run python -m newspaper --url="https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/" -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "You are an expert at categorizing topics for news stories. Read the text and provide no more than 5 topics."
```

**Output:**
```
1. Kilmar Abrego García deportation & detention  
2. Senator Van Hollen’s El Salvador fact-finding trip  
3. Trump administration vs. courts on deportee return order  
4. U.S.–El Salvador prison deal & $15 million payments  
5. Constitutional & international human-rights issues
```

**Evaluation:**
While the topics it chose here are appropriate given the article, they are not within two words and could not work as tags on the CNS website. Because of this, I need to adjust the prompt to try to force the LLM to only return minimal tags.

## Tagging (Attempt 2)
**Command:**
```{bash}
uv run python -m newspaper --url="https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/" -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "You are an expert at categorizing topics for news stories and deciding on keyword-based tags. Read the text and provide no more than 5 tags. Ensure tags are short—one, maybe two words at most."
```

**Output:**
```
Van-Hollen  
Abrego-García  
deportation  
CECOT  
due-process
```

**Evaluation:**
This is a much better response from the LLM, but there are still several things wrong. For one, the formatting of its tags is awkward—ideally we would have no dashes separating words (instead we should just use spaces). I do like how it capitalized proper nouns, so I'll aim to keep that behavior, however the proper nouns it included are abbreviated versions of the original names. I'm assuming my rules that establish a maximum of two words were overly strict, so I'll need to make a carve out for proper nouns. For the next prompt, I'll write much stricter guidelines for how to decide on tag names, with the goal of getting a list that looks something like this:
- Chris Van Hollen
- Kilmar Abrego Garcia
- deportation
- CECOT
- Due process

## Attempt 3
**Command:**
```{bash}
uv run python -m newspaper --url="https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/" -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "You are an SEO expert in charge of assigning keyword-based tags for news stories. After reading the provided article, create no more than 5 tags. Each tag must be concise—one or two words only, but preferring full names for proper nouns. Separate words in tags with spaces only, and avoid using dashes, underscores, etc. Ensure the tags are unique to the article and do not repeat. Tags must be specific and meaningful, and reflect the search terms likely used for other similar stories."
```

**Output:**
```
Abrego García
Van Hollen
CECOT
El Salvador deportation
constitutional rights
```

**Evaluation:**
I tried something new with this prompt, which was to give it a "role play" scenario in which it acts as an "SEO expert." I recently tried this technique with a personal project and actually received better outputs from it, so I figured I would try it here. As you can see, though, it didn't really work... at all!

If I had to guess, the reason why it worked better for my personal project was because I was using a more advanced model. My understanding (which could be very flawed) is that smaller/dumber models need more specific and narrow instructions than larger models (especially larger models with reasoning), so I will try to make my instructions even clearer.

This may just be a quirk I have, but I sometimes have a temptation to make AI prompts that are too specific to the current task at hand. In this case, I so badly want to write an example in its instructions, like this:
```
"For example, instead of writing 'Van Hollen,' prefer writing his full name, 'Chris Van Hollen'"
```
If I do this, though, the model will almost certainly perform better at creating tags for this specific article, but may fail to pick up on the pattern I'm trying to establish more broadly. It's better to be clear about the intended pattern without using a specific example, I think, so it can properly categorize articles about a wide range of topics.

## Attempt 4
**Command:**
```{bash}
uv run python -m newspaper --url="https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/" -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "You are an SEO expert in charge of assigning keyword-based tags for news stories. After reading the provided article, create no more than 5 tags. Each tag must be concise. Prefer using one or two words per keyword, UNLESS the keyword is for a name or proper noun—in that case, use the full, unabbreviated proper noun. Prefer separating words in tags with spaces only, and avoid using dashes, underscores, etc. as separators. Ensure your tags are unique to the article and do not repeat themselves. Tags must be specific and meaningful, and reflect the search terms likely used to find this story."
```

**Output:**
```
Kilmar Abrego García  
Chris Van Hollen  
CECOT El Salvador  
deportation due process  
Trump administration
```

**Evaluation:**
This output is better, but now there are weirdly more than 5 tags. I'm going to make my prompt more clearly outline the need for 5 tags, asking it to number each one. I also am going to try changing the formatting to be more markdown-y, since LLMs usually have an easy time understanding markdown and my prompt is a little long.

## Attempt 5
**Command:**
```{bash}
uv run python -m newspaper --url="https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/" -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "You are an SEO expert in charge of assigning keyword-based tags for news stories. After reading the provided article, create exactly 5 tags in a numbered list.

## Guidelines for Tags:
- Each tag tag must be concise—prefer using one or two words per tag, UNLESS the tag will be of a name or proper noun—in that case, use the full, unabbreviated proper noun.
- Prefer separating words in tags with spaces—avoid using dashes, underscores, etc. as separators.
- Ensure your tags are unique to the article and do not repeat themselves.
- Tags must be specific and meaningful, and reflect the search terms likely used to find this story."
```

**Output:**
```
1. Kilmar Abrego García
2. CECOT
3. Chris Van Hollen
4. El Salvador deportation
5. due process
```

**Evaluation:**
Grrr, this one was so close. But "El Salvador deportation" is three words, and we are trying to limit ours to two. I think what happened here is that the model saw a proper noun, read my rules that allow more than two words for proper noun-related tags, and assumed it could append things onto "El Salvador".

## Attempt 6
**Command:**
```{bash}
uv run python -m newspaper --url="https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/" -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "You are an SEO expert in charge of assigning keyword-based tags for news stories. After reading the provided article, create exactly 5 tags in a numbered list.

## Guidelines for Tags:
- Each tag tag must be concise—prefer using one or two words per tag, UNLESS the tag will be of a name or proper noun—in that case, use the full, unabbreviated proper noun.
- For tags containing proper nouns, do not include or append other words or phrases to the tag. Solely include the unabbreviated proper noun.
- Prefer separating words in tags with spaces—avoid using dashes, underscores, etc. as separators.
- Ensure your tags are unique to the article and do not repeat themselves.
- Tags must be specific and meaningful, and reflect the search terms likely used to find this story."
```

**Output:**
```
1. Kilmar Abrego García  
2. Chris Van Hollen  
3. CECOT prison  
4. El Salvador deportation  
5. due process
```

**Evaluation:**
Same problem as last time, so I'm going to adjust the prompt again to be even clearer with a section specifically for proper nouns.

## Attempt 7
**Command:**
```{bash}
uv run python -m newspaper --url="https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/" -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "You are an SEO expert in charge of assigning keyword-based tags for news stories. After reading the provided article, create exactly 5 tags in a numbered list.

## Guidelines for Tags:
- If the tag will contain a proper noun of a person or place, follow the guidelines below for proper noun tags.
- Each tag tag must be concise—prefer using one word per tag, or if you must, a maximum of TWO.
- Prefer separating words in tags with spaces—avoid using dashes, underscores, etc. as separators.
- Ensure your tags are unique to the article and correspond to a single concept or topic within the article—do not combine topics into one tag (prefer another tag, if possible).
- Tags must be specific and meaningful, and reflect the search terms likely used to find this story.

## Guidelines for Proper Noun Tags:
- Always use the full, unabbreviated proper noun for people and places.
- Do not couple proper nouns of people or places with any additional words under any circumstances. Prefer tags containing proper nouns to solely contain those proper nouns.
- Do not combine multiple proper nouns in a single tag."
```

**Output:**
```
1. Kilmar Abrego García  
2. Chris Van Hollen  
3. El Salvador  
4. CECOT  
5. deportation
```

**Evaluation:**
🥳 I had no idea you could put emojis in VS code—wild!

Anyways, it worked! I broke off proper noun rules into their own section, since there became enough rules to warrant one. I also subtly improved the wording for some parts of the prompt, like clarifying that tags should each only encompass one topic within the article. These changes seemed to work and I'm happy with the tags it provided.

Just to be safe, I also tried the prompt with this article: https://cnsmaryland.org/2024/02/08/the-law-is-clear-crowd-urges-supreme-court-to-rule-against-trump-in-ballot-case/, and its output was the following:
```
1. Supreme Court  
2. Donald Trump  
3. 14th Amendment  
4. Colorado ballot  
5. insurrection
```

Another totally acceptable response, in my opinion.

## Conclusions
This admittedly took more work than I expected. The immediate takeaway is that prompt engineering takes multiple attempts, and you need to—at least partially— understand how LLMs work to properly iterate. For example, I subtly tweaked my final prompt to specify exactly what I meant by "proper nouns." To do this, I included the phrase "people and places," since I was beginning to suspect the LLM may not actually *know* what I intended when using the phrase "proper noun." Properly evaluating details like these for potentially confusing instructions is important because it can save a lot of repetitive calls (and therefore time and money).

I also believe the formatting of prompts really matters. Writing the prompts in markdown seemed to immediately improve the model's ability to follow instructions. It also has the added benefits of being prettier to human eyes, and presumably the ability to pipe in a .md file into the model as its prompt, rather than writing it entirely in the command itself.

This was definitely a challenge—one of the ideas I had for speeding this process up was giving *another* LLM the first model's output, and having the second model compare the first's outputted tags with the guidelines I wrote—essentially acting as a "check" on the first model's response that would catch errors. I'd imagine this approach would only make sense, though, if we were optimizing for high accuracy and didn't mind waiting longer and spending more (probably double) the money on each response. For this assignment, it seemed like fixing the original prompt was a smarter use of time.

Another idea I had was to write multiple prompts for each iteration, rather than just one. When adjusting my prompt, I had many ideas for directions I could go in to find the "perfect prompt," and I wished I could run the same LLM several times with each of those ideas to find which ideas it responded to better and how certain differences between prompts shaped its outputs.