# Feedback: Run 1 (Whois)

## Issues

- General: Maybe even add feed back loop as last Phase
- Phase 3: If Approve, then create feature branch
- Phase 4: Created and running tests in Phase 4, should be Phase 5
- Phase 4: Note that I am using .venv and it should always active it or run it (Maybe I put this in development process)
- Phase 4: Run all tests in -vv
- Phase 4: Ran off course between Phase 4 and Phase 5
- Phase 5: Next steps always need to be multiple choice (A, B, C, Etc..) 
- Phase 5: Needed to run "func start" manually
- Phase 5: Attempted to use curl on 7071 and failed, even though it does work
    - COMMAND: bash -lc 'URL=${FUNCTION_BASE_URL:-http://localhost:7071}; echo "Checking $URL"; curl --max-time 2 -s -o /dev/null -w "%{http_code}" "$URL" || echo "unreachable"'
- Phase 5: Not sure if it is running off course, but my next steps arn't using Phases anymore, should be asking if I want to go to Phase 6
- Phase 6: Ran ruff check first (Fixed Already)
- Phase 6: Not using my virutal environment again and trying to pip install ruff 
- Phase 6: Not using next step options (A, B, C, etc...)
- Phase 6: End it with one last pytest --vv
- Phase 6: Has no knowledge of Phase 7
- Phase 7: The AI itself provided a really cool idea of adding examples in ./docs/examples
- Phase 7: Move module readmes to ./docs/modules/[MODULENAME].md

## Interesting next steps:

- Create a branch and commit all changes, then open a PR with a summary and checklist.
- Or prepare a short changelog/commit message and the exact list of files changed for your review.
Which would you like next?

## Completed
- DONE: Phase 4: Add implementation documentation to ./docs/implementation/[MODULE].py
