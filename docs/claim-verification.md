# Private Claim Verification System

The Member 2 Private Claim Verification Engine allows item finders or campus authorities to establish verification questions while protecting secret answers server-side.

## Workflow
1. **Question Setup**: Finder provides verification questions (e.g. "What card is inside the front pocket?") and expected answers.
2. **Server-Side Protection**: Expected answers are stored securely in `VerificationQuestion.expected_answer` and NEVER returned in client API payloads or Jinja2 context.
3. **Claimant Response**: Claimant answers questions in the private verification form.
4. **Answer Evaluation**: `AnswerMatcher` calculates similarity combining:
   - Sequence ratio (Ratcliff-Obershelp / Levenshtein)
   - Token overlap Jaccard index
   - Case & punctuation normalization
5. **Score Aggregation**: `VerificationScorer` averages question scores and assigns confidence:
   - \(\ge 75.0\%\) \(\rightarrow\) `STRONG_VERIFICATION`
   - \(\ge 50.0\%\) \(\rightarrow\) `PARTIAL_VERIFICATION`
   - \(< 50.0\%\) \(\rightarrow\) `WEAK_VERIFICATION`
6. **Admin Review**: Claim status transitions to `UNDER_VERIFICATION` and is sent to Member 3 Admin Review for final human approval.
