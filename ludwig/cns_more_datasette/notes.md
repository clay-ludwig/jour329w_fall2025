CNS More Datasette
October 8, 2025

---

## Enrichment #1

The results do "make sense," but they are formatted very inconsistently due to the fact that our Datasette extension runs each model call independently per row. It surprised me how many variations the model came up with to format its answers — everything from dashed and numbered lists to separating topics with commas. I also saw it give different amounts of topics per answer, sometimes going over the maximum of 5 we established in our prompt. It seems we need to wrangle the model much more aggressively with a better-written prompt for its results to be more useful.

I don't like how this extension forces us to use older models since it hasn't been updated, as we discussed in class. Being reliant on another developer like this can be a double-edged sword since it can save us having to write our own code, but it can also leave us dependent on their schedule. I also don't like how the extension runs model calls for each row independently — it would be much more useful if the model could be aware of its own past answers so that it could maintain consistent formatting across its results. That way, we could save tokens by prompting it without very specific formatting guidelines.

## Enrichment #2

The results make more sense here to me, given what we've learned about embeddings. Being able to rank stories based on semantic similarity to a given topic is super useful — I can imagine several scenarios where newsrooms would love something like this. I'm surprised that it ranked *all* rows of our stories — I was expecting it to be a ranked list of the top, say, 20 rows or something. I also didn't expect that the searches, themselves, would be converted into embeddings. It makes total sense and I think it's very clever, but it's a shame we have to run every search through the API because of that. That's pretty much the only part of this I don't like — this seems very useful.
