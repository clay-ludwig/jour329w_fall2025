CNS Metadata
September 27, 2025

---

### Government shutdown and mass firings loom: budget agreement yet to be reached
URL: https://cnsmaryland.org/2025/09/25/government-shutdown-and-mass-firings-loom-budget-agreement-yet-to-be-reached/

People:
- Chris Van Hollen
- John Thune
- Chuck Schumer

Organizations/Institutions:
- White House Office of Management and Budget
- Congress

Locations:
- Washington, D.C.
- California
- Virgnia

Topics:
- Government shutdown
- Federal workers
- Spending bill

Type: Breaking news

Importance: 4

---

### Maryland Democratic lawmakers see Kimmel suspension as threat to free speech
URL: https://cnsmaryland.org/2025/09/19/maryland-democratic-lawmakers-see-kimmel-suspension-as-threat-to-free-speech/

People:
- Jimmy Kimmel
- Chris Van Hollen
- Brendan Carr

Organizations/Institutions:
- Federal Communications Commission

Locations:
- Washington, D.C.

Topics:
- Censorship
- Free speech
- Kimmel suspension

Type: Breaking news

Importance: 4

---

### Joining cancer patients, Van Hollen, colleagues warn against research cuts
URL: https://cnsmaryland.org/2025/09/16/joining-cancer-patients-van-hollen-colleagues-warn-against-research-cuts/

People:
- Chris Van Hollen
- Zach Nunn
- Debbie Wasserman-Schultz

Organizations/Institutions:
- National Institutes of Health
- National Cancer Institute

Locations:
- Washington, D.C.
- Bethesda, Maryland

Topics:
- Cancer research
- Funding cuts
- Federal spending

Type: Feature

Importance: 5

---

### Returning from El Salvador, Van Hollen says ‘we need to bring Mr. Abrego García home’
URL: https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/

People:
- Kilmar Abrego García
- Chris Van Hollen
- Nayib Bukele

Organizations/Institutions:
- CECOT
- Maryland Legislative Latino Caucus
- United Nations

Locations:
- El Salvador
- Maryland
- Dulles, Virginia

Topics:
- Immigration
- Deportation
- CECOT

Type: Breaking news

Importance: 3

---

### Maryland lawmakers, legal experts press Trump to return Abrego García from El Salvador
URL: https://cnsmaryland.org/2025/04/16/maryland-lawmakers-legal-experts-press-trump-to-return-abrego-garcia-from-el-salvador/

People:
- Kilmar Abrego García
- Chris Van Hollen
- James E. Boasberg

Organizations/Institutions:
- CECOT
- Department of Justice
- Supreme Court

Locations:
- Washington, D.C.
- El Salvador

Topics:
- Immigration
- Deportation
- CECOT

Type: Breaking news

Importance: 3

---

# LLM Analysis

### Government shutdown and mass firings loom: budget agreement yet to be reached
URL: https://cnsmaryland.org/2025/09/25/government-shutdown-and-mass-firings-loom-budget-agreement-yet-to-be-reached/

OpenAI Command:
```{bash}
uv run python -m newspaper --url=https://cnsmaryland.org/2025/09/25/government-shutdown-and-mass-firings-loom-budget-agreement-yet-to-be-reached/ -of=text | uv run llm -m groq/openai/gpt-oss-120b "Extract structured metadata from this news story and return as JSON with these exact fields:
{
  \"url\": \"the url of the story\",
  \"people\": [\"list of up to 3 people with their titles/roles\"],
  \"organizations\": [\"government agencies, companies, groups mentioned\"],  
  \"locations\": [\"cities, counties, states, specific places\"],
  \"topics\": [\"3-5 topic tags, max 2 words each\"],
  \"story_type\": \"breaking news, feature, analysis, investigation, other\",
  \"impact\": \"a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people\",
  \"
}"
```

