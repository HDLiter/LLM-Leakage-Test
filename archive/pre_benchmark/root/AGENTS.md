Environment:
- This project uses the conda environment `rag_finance`.

Execution rule:
- Always use `conda run -n rag_finance python` instead of bare `python`.
- Prefer `conda install -n rag_finance` for dependency installation.
- If a package is unavailable or unsuitable via conda, use `conda run -n rag_finance python -m pip install`.
- Never rely on ambient activation, because the sandbox shell may still resolve `python` to `D:\Anaconda\python.exe` (`base`).
