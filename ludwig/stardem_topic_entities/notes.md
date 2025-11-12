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
