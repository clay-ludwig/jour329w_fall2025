Star-Dem Entities
November 8, 2025

---

*I used the groq/openai/gpt-oss-120b model for this assignment.*

## Evaluation
After several iterations of both the add_entities.py script and its prompt, I was able to get results that I'm mostly satisfied with. I used the same model throughout the process (groq/openai/gpt-oss-120b), since I really wanted to understand the effects of changing the prompt.

I started with an initial prompt similar to the one in the classify_topics.py script, where the AI model was loosely asked to record the people, places and organizations inside stories published in the Star-Democrat. In my first attempt, I asked Copilot to adjust the classify_topics script and replace language about assigning "topics" with assigning "entities" in the prompt. The first iteration had several issues though, including the model recording the publishers, authors and photographers associated with *producing* the articles, rather than the subjects of the articles themselves. It also was wildly inconsistent with the conventions it used to list the names of various entities — sometimes both the city and state (i.e. "Easton, MD") would be recorded, for example, while other times it would list only the city or state (i.e. "Easton"). It also abbreviated things inconsistently (sometimes saying "MD" and other times "Maryland").

After reviewing these issues, I asked Copilot to make changes to the script addressing some of them. I got slightly more forceful with the formatting, asking Copilot to update the prompt to specifically make the LLM list names in the format "First (Middle) Last, Title." I also asked the model to exclude the news organizations and people responsible for producing the article and to focus on the subjects of articles instead. The resulting JSON from these changes was slightly better (more consistent and descriptive), but it still wasn't perfect — sometimes the model chose to omit people's titles completely, and the formatting was still inconsistent across the names of places and organizations (still using inconsistent abbreviations, for example).

For the third iteration, I asked Copilot to address these remaining issues. By this point, the model's prompt had become somewhat lengthy (in a good way). Copilot even included several examples of high quality outputs for it to follow, which seemed to help improve its consistency. It seemed to do a better job in the third iteration, but there were still minor issues. While some people's titles were technically correct, they often lacked context (i.e. "town manager" instead of "Oxford town manager"). I also noticed that we were spending a lot of tokens on non-article content, such as calendars and "today in history" pieces. Because of this, I asked Copilot to programatically exclude certain stories that included certain keywords or phrases in their 'title' or 'content' values. Specifically, I told it to exclude stories that:
- Contain "TODAY IN HISTORY" in the title
- Contain "RELIGION CALENDAR" in the title
- Contain "Mid-Shore Calendar" in the title
- Contain "Section: Calendar" in the content
- Contain "Section: Columns" in the content
- Contain "Section: Letters" in the content
*(In retrospect, I also should've asked it to exclude TV listings.)*

Adjusting things programatically like this, rather than asking the model to make a judgement call, felt like the right approach in this case since the Star-Democrat content follows a somewhat rigid structure in where/how it labels its pieces. It's possible — but highly unlikely — that a normal story's content would contain the phrase "Section: Calendar," for example. Because of this, a programmatic/deterministic filtering system applied *before* the model reviewed the stories felt like an appropriate approach. This filtering system helped lower the number of stories passed to the model from 200 to 165 — though it's also worth noting that in every iteration, there were around 20-30 stories that couldn't be categorized due to Groq API limit errors.

After I asked Copilot to make these last changes, the resulting JSON was much higher quality. I explored the "v4" version in Datasette to ensure its responses were accurate and descriptive, and in most cases they are. One error I noticed was that it incorrectly assigned Donald Trump's title in one federal story "Former President of the United States" (and Joe Biden's "President of the United States"), likely because its training data cut off is some time before 2025. This hit on a worry I had with this method, which was that the model may sometimes rely more on its training data than what was written in the article's content. That particular federal story was published in 2023, so the author had actually written "former president," but I can see this being a problem. You could argue that including "former" was technically accurate in that case, but it could create confusion over time if we label people and entities differently based on time-sensitive language. We could maybe ask the model to exclude time-based language in titles, removing words like "former" — but I could see this being imperfect too.

