# HTMLGenerator

This repository contains a GitHub-native workflow for publishing a static, visual report website from markdown content.

## Workflow

1. Open the web interface at `docs/index.html` (or the GitHub Pages site).
2. Download the markdown template and fill in the `Metrics` and `Text` sections.
3. Upload the file from the same interface using a GitHub token with repository write access.
4. The upload commits the file to `content/submissions/*.md` and triggers the GitHub Actions workflow.
5. The workflow renders `report.html` and deploys it to GitHub Pages.

## Repository structure

- `/docs/index.html` – web UI for template download and upload
- `/templates/report-template.md` – reusable markdown template
- `/scripts/generate_site.py` – markdown-to-static-HTML generator
- `/.github/workflows/build-and-deploy-site.yml` – automated build + deploy pipeline

## Accessing the generated site

After upload, use the link shown in the web UI or open:

`https://<owner>.github.io/<repo>/report.html`

If it is not ready yet, check workflow progress at:

`https://github.com/<owner>/<repo>/actions`