OpenAI Output:
```
{
  "url": null,
  "people": [
    "President Donald Trump",
    "Sen. Chris Van Hollen (D‑Maryland)",
    "Sen. John Thune, Senate Majority Leader (R‑South Dakota)"
  ],
  "organizations": [
    "White House Office of Management and Budget (OMB)",
    "U.S. House of Representatives",
    "U.S. Senate",
    "Government Employee Fair Treatment Act of 2019"
  ],
  "locations": [
    "Washington, D.C.",
    "Maryland",
    "South Dakota",
    "New York"
  ],
  "topics": [
    "government shutdown",
    "budget dispute",
    "federal workers",
    "Obamacare credits"
  ],
  "story_type": "breaking news",
  "impact": 4
}
```

Claude Command:
```{bash}
uv run python -m newspaper --url=https://cnsmaryland.org/2025/09/25/government-shutdown-and-mass-firings-loom-budget-agreement-yet-to-be-reached/ -of=text | uv run llm -m claude-4-sonnet "Extract structured metadata from this news story and return as JSON with these exact fields:
{
  \"url\": \"the url of the story\",
  \"people\": [\"list of up to 3 people with their titles/roles\"],
  \"organizations\": [\"government agencies, companies, groups mentioned\"],  
  \"locations\": [\"cities, counties, states, specific places\"],
  \"topics\": [\"3-5 topic tags, max 2 words each\"],
  \"story_type\": \"breaking news, feature, analysis, investigation, other\",
  \"impact\": \"a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people\",
  \"
}"
```

Claude Output:
```
{
  "url": "",
  "people": [
    "Chris Van Hollen - Senator (D-Maryland)",
    "John Thune - Senate Majority Leader (R-South Dakota)", 
    "Chuck Schumer - Senate Minority Leader (D-New York)"
  ],
  "organizations": [
    "White House Office of Management and Budget",
    "House of Representatives",
    "U.S. Senate",
    "Capital News Service"
  ],
  "locations": [
    "Washington",
    "Maryland",
    "South Dakota",
    "New York"
  ],
  "topics": [
    "Government shutdown",
    "Budget impasse",
    "Federal employees",
    "Tax credits",
    "Congressional deadlock"
  ],
  "story_type": "breaking news",
  "impact": 5
}
```

Evaluation: Both responses by GPT and Claude were similar to mine, with a few notable differences. Claude and I both wrote the exact same names for the people we listed, though GPT opted to include Trump's name. I had thought about writing Trump's name, too, but quickly decided he would likely be written under every story since he never gets out of the news. GPT's response, therefore, is less useful here.

GPT listed better organizations than Claude, however. I thought it was odd that Claude wrote "Capital News Service," because CNS was never part of the story but, obviously, did reporting on it. I laughed when I saw it because of how useless its answer there is—imagine if The New York Times made one of their tags on every story "The New York Times." This is a classic example of LLMs missing critical thinking that we humans are (sometimes) gifted with. You can totally understand why Claude wrote that, but its answer is entirely useless for our categorization purposes. If I see Claude repeatedly do this, I may adjust its prompt to specifically ignore CNS as an organization.

