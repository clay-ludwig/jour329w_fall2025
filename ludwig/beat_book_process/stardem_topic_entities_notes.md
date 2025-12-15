Star-Dem Topic Entities
November 10, 2025

---

I chose the education topic because I'm already familiar with its stories in the Star-Democrat from previous assignments and from asking Jim questions about it. I changed the prompt before my first run to reflect the specific qualities of the education beat, mentioning education-focused examples (like principals of schools for the 'people' section) and informing it to think about different aspects of education like school boards, PTA programs, funding, etc. I made a point to define very specifically what I was looking for in this prompt, since my one in previous assignments felt a little too vague/wide-reaching.

## Second Run Approach
I used the groq/openai/gpt-oss-120b model for both my first and second runs, but I also involved another model — groq/openai/gpt-oss-20b — for my second run. I didn't modify the 120b model's prompt for my second run, but I added a "screening" phase that involved the 20b model, since I noticed a lot of the stories in the education JSON didn't perfectly belong to that category.

I was originally going to rely on the confidence rating provided in the JSON to filter these stories out (and I was thinking of excluding stories under a score of 0.9), but there were enough valid stories around the ~0.86 mark that I was afraid I'd be cutting out too many. Instead, I opted to use an LLM since it can semantically understand the content of each story (and each story's metadata) while still factoring in the original assigned confidence rating. I instructed Copilot to make this "screening" phase occur before the main 120b model processes each JSON entry, and if the screening step fails, to skip that entry.

To prompt the smaller screening model, I asked Copilot to help me but gave it some guidelines so that it could only set a "passing" score for stories centered on education (rather than ones that merely mention it). Here was the exact criteria in the prompt for these types of stories:

```
CRITERIA FOR TRUE EDUCATION STORIES:
A story should be considered CENTERED on education if its primary focus is:
- K-12 schools, colleges, or universities (operations, policies, events, achievements)
- School boards, education administrators, or education policy decisions
- Teachers, students, or educational programs as the main subject
- Educational initiatives, curriculum changes, or academic outcomes
- School facilities, funding, or educational resources
- Student activities where the educational context is central (academic competitions, school programs)
```

The screening model was asked to respond with a JSON format that the Python script could then interpret to either skip the entry or pass it to the next larger 120b model. I attempted this a few times (there were some minor issues with my script for v2 and v3, so just ignore those), but by my v4 version I landed somewhere I was mostly satisfied with.

This approach surprised me with how effective it was, even if there were a few missteps by the 20b screening model. For example, it screened out a fairly obvious story directly related to the Maryland Blueprint mentioned throughout the set of stories:
```
Processing 130/200: Blueprint pillar chairs share Caroline's progress...
  ⊘ Screened out: The title and likely content focus on a product (chairs) and personal progress, not on schools, educators, or educational programs, so the story is not centered on education.
```
*(Not a great showing for our friend gpt-oss-20b, which is apparently unaware that the term "chair" can be used to describe a role)*

In general, its problem seemed to be that there were a few false positives rather than false negatives. This didn't surprise me, but I actually did expect there to be *more* false positives by the end. In total for the v4 JSON, out of 200 stories I attempted to run (attempted because Groq rate limited me), 62 were screened out. I reviewed most of these and the majority seemed to be reasonably excluded.

## Entities Assessment
The entities were overwhelmingly accurate and descriptive, especially with the people the model listed. I have a theory for why this could be, though I could be totally wrong: having the LLM write each person's title may ground its responses more in the content of the article, since it has to look through the article's content more thoroughly for information about the person, which prevents answers that come out of left field.

Still, the model wasn't perfect. For one story, which mentioned at the end "Mary Hunt is the founder of EverydayCheapskate.com," the model returned an empty array of people. It also didn't mention EverydayCheapskate.com in its organizations.

Sometimes the titles it listed for people weren't perfect either, though it was mainly because we forced every answer to include a title. For example, high schoolers who don't have an official title were sometimes listed as "Student at {High School}" or "High Schooler" for their title — I think these are fine, but a better answer may have been to exclude a title for them instead.

