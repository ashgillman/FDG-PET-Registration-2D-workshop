# Notebook workflow

- Treat `build_notebooks.py` as the source of truth for `NeuroSTEM_exercise.ipynb` and its temporary `NeuroPET_exercise.ipynb` Binder compatibility copy.
- Make workshop content and default-value changes in the generator, then run `python build_notebooks.py` to regenerate the student notebook.
- Before committing, rerun `python build_notebooks.py` after any notebook execution or interactive experimentation.
- Verify that every code cell in both generated notebooks has an empty `outputs` list and a null `execution_count`, and review the generated diff to confirm that workshop defaults are restored and intended changes are preserved.
- Use `python scripts/build_finished_notebook.py` to execute and validate a separate review copy in ignored `dist/NeuroSTEM_exercise_finished.ipynb`.
- Keep executed review copies out of Git, and do not commit or push unless the user explicitly requests it.