Despite these small issues, this last iteration felt more consistent, descriptive and accurate to the stories they were derived from. Overall I think it did a pretty good job even if it took some trial and error.

## Copilot Transcript
clay-ludwig: Hello! I'd like to follow exactly what this part of the instructions document is saying here: we should modify the add_entities.py file in our stardem_entities directory by changing its prompt and maybe some of its architecture to make the models extract people, places and organizations into arrays. Please go ahead with this change and modify the script.

GitHub Copilot: I'll help you modify the `add_entities.py` file to extract people, places, and organizations into arrays. Let me first check the current state of the file to understand its structure. 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_entities/add_entities.py#1-1), lines 1 to 150

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_entities/add_entities.py#150-150), lines 150 to 163

Now I'll modify the add_entities.py script to focus on extracting people, places, and organizations into arrays. I'll simplify the schema and update the prompt to be specific to entity extraction: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Now let me verify the changes by reading the modified file: 

Checked [](file:///workspaces/jour329w_fall2025/ludwig/stardem_entities/add_entities.py), no problems found

Perfect! Let me show you a summary of what I've done: 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_entities/add_entities.py)

Perfect! I've successfully modified the add_entities.py script in your `stardem_entities` directory. Here's what I changed:

## Key Modifications:

1. **Renamed the function**: Changed `extract_metadata()` to `extract_entities()` to better reflect its purpose

2. **Simplified the prompt**: 
   - Removed the complex schema with education-specific metadata and topic overlap ratings
   - Focused on extracting just three entity types: **people**, **places**, and **organizations**
   - Added a clear example output to guide the LLM

3. **Updated the output structure**:
   - Stories now get three simple array fields: `people`, `places`, and `organizations`
   - Each field contains an array of extracted entities
   - If extraction fails, empty arrays are added instead

4. **Changed default input file**: Updated from `story_summaries_elections.json` to `stardem_sample.json`

5. **Changed output file**: Now saves to `stories_with_entities.json` instead of `enhanced_beat_stories.json`

6. **Updated descriptions**: Made them specific to Star-Democrat entity extraction

The script is now ready to use! You can run it with:

```bash
uv run python add_entities.py --model groq/openai/gpt-oss-120b --input stardem_sample.json
```

The simplified prompt with the example should help the LLM extract entities more accurately and consistently.

Made changes.

clay-ludwig: Nice job, I just tested it. Can you please make the script outut the suffix "_v{number}" after each file so that I can generate multiple versions?

GitHub Copilot: I'll modify the script to add a version number argument so you can generate multiple versions of the output file. Let me update it: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Perfect! I've updated the script to support versioning. Now you can use it like this:

```bash
# First version (default)
uv run python add_entities.py --model groq/openai/gpt-oss-120b --input stardem_sample.json

# Or explicitly specify version 1
uv run python add_entities.py --model groq/openai/gpt-oss-120b --input stardem_sample.json --version 1

# Second version with a different model
uv run python add_entities.py --model groq/meta-llama/llama-4-maverick-17b-128e-instruct --input stardem_sample.json --version 2

# Third version with different prompt tweaks
uv run python add_entities.py --model groq/openai/gpt-oss-20b --input stardem_sample.json --version 3
```

The output files will be named:
- `stories_with_entities_v1.json`
- `stories_with_entities_v2.json`
- `stories_with_entities_v3.json`
- etc.

This way you can easily compare results from different models or prompt variations!

Made changes.

clay-ludwig: I'd also like to adjust the prompt in our script to specifically ask the model to list people's name and title in the format First (Middle) Last, Title if possible. Also give it some explicit rules, like not listing APGMedia or Star-Democrat as an organization (we are strictly listing people/organizations who are featured as news *in* an article — not those producing the article content).

GitHub Copilot: I'll update the prompt in the script to include those specifications about name formatting and explicit rules about what to exclude: 

Using "Replace String in File"


```

```
Perfect! I've updated the prompt with:

1. **Name formatting instructions**: Now asks the model to format people as "First (Middle) Last, Title" when possible (e.g., "John A. Smith, Mayor")

2. **Explicit exclusion rules**:
   - Don't include news organizations like Star-Democrat or APGMedia
   - Don't include reporters, photographers, or byline authors
   - Only extract entities that are subjects OF the news story, not those producing it

3. **Updated example** to show the proper name/title format

This should give you much cleaner entity extraction focused on the actual news subjects rather than the publication metadata!

Made changes.

clay-ludwig: Just tested this change - it is ocassionally not listing a title next to people so can you make the prompt a little more forceful about that? Also we should make sure we keep formatting consistent for each type of data (people, places, orgs).

GitHub Copilot: I'll make the prompt more forceful about including titles and add consistency requirements for formatting: 

Using "Replace String in File"


```

```
Perfect! I've updated the prompt to be much more forceful and explicit:

**Key changes:**

1. **Stronger title requirement**: Changed from "when possible" to "You MUST include a title/role for each person" and "Never list a name without a title"

2. **Fallback guidance**: If exact title isn't stated, the model should infer their role from context (e.g., "resident", "spokesperson", "witness", "official")

3. **Consistency requirements** for each category:
   - **People**: ALWAYS use "Name, Title" format
   - **Places**: Use full official names consistently
   - **Organizations**: Use full official names (not abbreviations)

4. **Updated example**: Added "Tom Brown, resident" to show that even without an official title, a role/descriptor should be included

5. **Emphasized consistency**: Added "Maintain consistent formatting within each category" to the rules

This should give you much more consistent results with titles always included for people!

Made changes.

clay-ludwig: Also the script doesn't seem to be properly saving to a new number (i.e. v1, v2, v3). It needs to check the current files before naming its file.

GitHub Copilot: I'll update the script to automatically detect the next available version number by checking existing files: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Perfect! I've updated the script to automatically detect and increment version numbers. Here's what changed:

**Key improvements:**

1. **Auto-increment by default**: If you don't specify `--version`, it will automatically find the highest existing version number and increment it
   - First run: creates `stories_with_entities_v1.json`
   - Second run: creates `stories_with_entities_v2.json`
   - Third run: creates `stories_with_entities_v3.json`
   - etc.

2. **Manual override still available**: You can still specify `--version 5` if you want to create a specific version

3. **Feedback**: The script now prints which version number it's using

**Usage examples:**

```bash
# Auto-increment (recommended)
uv run python add_entities.py --model groq/openai/gpt-oss-120b --input stardem_sample.json

# Force a specific version
uv run python add_entities.py --model groq/openai/gpt-oss-120b --input stardem_sample.json --version 10
```

Now each time you run the script without specifying a version, it will automatically create the next numbered file!

Made changes.

clay-ludwig: There are also several instances, after testing, where there are no listed people, places or organizations. Please try to fix this - I'm not fully sure what the problem may be

GitHub Copilot: Let me first check one of the output files to see what's happening with the empty results: 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_entities/stories_with_entities_v1.json#1-1), lines 1 to 100

I can see the issue! There are several problems:

1. **Timeout errors**: The LLM is timing out (30 seconds) when processing longer content
2. **"LLM failed" errors**: The subprocess is failing for some reason
3. The content being sent is the **full article content**, not the summary

Let me check if there's a summary field available: 

Searched text for `summary` (`**/ludwig/stardem_entities/stardem_sample.json`), no results

The problem is clear: the script is sending the entire article content (which can be very long) instead of a summary, causing timeouts. Let me fix this by:

1. Increasing the timeout
2. Truncating the content to a reasonable length
3. Adding better error handling and retry logic 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Now let me also add some diagnostic output and make the processing more robust: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Perfect! I've made several important improvements to fix the empty entity issue:

## Key Changes:

1. **Content Truncation**: The script now truncates long articles to the first 2000 characters (~400-500 words). This prevents timeouts while keeping the most important content where entities are usually mentioned.

2. **Increased Timeout**: Raised from 30 to 60 seconds to handle longer processing times.

3. **Better Error Handling**: 
   - Separate handling for timeouts, JSON parsing errors, and other failures
   - More detailed error messages to diagnose issues

4. **Enhanced Logging**: 
   - Shows progress with ✓ and ✗ symbols
   - Displays count of entities found for each story
   - Summary at the end showing success rate and error details

5. **Empty Content Check**: Warns if a story has no content available

The main issue was that the full article content (sometimes 1000+ words) was being sent to the LLM, causing timeouts. By truncating to the first 2000 characters, we get the most important part (headline, lead, first paragraphs) where entities are typically concentrated, while avoiding timeouts.

Try running it again and you should see much better results with fewer empty entity lists!

Made changes.

clay-ludwig: I'm seeing this in the console: Processing 1/200: Townsend, Orrell lead Warriors...
  ✓ Found 3 people, 6 places, 5 orgs
Processing 2/200: Easton man pleads guilty to possessing child pornography...
  ✗ Error: LLM failed
Processing 3/200: GREENSBORO CANDIDATE: Paula Turner...
  ✗ Error: LLM failed
Processing 4/200: Men For Change recognizes volunteers' service...
  ✗ Error: LLM failed
Processing 5/200: TODAY IN HISTORY/March 24...
  ✗ Error: LLM failed
^CTraceback (most recent call last). Can you list the error?

GitHub Copilot: Let me check what the actual LLM error is by looking at the stderr output. I'll modify the script to print the full error details: 

Using "Replace String in File"


```

```
Now run the script again and you'll see the detailed error messages. This will help us understand what's causing the "LLM failed" errors. The script will now show:
- The error message
- The stderr output from the LLM command
- The return code

Try running it again:

```bash
uv run python add_entities.py --model groq/openai/gpt-oss-120b --input stardem_sample.json
```

And let me know what the stderr and return code say. This will help me diagnose whether it's an API quota issue, model availability issue, or something else.

Made changes.

clay-ludwig: Can you adjust the script to automatically first filter out any of the following stories: 1) Titles that contain the string "TODAY IN HISTORY", 2) titles that contain "RELIGION CALENDAR", 3) titles that contain "Mid-Shore Calendar", 4) content that contains the string "Section: Calendar" or "Section: Columns" or "Section: Letters". Can you also adjust the prompt to write people's titles in a way that people who have never read the article would understand? I.e. sometimes right now I see it write things like First Last, Town Manager which isn't very descriptive - it should say which town in that case, for example. Also please make sure the places list the city and state.

