# GitHub Practical and Theoretical Assessment

## Requirements

- [Docker](https://docs.docker.com/get-docker/) must be installed and running on your machine.
- Python 3.x (to run the notebook kernel).
- A Jupyter-compatible environment (VS Code with the Jupyter extension, JupyterLab, etc.).

## How to run

**All exercises must be run from the notebook `python-dev-tools.ipynb`.**

Do not run the scripts in `scripts/` directly. Each exercise cell in the notebook launches its script inside an isolated Docker container, so no tools (poetry, uv, conda, Node.js, etc.) need to be installed on your machine.

1. Open `python-dev-tools.ipynb` in your IDE.
2. Make sure Docker is running.
3. Work through each exercise and write your solution in the provided code cell.
4. Run the cell below your solution to execute the reference script and verify the result.

## Project structure

```
python-dev-tools.ipynb   # Main workbook — start here
scripts/                 # Solution scripts (run via Docker from the notebook)
```
