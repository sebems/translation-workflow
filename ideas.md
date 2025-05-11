delibereately introduce errors into translation prompt to see if the review is "hallucinating"
- source: translate without context (one line at a time)
- consistency issues
- misinterpreation
- involuntary omission of a token (word)
- overly literal (is it too greedy)

THE FOCUS is the REVIEW STEP


NICE-TO-HAVES
- inter-model evaluation
- how well does each model's review perform?
    - is there a correlation between review and translation performance
    - try an evaluation pipeline
- finding typographic errors in human translations
- is there a model that analyzes another's confidence?