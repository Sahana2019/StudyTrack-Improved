# StudyTrack Before/After Verification

## Before this improvement pass

- Core FastAPI/SQLAlchemy CRUD structure was present.
- Algorithms were present and wired to API endpoints.
- AI Helper was present but its embedding implementation used hash buckets instead of the assignment's exact 12-word vocabulary.
- Empty AI search was rejected even though the assignment requires a successful zero-vector response.
- Empty summarizer fallback returned `Study Notes` instead of the required `untitled`.
- There was no automated test suite.
- There was no GitHub Actions test workflow.
- README documentation existed but did not document automated verification or the exact real-LLM prompt requested by the assignment.

## After this improvement pass

- [x] Exact 12-word fixed-vocabulary `mock_embed`.
- [x] Exact-token matching; `sorted` does not count as `sort`.
- [x] First-principles cosine similarity.
- [x] Zero-vector handling without division by zero.
- [x] Empty semantic-search query returns all five notes with score `0.0` in ID order.
- [x] Empty summarizer input returns `untitled`, `[]`, and `easy`.
- [x] Assignment payload `{"text": ...}` is supported.
- [x] `raw_text` remains accepted for backward compatibility.
- [x] `STUDYTRACK_DATABASE_URL` supports isolated test databases.
- [x] `Course.student_id` has an index for course-count/relationship lookups.
- [x] 21 automated tests pass locally.
- [x] GitHub Actions workflow added.
- [x] README expanded with setup, API usage, AI rules, complexity explanation, testing, CI, and resume evidence.
- [x] Authentication was deliberately not added because the assignment does not define an account model or authorization workflow; adding superficial authentication would change the required application flow.

## Verification command

```powershell
pytest -q
```

Expected current local result:

```text
21 passed, 0 warnings
```

The startup seeding logic uses FastAPI's lifespan API, so the test run completes without framework deprecation warnings.