Both GPT and Claude also listed the same locations, albeit in slightly different ways with GPT writing "Washington, D.C." and Claude just writing "Washington" (I prefer GPT's answer here because it causes less confusion over Washington the state vs. Washington the capital). This specific story contained a lot of location-based information inside an interactive map, showing the states with the highest number of federal employees. For my answers, I used the information in this map to write states like California and Virginia. Neither GPT nor Claude wrote these states because they weren't included or written about in the article body—only in the map. This is one of the great flaws with this system—LLMs will miss certain parts of stories outside of the main article body, unless we give them a screenshot to look at or some way to read the code of each interactive element. Even then, there doesn't seem to be a perfect way to give LLMs access to these kinds of interactive and open-ended embeds since they cannot (yet) reliably use a computer to "explore" the story for themselves.

The other notable difference between the two LLMs' outputs was their ranking of the impact. GPT and I agreed that it was a 4, but you could arguably make Claude's case that it's a 5—or that there isn't much a difference between a 4 or 5 to begin with.

---

### Maryland Democratic lawmakers see Kimmel suspension as threat to free speech
URL: https://cnsmaryland.org/2025/09/19/maryland-democratic-lawmakers-see-kimmel-suspension-as-threat-to-free-speech/

OpenAI Command:
```{bash}
uv run python -m newspaper --url=https://cnsmaryland.org/2025/09/19/maryland-democratic-lawmakers-see-kimmel-suspension-as-threat-to-free-speech/ -of=text | uv run llm -m groq/openai/gpt-oss-120b "Extract structured metadata from this news story and return as JSON with these exact fields:
{
  \"url\": \"the url of the story\",
  \"people\": [\"list of up to 3 people with their titles/roles\"],
  \"organizations\": [\"government agencies, companies, groups mentioned\"],  
  \"locations\": [\"cities, counties, states, specific places\"],
  \"topics\": [\"3-5 topic tags, max 2 words each\"],
  \"story_type\": \"breaking news, feature, analysis, investigation, other\",
  \"impact\": \"a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people\",
  \"
}"
```

OpenAI Output:
```
{
  "url": null,
  "people": [
    "Rep. Johnny Olszewski (Maryland Representative)",
    "Rep. Jamie Raskin (U.S. Representative, constitutional lawyer)",
    "Sen. Chris Van Hollen (Maryland Senator)"
  ],
  "organizations": [
    "ABC",
    "Federal Communications Commission (FCC)",
    "No Political Enemies Act (NOPE)",
    "U.S. Congress",
    "Trump administration"
  ],
  "locations": [
    "Washington, D.C.",
    "Maryland",
    "United States Capitol"
  ],
  "topics": [
    "free speech",
    "media censorship",
    "FCC",
    "legislation"
  ],
  "story_type": "breaking news",
  "impact": 4
}
```

Claude Command:
```{bash}
uv run python -m newspaper --url=https://cnsmaryland.org/2025/09/19/maryland-democratic-lawmakers-see-kimmel-suspension-as-threat-to-free-speech/ -of=text | uv run llm -m claude-4-sonnet "Extract structured metadata from this news story and return as JSON with these exact fields:
{
  \"url\": \"the url of the story\",
  \"people\": [\"list of up to 3 people with their titles/roles\"],
  \"organizations\": [\"government agencies, companies, groups mentioned\"],  
  \"locations\": [\"cities, counties, states, specific places\"],
  \"topics\": [\"3-5 topic tags, max 2 words each\"],
  \"story_type\": \"breaking news, feature, analysis, investigation, other\",
  \"impact\": \"a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people\",
  \"
}"
```

Claude Output:
```
{
  "url": "not provided",
  "people": [
    "Jimmy Kimmel - TV host",
    "Jamie Raskin - Rep./Constitutional lawyer", 
    "Chris Van Hollen - Maryland Senator"
  ],
  "organizations": [
    "ABC",
    "Federal Communications Commission",
    "Maryland congressional delegation",
    "Jimmy Kimmel Live!",
    "CNN",
    "MSNBC",
    "Fox News"
  ],
  "locations": [
    "Washington",
    "Maryland",
    "United States Capitol"
  ],
  "topics": [
    "Free speech",
    "Media censorship",
    "Political retaliation",
    "Broadcasting licenses",
    "First Amendment"
  ],
  "story_type": "breaking news",
  "impact": 4
}
```

Evaluation: Both LLMs gave poor responses here, though I prefer Claude's because of its people section. One of GPT's biggest flaws was its exclusion of Jimmy Kimmel in the people section. I'm not sure how GPT missed that, since he is a key figure and his name was in the headline/article body. Claude also listed "Jimmy Kimmel Live!" under organizations, which GPT did not.

More importantly, both LLMs missed Brendan Carr, who is central to this story. He is far more important than Jamie Raskin, who both LLMs wrote under their people sections. This is especially puzzling since Carr was written about extensively in the article, including his "we can do this the easy way or the hard way" quote. If I had to guess why both LLMs missed this, it's because Carr is less established and well-known in Washington than somebody like Raskin—especially within the LLMs' training data window, which likely cuts off before the second Trump administration. Still, the Kimmel story wouldn't have happened without Carr's threats—which were, themselves, unprecedented and newsworthy. Omitting him from the key figures section, therefore, seems like a heavily misguided decision. I would give both LLMs failing grades here solely because of this.

In general, LLMs' inability to judge what is culturally relevant hampers their ability to give high quality responses. This story was a massive cultural moment (in terms of the government attempting to directly interfere with free speech), yet both LLMs don't seem to grasp this judging by their responses. This gap feels like one of the main reasons why LLMs seem to lack "critical thinking," like I wrote about in the previous example.

---

### Joining cancer patients, Van Hollen, colleagues warn against research cuts
URL: https://cnsmaryland.org/2025/09/16/joining-cancer-patients-van-hollen-colleagues-warn-against-research-cuts/

OpenAI Command:
```{bash}
uv run python -m newspaper --url=https://cnsmaryland.org/2025/09/16/joining-cancer-patients-van-hollen-colleagues-warn-against-research-cuts/ -of=text | uv run llm -m groq/openai/gpt-oss-120b "Extract structured metadata from this news story and return as JSON with these exact fields:
{
  \"url\": \"the url of the story\",
  \"people\": [\"list of up to 3 people with their titles/roles\"],
  \"organizations\": [\"government agencies, companies, groups mentioned\"],  
  \"locations\": [\"cities, counties, states, specific places\"],
  \"topics\": [\"3-5 topic tags, max 2 words each\"],
  \"story_type\": \"breaking news, feature, analysis, investigation, other\",
  \"impact\": \"a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people\",
  \"
}"
```

OpenAI Output:
```
{
  "url": null,
  "people": [
    "Sen. Chris Van Hollen (U.S. Senator, Maryland)",
    "Rep. Zach Nunn (U.S. Representative, Iowa)",
    "President Donald Trump (U.S. President)"
  ],
  "organizations": [
    "National Institutes of Health (NIH)",
    "National Cancer Institute (NCI)",
    "American Cancer Society",
    "White House",
    "Senate Appropriations Committee",
    "House Appropriations Committee",
    "Trump administration"
  ],
  "locations": [
    "Maryland",
    "Bethesda, MD",
    "Washington, D.C.",
    "Massachusetts",
    "Iowa",
    "Florida",
    "Alabama"
  ],
  "topics": [
    "cancer research",
    "budget cuts",
    "NIH",
    "politics"
  ],
  "story_type": "breaking news",
  "impact": 4
}
```

Claude Command:
```{bash}
uv run python -m newspaper --url=https://cnsmaryland.org/2025/09/16/joining-cancer-patients-van-hollen-colleagues-warn-against-research-cuts/ -of=text | uv run llm -m claude-4-sonnet "Extract structured metadata from this news story and return as JSON with these exact fields:
{
  \"url\": \"the url of the story\",
  \"people\": [\"list of up to 3 people with their titles/roles\"],
  \"organizations\": [\"government agencies, companies, groups mentioned\"],  
  \"locations\": [\"cities, counties, states, specific places\"],
  \"topics\": [\"3-5 topic tags, max 2 words each\"],
  \"story_type\": \"breaking news, feature, analysis, investigation, other\",
  \"impact\": \"a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people\",
  \"
}"
```

Claude Output:
```
{
  "url": "",
  "people": [
    "Chris Van Hollen - Maryland Senator",
    "Teresa Simpson - ovarian cancer patient from Massachusetts", 
    "Zach Nunn - Representative from Iowa"
  ],
  "organizations": [
    "National Institutes of Health",
    "National Cancer Institute",
    "American Cancer Society",
    "Trump administration",
    "White House",
    "Congress",
    "Senate Appropriations Committee",
    "House Appropriations Committee"
  ],
  "locations": [
    "Washington",
    "Maryland",
    "Capitol Hill",
    "Massachusetts",
    "Iowa",
    "Bethesda",
    "Florida",
    "Alabama"
  ],
  "topics": [
    "Cancer research",
    "Budget cuts",
    "NIH funding",
    "Medical trials",
    "Bipartisan support"
  ],
  "story_type": "breaking news",
  "impact": 4
}
```

Evaluation: In the people section, GPT once again included Trump's name. Beyond that, though, the LLMs differed over something I spent time grappling with: whether to include the name of Teresa Simpson, an ovarian cancer patient mentioned in the article.

I opted to exclude Simpson, since she is not a well-known figure that somebody would likely search for to find this article at a later date. That said, I debated whether or not she was worth including because she was prominently quoted in the article and was a speaker at the rally, which this article is based on. I thought it was interesting that the LLMs differed here in their responses, since you can reasonably argue whether she should be included. It seems like GPT and Claude landed on different sides of this coin, perhaps because of differences in their training. It's possible that Claude wanted to focus more on the human interest side of this story than GPT, leading it to include Simpson's name. Being aware of the ways different models "lean" is useful when considering things like this.

---

### Returning from El Salvador, Van Hollen says ‘we need to bring Mr. Abrego García home’
URL: https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/

OpenAI Command:
```{bash}
uv run python -m newspaper --url=https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/ -of=text | uv run llm -m groq/openai/gpt-oss-120b "Extract structured metadata from this news story and return as JSON with these exact fields:
{
  \"url\": \"the url of the story\",
  \"people\": [\"list of up to 3 people with their titles/roles\"],
  \"organizations\": [\"government agencies, companies, groups mentioned\"],  
  \"locations\": [\"cities, counties, states, specific places\"],
  \"topics\": [\"3-5 topic tags, max 2 words each\"],
  \"story_type\": \"breaking news, feature, analysis, investigation, other\",
  \"impact\": \"a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people\",
  \"
}"
```

OpenAI Output:
```
{
  "url": "",
  "people": [
    "Chris Van Hollen (U.S. Senator, Maryland)",
    "Kilmar Abrego García (detained Salvadoran national)",
    "Donald Trump (former U.S. President)"
  ],
  "organizations": [
    "U.S. Senate",
    "Maryland Legislative Latino Caucus",
    "Government of El Salvador",
    "CECOT (Central Prison of El Salvador)",
    "Santa Ana Prison",
    "Trump Administration"
  ],
  "locations": [
    "Dulles, Virginia",
    "Washington Dulles International Airport",
    "San Salvador, El Salvador",
    "CECOT prison, San Salvador",
    "Santa Ana, El Salvador"
  ],
  "topics": [
    "detention",
    "human rights",
    "US‑El Salvador",
    "prison reform"
  ],
  "story_type": "breaking news",
  "impact": 3
}
```

Claude Command:
```{bash}
uv run python -m newspaper --url=https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/ -of=text | uv run llm -m claude-4-sonnet "Extract structured metadata from this news story and return as JSON with these exact fields:
{
  \"url\": \"the url of the story\",
  \"people\": [\"list of up to 3 people with their titles/roles\"],
  \"organizations\": [\"government agencies, companies, groups mentioned\"],  
  \"locations\": [\"cities, counties, states, specific places\"],
  \"topics\": [\"3-5 topic tags, max 2 words each\"],
  \"story_type\": \"breaking news, feature, analysis, investigation, other\",
  \"impact\": \"a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people\",
  \"
}"
```

Claude Output:
```
{
  "url": "",
  "people": [
    "Chris Van Hollen - Maryland Senator",
    "Kilmar Abrego García - Detained individual",
    "Nayib Bukele - El Salvador President"
  ],
  "organizations": [
    "Maryland Legislative Latino Caucus",
    "CECOT prison",
    "U.S. Court of Appeals for the Fourth Circuit",
    "Trump administration",
    "MS-13",
    "United Nations"
  ],
  "locations": [
    "El Salvador",
    "Dulles, Virginia",
    "Maryland",
    "San Salvador",
    "Santa Ana",
    "Washington Dulles International Airport"
  ],
  "topics": [
    "Constitutional rights",
    "International law",
    "Prison conditions",
    "Deportation policy",
    "Due process"
  ],
  "story_type": "breaking news",
  "impact": 4
}
```

Evaluation: In this case, both LLMs did a more thorough job than I did. While many parts of the responses were similar to my answers, the LLMs covered more organizations and places.

For the impact rating, I had chosen a 3—putting me in agreement with GPT—but Claude's answers more closely aligned with the ones I wrote. I also like Claude's topics more than GPT's, since they are more specific and descriptive of the story. If somebody were retroactively searching for this story, I'd imagine them having an easier time if Claude's keywords were used for tagging instead of GPT's.

Semantically, both LLM responses were nearly identical to each other.

---

### Maryland lawmakers, legal experts press Trump to return Abrego García from El Salvador
URL: https://cnsmaryland.org/2025/04/16/maryland-lawmakers-legal-experts-press-trump-to-return-abrego-garcia-from-el-salvador/

OpenAI Command:
```{bash}
uv run python -m newspaper --url=https://cnsmaryland.org/2025/04/16/maryland-lawmakers-legal-experts-press-trump-to-return-abrego-garcia-from-el-salvador/ -of=text | uv run llm -m groq/openai/gpt-oss-120b "Extract structured metadata from this news story and return as JSON with these exact fields:
{
  \"url\": \"the url of the story\",
  \"people\": [\"list of up to 3 people with their titles/roles\"],
  \"organizations\": [\"government agencies, companies, groups mentioned\"],  
  \"locations\": [\"cities, counties, states, specific places\"],
  \"topics\": [\"3-5 topic tags, max 2 words each\"],
  \"story_type\": \"breaking news, feature, analysis, investigation, other\",
  \"impact\": \"a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people\",
  \"
}"
```

OpenAI Output:
```
{
  "url": "",
  "people": [
    "Sen. Chris Van Hollen (U.S. Senator, MD)",
    "Rep. Jamie Raskin (U.S. Representative, MD)",
    "Vice President Félix Ulloa (Vice President of El Salvador)"
  ],
  "organizations": [
    "U.S. Senate",
    "U.S. House of Representatives",
    "Government of El Salvador",
    "CECOT Prison",
    "Supreme Court of the United States",
    "U.S. District Court (Washington, D.C.)",
    "Attorney General's Office (FL)",
    "America’s Voice",
    "UB Greensfelder (law firm)",
    "Fox News"
  ],
  "locations": [
    "Washington, D.C.",
    "Maryland",
    "El Salvador",
    "CECOT Prison"
  ],
  "topics": [
    "immigration",
    "deportation",
    "court ruling",
    "human rights"
  ],
  "story_type": "breaking news",
  "impact": 4
}
```

Claude Command:
```{bash}
uv run python -m newspaper --url=https://cnsmaryland.org/2025/04/16/maryland-lawmakers-legal-experts-press-trump-to-return-abrego-garcia-from-el-salvador/ -of=text | uv run llm -m claude-4-sonnet "Extract structured metadata from this news story and return as JSON with these exact fields:
{
  \"url\": \"the url of the story\",
  \"people\": [\"list of up to 3 people with their titles/roles\"],
  \"organizations\": [\"government agencies, companies, groups mentioned\"],  
  \"locations\": [\"cities, counties, states, specific places\"],
  \"topics\": [\"3-5 topic tags, max 2 words each\"],
  \"story_type\": \"breaking news, feature, analysis, investigation, other\",
  \"impact\": \"a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people\",
  \"
}"
```

Claude Output:
```
{
  "url": "",
  "people": [
    "Kilmar Abrego García - Maryland resident mistakenly deported to El Salvador",
    "Chris Van Hollen - Maryland Democratic Senator",
    "Jamie Raskin - Maryland Democratic Representative"
  ],
  "organizations": [
    "Supreme Court",
    "Trump Administration", 
    "El Salvador government",
    "Immigration Court",
    "America's Voice",
    "CECOT prison",
    "U.S. embassy"
  ],
  "locations": [
    "Maryland",
    "El Salvador", 
    "Washington",
    "CECOT prison"
  ],
  "topics": [
    "Immigration deportation",
    "Constitutional rights",
    "International relations",
    "Supreme Court",
    "Due process"
  ],
  "story_type": "breaking news",
  "impact": 4
}
```

Evaluation: Something I noticed after this last response was that GPT has been more consistent with the actual formatting of its answers than Claude—particularly with the titles of people it identifies. For all articles, it has consistently written people in the format "Name (Title)", sourcing its titles directly from the article. Claude, on the other hand, seems to decide how to format people's titles on the spot. We would likely need to adjust Claude's prompt to be more specific about the format, saying something like "write titles inside parenthesis" and including examples of correctly-written titles.

---

# Overall Evaluation

Overall, the LLMs did a decent job writing metadata for these stories, with the glaring exception of the Jimmy Kimmel story. I actually expected there to be more variety in how the models formatted their responses each time, since the prompt wasn't very specific about how it expected things to be written. Like I said above, we could expand our prompts to include stricter, more specific guidelines about the exact formats for each section (i.e. specific rules around people's titles). We could also give it rules for who/what to avoid writing about, so that we don't end up with Donald Trump being written as a "key figure" under every story.

