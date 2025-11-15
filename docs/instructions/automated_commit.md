# 🤖 **Automated Commit + Merge Workflow (with Copilot Auto-Merge)**

* **Developer creates a feature branch**

  * `git checkout -b feature/<change>`

* **Developer stages and commits changes**

  * `git add -A`
  * `git commit -m "<conventional commit message>"`

* **Developer pushes the branch**

  * `git push -u origin feature/<change>`

* **Developer opens a Pull Request**

  * GitHub automatically triggers:

    * CI validation (lint, tests, security scans)
    * Copilot PR Review run

* **GitHub Copilot performs automated review**

  * Identifies bugs, logic issues, anti-patterns
  * Suggests improvements
  * Leaves comments to fix before merging

* **If CI or Copilot flags issues**

  * Developer updates code
  * `git add -A` → `git commit` → `git push`
  * Automation reruns all checks and re-reviews

* **When all automation conditions are satisfied**

  * ✔ CI checks pass
  * ✔ Security scans pass
  * ✔ Copilot PR review reports **no blocking issues**
  * ✔ Branch protection rules satisfied

* **✨ Auto-merge when Copilot gives the green light**

  * GitHub Actions (or branch rules) automatically:

    * approves the PR
    * performs a “Squash and Merge” into `main`
    * closes the PR

* **Automation deletes the feature branch**

* **Developer syncs local environment**

  ```
  git checkout main
  git pull
  ```

