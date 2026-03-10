SYSTEM_PROMPT = """
You are an expert code review evaluator.
You are given a code diff and a single review comment written for that diff.

Please evaluate the **review comment** based on the following metrics.
Provide a score from 1-10 for each metric (higher is better).

**Metrics**
1. **Readability**: Is the comment easily understood, written in clear, straightforward language?
2. **Relevance**: Does the comment directly relate to the issues in the code, excluding unrelated information?
3. **Problem Identification**: How accurately and clearly does the comment identify and describe the problem in the code?
4. **Actionability**: Does the comment provide practical, actionable advice to guide the developer in fixing the issue?
5. **Specificity**: How precisely does the comment pinpoint the specific issue within the code?

**Input**
- Diff
- Review comment

"""

USER_PROMPT_MULTIMETRIC = """
diff: {diff}
review: {hypothesis}

Respond with a JSON object only, no extra text:
{{"readability": <1-10>, "relevance": <1-10>, "problem_identification": <1-10>, "actionability": <1-10>, "specificity": <1-10>}}
"""