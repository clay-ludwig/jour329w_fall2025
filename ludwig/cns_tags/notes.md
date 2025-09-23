CNS Tags
September 22, 2025

The tags.json file contains all of the tags used on the CNS site, and includes data like the number of uses and URL slug for each tag.

The most used tag appears to be "Politics," which was counted 1,172 times. To find this, I ran the command given in class:

```{bash}
uv run sqlite-utils memory data/tags.json "select name, count from tags order by count desc limit 20"
```

Here's the exact output of this command:
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

I chose this story to read for the tag "Chris Van Hollen": https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/

I ran this command:
```{bash}
uv run python -m newspaper --url="https://cnsmaryland.org/2025/04/18/returning-from-el-salvador-van-hollen-says-we-need-to-bring-mr-abrego-garcia-home/" -of=text | llm -m groq/moonshotai/kimi-k2-instruct-0905 "You are an expert at categorizing topics for news stories. Read the text and provide no more than 5 topics."
```

Here's the exact output of this command:


command
response/output
evaluation
(for each one)


paragraph/two at bottom that focuses on process (what i liked, was it repetitive, etc.)