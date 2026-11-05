You are taking part in a methodological experiment. Answer ONLY from your own trained knowledge.

RULES
- Do NOT use any tool except Write for the single output file named below. No web, no MCP, no Bash, no file reading.
- Do not invent identifiers. If you are not sure of a PMID or DOI, leave it empty. It is better to give fewer, correct items.

TASK
List as many as you can (up to 150) published clinical trials in humans (randomised or not) in medicine or health sciences whose RETRACTION NOTICE was published between 2003-01-01 and 2023-08-07. Exclude retraction-and-replacement cases, corrections and expressions of concern.

OUTPUT: write {OUTPUT}, one JSON object per line:
{"n": 1, "first_author": "...", "title": "<as exact as you can>", "journal": "...", "publication_year": 2010, "retraction_year": 2012, "pmid": "" , "doi": "", "confidence": "high"|"medium"|"low"}
When done, reply with only the number of items written and how many have a PMID or DOI.
