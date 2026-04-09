# Focus AI Engine

This repo now keeps a reusable **bid-editing workflow** alongside the existing repository connector tools.

## Open the workflow from the repo root

```bash
cd /workspace/focus
./focus_engine.sh open
```

To jump straight to the bid workflow instructions:

```bash
./focus_engine.sh bid-open
```

## Create or refresh a bid workspace

```bash
./focus_engine.sh bid-init quincy-office-remodel "Quincy Office Remodel"
```

That command creates a project workspace under `projects/` with:

- `input/` for the bid PDF, template, and logo files
- `working/` for draft edits
- `output/` for final exports
- `notes/` for checklist and research
- `materials_pricing.csv` for the estimate line items that need updating

## Current office remodel instruction set

The generated workspace is designed for the office remodel request that needs these edits:

- apply the gold-line RLC bid/contract styling when the template is supplied
- keep the company logo but crop/remove the black square background
- update the materials sheet with current pricing
- add a drywall T-square
- add a DeWalt laser suited to drop ceilings/drywall layout
- add one box each of Hilti collated drywall screw strips in 1-5/8 in. and 1-1/4 in.
- add delivery
- add `$400` for Big River Disposal dumpster/trash removal
- calculate the Quincy, Illinois commercial remodel permit fee from final contract value
- **leave out the floor plans**

## Files still needed before the PDF can actually be revised

Put these into the project workspace `input/` folder:

- the current bid PDF or editable source file
- the gold-line RLC template
- the original or highest-quality logo file

Without those source files, the repo can store the workflow and estimate checklist, but it cannot produce the revised PDF yet.

## Save the most recent workflows/tasks to Google Drive

```bash
./focus_engine.sh drive-save
```

Optional flags can be passed through, for example:

```bash
./focus_engine.sh drive-save --drive-dir "~/Google Drive/Focus AI Engine" --limit 3
```

This copies the latest workflow artifacts (`README.md`, `request.json`, and `output/package_edit_pass.md`) and task artifacts (`notes/checklist.md`, `notes/research.md`, and `materials_pricing.csv`) into a timestamped Google Drive folder for live editing and storage.

## Other available commands

```bash
./focus_engine.sh clone
./focus_engine.sh report
./focus_engine.sh mirror
./focus_engine.sh list
./focus_engine.sh task "git status"
```

`npm start` still opens the engine entrypoint.


## Export current project files to PDF

```bash
./focus_engine.sh bid-pdfs quincy-office-remodel
```

That command exports the current workspace text artifacts into PDF files inside `projects/quincy-office-remodel/output/`.