Something I repeatedly hit on in my evaluations above was the fact that LLMs don't seem to intuitively understand what actually makes helpful metadata. I think the best way to solve this would be to give the LLMs a description of what we plan on using this metadata for down the road. Doing so would help frame the task in a way that it would (hopefully) be clearer on exactly what it should include and how it should format it. I could imagine including something like this in the prompt to help with this problem:

```
This metadata will be used to create a searchable database of news stories from CNS, where journalists, researchers and academics will look for articles by searching for specific people, organizations, locations, or topics. The goal, in the future, is to help people find relevant stories they might have missed or want to reference later. For now, please just focus on extracting information that someone would actually search for, rather than just what appears most prominently in the text.
```

Additionally, to address the problem of LLMs not understanding culture (like I mentioned above with the Jimmy Kimmel story) we could use some kind of RAG technique to help it fill in knowledge gaps about current events. I suspect it would've vastly improved both LLMs' responses for the Jimmy Kimmel story if GPT and Claude were able to briefly search the web for other stories and summaries of the Kimmel fiasco, since both models likely had limited training data about Brendan Carr's role as FCC Chairman and how unprecedented his threats against broadcast networks truly were.

### Speeding Up the Process

This is a task where LLMs run circles around humans–it took me significantly longer to write my metadata by hand, and the results were honestly just worse (less detailed, missing certain facts) compared to most of the LLM responses. It's definitely easy to get caught up in all the little mistakes an LLM makes and to stop appreciating what it still is capable of (albeit imperfectly).

For me, the second-slowest part of this exercise was actually comparing the LLM responses with mine. It took a while to repeatedly scroll up to my responses, then back down to theirs. This is the same reason why the AI chat interface, while simple, can be difficult to work in when having long back-and-forths with an LLM. Being able to directly compare the diffs between my responses and the LLM's without scrolling back and forth would've sped this up significantly. I also think having a more systematic way to iterate on prompts would have made this much faster. Right now, testing a prompt change would mean manually running it on each story and then doing the comparison work all over again. If I had some kind of script that could run multiple prompt versions on the same story set and generate side-by-side comparisons of the LLMs' resopnses, I could have tested 5-10 different prompts in the time it took me to analyze these 5 stories once.
