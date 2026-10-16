# Test suite

The tests use Python's built-in `unittest`, so no additional testing package is required.

From the repository root, run:

```powershell
python -m unittest discover -s tests -v
```

The suite covers the current implemented functionality in the graphical solver, Simplex solver, settings persistence, and basic project syntax/import smoke checks. Tkinter windows are not launched by these tests, so they can run in headless environments.

Big M and Transportation solvers are currently placeholders; tests only check that their modules import. They do not test algorithm behavior that has not been implemented yet.