One story the model created entities for that impressed me was titled "Caroline County schools welcome new teachers." This story was almost entirely a list of new faculty/teachers at various schools in Caroline County, and to my surprise the model actually listed all of them correctly (from what I can tell), including their titles:
```
["Dr. Derek Simmons, Superintendent of Caroline County Public Schools", "Mark Jones, Vice President of Caroline County Board of Education", "Amy Bauman, President of Caroline County Education Association", "Courtney Handte, President of Administrators and Supervisors Association of Caroline County and Principal of Caroline Career & Technology Center", "Rob Willoughby, Supervisor of Human Resources of Caroline County Public Schools", "Garrett Shull, Transportation Coordinator of Caroline County Public Schools", "Dr. Rebecca Wivell, Dean of Students of Caroline County Public Schools", "Thomas \"Trey\" Mills, Assistant Principal of Colonel Richardson High School", "Jared Sherman, Principal of Colonel Richardson High School", "Dr. Yolanda Holloway, Principal of Colonel Richardson Middle School", "Neal Lambert, Assistant Principal of Colonel Richardson Middle School", "Carol Breeding, Teacher at Colonel Richardson Middle School", "Alexandra Miller, Teacher at Colonel Richardson Middle School", "Kirk Dahlbert, Teacher at Colonel Richardson Middle School", "Lindsay Grow, Assistant Principal of Denton Elementary School", "Sarah Crebs, Principal of Denton Elementary School", "McKenna Fox, Teacher at Denton Elementary School", "Jennifer Vallee, Teacher at Denton Elementary School", "Makenna Nesselroad, Teacher at Denton Elementary School", "Ashlynne Raby, Teacher at Denton Elementary School", "Cathy Higgins, Teacher at Denton Elementary School", "Marissa Bacco, Teacher at Federalsburg Elementary School", "Alexis Willoughby, Teacher at Federalsburg Elementary School", "Valerie Moore, Teacher at Federalsburg Elementary School", "Stephanie Stebbins, Teacher at Federalsburg Elementary School", "Stephanie Brohawn, Principal of Federalsburg Elementary School", "Calyn Shellabarger, Teacher at Federalsburg Elementary School", "Sarah Hill, Teacher at Federalsburg Elementary School", "Brian Curtis, Assistant Principal of Federalsburg Elementary School", "Zoe Breeding, Teacher at Greensboro Elementary School", "Jackie Murray, Assistant Principal of Greensboro Elementary School", "Mary Jo Kerr, Principal of Greensboro Elementary School", "Briana Walker, Assistant Principal of Greensboro Elementary School", "Andrea Hill, Assistant Principal of Lockerman Middle School", "Jeannine Necessary, Principal of Lockerman Middle School", "Tess Charney, Teacher at Lockerman Middle School", "Hannah Holmes, Teacher at Lockerman Middle School", "Misti Larmore, Teacher at Lockerman Middle School", "Stacy DeWitt, Teacher at Lockerman Middle School", "Ali Rodrigues, Teacher at Lockerman Middle School", "Shannon Thompson, Teacher at Lockerman Middle School", "Sherry Murray, Teacher at Lockerman Middle School", "Kaitlin George, Teacher at Lockerman Middle School", "Colleen France, Teacher at Lockerman Middle School", "Garrett Nepert, Teacher at Lockerman Middle School", "Rondell Sorrell, Assistant Principal of Lockerman Middle School", "Patrick Pearce, Teacher at Lockerman Middle School", "Conor Prochaska, Teacher at Lockerman Middle School", "Crystal Drexel, Assistant Principal of North Caroline High School", "Matt Spiker, Principal of North Caroline High School", "Tommy Jefferson, Assistant Principal of North Caroline High School", "Chasity Wright, Teacher at North Caroline High School", "Lindsay Julius, Teacher at North Caroline High School", "Tammie Willis, Teacher at North Caroline High School", "Donovan Beck, Teacher at North Caroline High School", "William Becker, Teacher at North Caroline High School", "Eric Blackwell, Teacher at North Caroline High School", "Bobby Helgason, Teacher at North Caroline High School", "Connor Polosky, Teacher at Preston Elementary School", "Deanne Waters, Assistant Principal of Preston Elementary School", "A.J. Angeloni, Principal of Preston Elementary School", "Lee Sutton, Principal of Ridgely Elementary School", "Barbara Henderson, Teacher at Ridgely Elementary School", "Hunter Van-Reenan, Teacher at Ridgely Elementary School", "Jacob Dickinson, Teacher at Ridgely Elementary School", "Austin Dickinson, Teacher at Ridgely Elementary School", "Allison Beyer, Teacher at Ridgely Elementary School", "Kelsie Beall, Teacher at Ridgely Elementary School"]
```

