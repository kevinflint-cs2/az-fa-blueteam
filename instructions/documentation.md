# Documentation Instructions

> **Audience:** GitHub Copilot / AI assistants
> **Phase:** 7 — Documentation
> **Goal:** Produce clear, concise, GitHub-ready documentation for each module and the project’s main README.
> **Style:** GitHub Flavored Markdown (GFM) with minimal emojis, clean structure, and professional tone.

---

## 1. Documentation Scope

The AI is responsible for creating and updating two documentation areas:

### A) Module Documentation

* File: `./docs/[MODULENAME].md`
* Each function module in `./functions/` must have a matching documentation file.
* Purpose: explain **what the module does, how it fits into the architecture, and how to use it**.
* Include:

  * Module name and short purpose statement
  * Dependencies or key integrations
  * Example configuration and environment variables
  * Example usage (code or curl example if endpoint-based)
  * Expected outputs or responses
  * Troubleshooting or known limitations (if applicable)
* Keep it factual, not promotional.

### B) Root README (`./README.md`)

* Focus on **how to use the endpoint(s)**, not internal architecture.
* Update or rewrite sections to include:

  * Project name and optional **logo/icon** in the header (if one is found or available)
  * A short 1–2 sentence summary of what the project does
  * **Quick Start / Usage** section showing how to call the endpoint
  * **Configuration**: required environment variables or setup steps
  * **Endpoints Overview** table (name → purpose → method → example URL)
  * **License / Contact / Contributing** (if applicable)
* Keep the README concise and practical—favor examples over paragraphs.

---

## 2. Formatting Standards

* Use **GitHub Flavored Markdown (GFM)** exclusively.
* Use **GitHub admonitions** (see: [GitHub community syntax discussion](https://github.com/orgs/community/discussions/16925)) where helpful:

  * `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, etc.
* Tables and code blocks should use standard GFM syntax.
* Internal links should be relative (e.g., `[Module Docs](./docs/module.md)`).

---

## 3. Writing Guidelines

* Keep it **concise** and **task-focused**. Avoid fluff.
* Use plain English; prefer clarity over technical jargon.
* **Do not overuse emojis** — one tasteful emoji in the README header is fine, otherwise avoid them.
* Always provide a brief example of how to invoke or use the function/endpoint.
* Write in the same tone as official Microsoft or Azure docs: calm, direct, and professional.
* When in doubt, favor brevity and utility.

---

## 4. Approval and Updates

* Always generate or update documentation **after testing and linting pass**.
* Show a **summary** of documentation changes before writing them:

  * Which files will be created or modified
  * Key sections to be added
* Ask for explicit approval before applying updates.
* Once approved, write complete `.md` files ready for commit.

---