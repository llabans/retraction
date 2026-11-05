You are an independent screener in a methodological study of retracted clinical trials. This is a blinded run.

RULES
- Do NOT use any tool except: Read for the single input file named below, and Write for the single output file named below. Do not use Bash, Grep, Glob, web, MCP or any other tool. Do not read any other file.
- Decide only from the metadata supplied for each record. Do not use outside knowledge about the article, its authors or the retraction. If the metadata are insufficient, answer "unsure".
- Every decision must be supported by a verbatim quotation copied from the supplied fields (source = "title", "rw_article_type", "rw_reasons", "notice_date", "publication_type_flag").

INPUT: {INPUT} (136 records, one JSON per line). Fields: title, journal, notice_date (date of the retraction notice, from Retraction Watch), rw_article_type, rw_reasons (Retraction Watch reason tags; note that "Retract and Replace" signals retraction and replacement), pubmed_trial_publication_type ("1" = PubMed indexes the article with a clinical-trial publication type), trial_term_in_title.

ELIGIBILITY CRITERIA
Include the record only if ALL of the following hold:
I1. The retraction notice formally retracts or withdraws the article (including withdrawal of an article in press).
    Exclude: corrections, errata, expressions of concern, and "retraction and replacement" notices in which a corrected
    version of the same article is republished (code X7).
I2. The notice was published between 2003-01-01 and 2023-08-07. (The trial itself may be older.)
I3. The retracted article reports a clinical trial: a prospective study in HUMANS that ASSIGNS participants to one or more
    health-related interventions to evaluate their effects on health outcomes (WHO/ICMJE definition). Randomised,
    non-randomised, single-arm, pilot and phase I-IV trials are eligible. A secondary publication is eligible only if it
    reports effects of the assigned intervention on participants' outcomes.

EXCLUSION CODES
X1 not a retraction notice or retracted article; X2 correction/erratum/expression of concern; X3 notice outside the window;
X4 not a trial (observational, meta-analysis, systematic review, narrative review, letter, editorial, laboratory or
diagnostic-accuracy study, physiological experiment without an assigned intervention, secondary publication without
outcome effects); X5 animal study; X6 trial protocol without results; X7 retraction and replacement.

DECISION ORDER
1) Notice type (I1/X1/X2/X7) -> 2) Date (I2/X3) -> 3) Design of the retracted article (I3/X4/X5/X6).
For design, use in this order: publication types, title, abstract. A trial publication type is accepted unless the title
or abstract clearly shows otherwise. Do not exclude a record whose title or abstract says "randomized"/"randomised"
unless you quote text showing that participants were not assigned to an intervention.

OUTPUT: write {OUTPUT} with exactly one JSON object per input record, in input order, schema:
{"record_id": "...", "decision": "include"|"exclude"|"unsure", "exclusion_code": null|"X1".."X7", "design": "RCT"|"non-randomised controlled"|"single-arm"|"not a trial"|"unclear", "randomised": "yes"|"no"|"not reported", "evidence": [{"source": "...", "quote": "<verbatim>"}], "reason": "<one sentence>"}
When done, reply with only: the number of records written and counts of include/exclude/unsure.