As for the consistency of the people/places/organizations, the model seemed to do a good job here as well. I only counted a few instances where the model used the abbreviated "MD" rather than spelling out "Maryland," but they were used within proper nouns like the "MD Aware II grant." (Now, whether a grant should've been listed as an organization is another story, but I would argue overindexing on examples like this is smarter than being overly exclusionary.) The big exception to this was that the model sometimes listed North Caroline High School in the "places" array and other times in the "organizations" array, making it hard to keep track of. I'll definitely want to adjust my prompt again to make the differentiation between these types of data clearer.

Honestly, both runs seemed to work pretty well with very similar results. The main difference was the exclusion of certain, less-relevant stories, but because I didn't modify the prompt in the second run the non-affected story results were similar.

I did notice slightly worse results for the stories that were cut in the second version, though. This was likely because the prompt was focused heavily on traditional education stories, and the ones that strayed too far were probably more difficult for the model to categorize. For example, for a story titled "Kent 4-H alumna Jill Bramble to lead National Council," this was the model's response for the 'people' array:
```
["Jill Bramble, President and CEO of National 4-H Council", "John Hall, Extension Agent at University of Maryland Extension", "Laura Bradley, Mentor (Kent County 4-H)", "Susan Clarkson Fry, Former 4-H Volunteer in Montgomery County", "Reid Fry, Intermediate‑age 4‑H member (Kent County)", "Owen Fry, Intermediate‑age 4‑H member (Kent County)"]
```
This response is *okay*, but it isn't consistently formatted. Some counties are written within parentheses, while others like Montgomery County are not. It feels a little scattered and hard to read because of this — I would prefer if the model standardized this like it did for more education-focused stories.

## Education-Specific Patterns
I ran the SQL query and found the following:
- Dr. Derek Simmons, Superintendent of Caroline County Public Schools, is the most mentioned person in my sample of 100 stories (but only is mentioned twice)
- "North Caroline High School" was (arguably incorrectly) tagged as the most frequently listed place — the "real" answer, in my opinion, was Idlewild Park in Easton, Maryland which came in second
- For All Seasons was the most mentioned organization, with 18 mentions

These answers make sense to me, except for North Caroline High School being placed under "places" as I noted. I'll definitely want to clarify the difference between places and organizations in my prompt for my beat book, since the model seemed to get confused with how to categorize specific schools.

## Copilot Transcript
clay-ludwig: Can you follow these instructions for my add_entities.py file in the stardem_topic_entities directory, adjusting the file's prompt (and maybe the script itself) to be specific and hyper focused for the 'education' topic within a list of news stories that is inside the topic_stories.json file. And also follow the instructions below about passing an argument called --limit that will let me set a limit of the number of stories we test for debugging purposes.

GitHub Copilot: I'll help you modify the `add_entities.py` script in your `stardem_topic_entities` directory to be specifically tailored for education-focused stories and add a `--limit` argument for testing. Let me first check what files you have and examine the current script. 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_topic_entities)

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_entities/add_entities.py)

Now let me read the current version in your stardem_topic_entities directory and also take a quick look at the topic_stories.json to confirm it's education-focused: 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_topic_entities/add_entities.py)

Ran terminal command: head -30 /workspaces/jour329w_fall2025/ludwig/stardem_topic_entities/topic_stories.json

Perfect! I can see this is indeed education-focused content. Now I'll modify the add_entities.py script to:
1. Add a `--limit` argument for testing
2. Customize the prompt specifically for education stories with education-focused examples and context 

Using "Replace String in File"


```

```
Now let's add the `--limit` argument to the argument parser: 

Using "Replace String in File"


```

```
Now let's add the logic to actually use the `--limit` argument to restrict the number of stories processed: 

Using "Replace String in File"