GitHub Copilot: I'll modify the script to filter out those story types and improve the prompt for better entity descriptions: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Perfect! I've made the following changes to the script:

## 1. **Automatic Filtering**
The script now filters out:
- Stories with "TODAY IN HISTORY" in the title
- Stories with "RELIGION CALENDAR" in the title  
- Stories with "MID-SHORE CALENDAR" in the title
- Stories with "Section: Calendar", "Section: Columns", or "Section: Letters" in the content

It will show you how many stories were filtered and which ones (if 10 or fewer).

## 2. **Improved Entity Descriptions**

**People**: Now requires DESCRIPTIVE and SPECIFIC titles with organizational/geographic context:
- ✓ "John Smith, Mayor of Easton" 
- ✓ "Mary Johnson, Talbot County Police Chief"
- ✓ "Dr. Williams, Superintendent of Caroline County Public Schools"
- ✗ "John Smith, Mayor" (too vague)
- ✗ "Mary Johnson, Town Manager" (which town?)

**Places**: Now requires city AND state when applicable:
- ✓ "Easton, Maryland"
- ✓ "Talbot County, Maryland"
- ✓ "Washington D.C."
- ✗ "Easton" (missing state)

**Organizations**: Now includes geographic context when helpful:
- ✓ "Easton Police Department"
- ✗ "Police Department" (which one?)

The prompt now explicitly tells the LLM to provide context that would help someone who has never read the article understand who/what/where these entities are!

Made changes.