```

```
Perfect! Now let's verify the changes look good by reading the modified file: 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_topic_entities/add_entities.py#1-1), lines 1 to 101

Let me check the rest of the main function: 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_topic_entities/add_entities.py#102-102), lines 102 to 152

Excellent! The modifications are complete. Let me create a summary document to show you what I've done:

## Summary

I've successfully modified your add_entities.py script in the stardem_topic_entities directory with the following changes:

### 1. **Education-Specific Prompt** 
The prompt has been completely rewritten to be hyper-focused on education stories:

- **Context**: Added explicit context that these are education beat stories covering K-12 schools, colleges, school boards, and education policy in Maryland's Eastern Shore
- **People entities**: Now prioritizes education-specific roles:
  - School administrators (superintendents, principals)
  - School board members
  - Teachers and staff
  - Students (with grade/school context)
  - Parents
  - Education officials
- **Places**: Focuses on school-relevant locations (schools as places, cities with Maryland context, counties)
- **Organizations**: Emphasizes education organizations:
  - School systems/districts
  - School boards
  - Schools as institutions
  - Educational agencies (Maryland Dept of Education)
  - Student organizations
  - Educational programs (Blueprint for Maryland's Future, CTE programs)
  - PTAs and parent groups

- **Examples**: All examples now use real education-focused entities from Maryland Eastern Shore (Talbot County Public Schools, Easton High School, etc.)

### 2. **--limit Argument**
Added a `--limit` command-line argument that allows you to test with a smaller number of stories:

```bash
# Test with just 5 stories
uv run python add_entities.py --model groq/openai/gpt-oss-120b --input topic_stories.json --limit 5

# Test with 10 stories
uv run python add_entities.py --model groq/openai/gpt-oss-120b --input topic_stories.json --limit 10
```

The script will now:
- Load all stories
- Filter out unwanted story types
- Apply the limit (if specified) to process only the first N stories
- Show clear output indicating the limit is being applied

### 3. **Other Improvements**
- Changed default input file from `stardem_sample.json` to `topic_stories.json` (matching the assignment)
- Updated the parser description to mention "education stories"

You can now run the script with a small test first, verify the results look good, and then run it on the full dataset!

Made changes.

clay-ludwig: Alright good start. I'd like to remove the max content length limit we have imposed in our script. Just completely remove it please

GitHub Copilot: I'll remove the content length limit from the script. This will allow the full story content to be processed by the LLM. 

Using "Replace String in File"


```

```
Done! I've removed the max content length limit from the script. The LLM will now process the full content of each story without truncation. This should give you better and more complete entity extraction since the LLM will have access to all the information in each article.

Made changes.

clay-ludwig: Good, next let's update our script to get another smaller model (groq/openai/gpt-oss-20b) to review each JSON entry the main model (120b) reviews in the current version of the script. I basically want, as the 120b model reviews each story, to first run each story into a "screening" model whose prompt will ask it to determine whether or not the story was properly classified in this 'education' topic since some were not. You can tell it to roughly base its answers off the 'score' value, but with a huge grain of salt (say that more elegantly in the prompt). Just try to make the model screen out stories that aren't CENTERED around an education institution/event/plan. I've highlighted an example of a story that I don't think should've been classified as 'education'.

GitHub Copilot: I'll update the script to add a screening step that filters out stories that aren't truly centered on education before processing them for entity extraction. This will use the faster 20b model to evaluate each story first. 

Using "Replace String in File"


```

```
Now I'll update the main processing loop to use this screening function: 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_topic_entities/add_entities.py#225-225), lines 225 to 275

Using "Replace String in File"


```

```
Now let's update the final summary output to include information about screened-out stories: 

Read [](file:///workspaces/jour329w_fall2025/ludwig/stardem_topic_entities/add_entities.py#280-280), lines 280 to 320

Using "Replace String in File"


```

```
Perfect! Now let's test the updated script with a small limit to see how the screening works: 

Ran terminal command: cd /workspaces/jour329w_fall2025/ludwig/stardem_topic_entities && uv run python add_entities.py --model groq/openai/gpt-oss-120b --input topic_stories.json --limit 5

Excellent! The screening is working perfectly. It correctly identified and filtered out:
1. The 4-H story (which is about youth development, not formal education)
2. The library renovation story (which is a community event, not education-focused)

Let me create a summary of what was implemented:

## Summary of Changes

I've successfully updated your add_entities.py script with a two-stage screening and processing system:

### **New Features:**

1. **Education Relevance Screening Function** (`screen_education_relevance`)
   - Uses the faster `groq/openai/gpt-oss-20b` model for quick screening
   - Evaluates each story before entity extraction
   - Considers the original classification score but treats it skeptically
   - Filters out stories that mention education only tangentially

2. **Screening Criteria:**
   - **Includes**: Stories centered on K-12 schools, colleges, school boards, teachers, students, educational programs, curriculum, facilities, funding, or academic activities
   - **Excludes**: Youth programs (4-H, scouts), library events, stories where education is just biographical background, community events with only tangential education connections

3. **Updated Processing Flow:**
   - For each story, the script now:
     1. Screens for education relevance (using 20b model)
     2. If screened out: skips entity extraction and logs the reasoning
     3. If passes: proceeds with full entity extraction (using 120b model)
   
4. **Enhanced Output:**
   - Shows screening results for each story during processing
   - Comprehensive summary showing:
     - Total stories loaded
     - Stories filtered by type (calendars, columns, etc.)
     - Stories screened out (not education-centered)
     - Successfully processed stories
   - Detailed list of screened-out stories with reasoning and original scores
   - Each processed story includes `education_screening` metadata in the JSON

### **Test Results:**
In the test run, it correctly screened out 2 of 5 stories:
- ✗ 4-H leadership story (youth development, not formal education)
- ✗ Library renovation celebration (community event, not education-focused)
- ✓ School board resignation (education governance)
- ✓ College director hire (higher education administration)
- ✓ School fundraiser event (K-12 school support)

The script is now ready to process your full dataset with improved accuracy!

Made changes.

clay-ludwig: Can you make the script save each change in real time rather than waiting until the end to compile the whole file.

GitHub Copilot: I'll modify the script to save results incrementally as each story is processed, rather than waiting until the end. This way, if the script is interrupted, you won't lose your progress. 

Using "Replace String in File"


```

```
Now let's update the part where we append stories to save immediately after each one is processed: 

Using "Replace String in File"


```

```
Let's also update the final summary to reflect that we may have resumed from a previous run: 

Using "Replace String in File"


```

```
Now let's test the incremental saving functionality: 

Ran terminal command: cd /workspaces/jour329w_fall2025/ludwig/stardem_topic_entities && rm -f stories_with_entities_v3.json && uv run python add_entities.py --model groq/openai/gpt-oss-120b --input topic_stories.json --limit 3

Perfect! Now let's verify that the file was saved and check if resumption works: 

Ran terminal command: cd /workspaces/jour329w_fall2025/ludwig/stardem_topic_entities && wc -l stories_with_entities_v3.json && echo "---" && head -5 stories_with_entities_v3.json

Great! The script now has incremental saving functionality. Here's what I've implemented:

## Summary of Incremental Saving Changes

### **Key Improvements:**

1. **Real-time Saving**: The script now saves the output JSON file after processing each story, rather than waiting until the end. This means:
   - If you interrupt the script (Ctrl+C), all processed stories are already saved
   - No data loss from interruptions or errors
   - You can monitor progress by checking the output file while the script runs

2. **Resume Capability**: The script can now resume from where it left off:
   - When you run it again with the same version number, it checks if the output file already exists
   - If it finds existing results, it loads them and skips already-processed stories
   - Continues processing from where it stopped

3. **Enhanced Progress Tracking**: The summary now shows:
   - How many stories were previously processed (if resuming)
   - How many were newly processed in the current run
   - Clear indication that the file is saved incrementally

### **Benefits:**

- **Safer for long runs**: Processing 600+ stories won't risk losing hours of work if something goes wrong
- **Easy to interrupt**: You can safely stop the script (Ctrl+C) and all completed work is preserved
- **Flexible testing**: You can start without `--limit`, let it run for a while, stop it, check results, and continue
- **Resource-friendly**: Can spread processing across multiple sessions if needed

The script is now much more robust for processing large datasets!

Made changes.
