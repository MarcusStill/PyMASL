# CI/CD Workflow and GitHub Settings

This repository is configured with a continuous integration (CI) pipeline using GitHub Actions to automate testing and ensure code quality.

## Git Branching Strategy

We follow a two-branch workflow:
- **`dev`**: The development branch. All new features, bug fixes, and active work are pushed to this branch.
- **`master`**: The stable branch. Code is only merged here via Pull Requests once it has been tested and verified in `dev`.

## GitHub Actions Workflow (`ci.yml`)

The CI workflow is defined in `.github/workflows/ci.yml`. It handles the following automatic triggers:
1. **Push to `dev`**: Whenever you push changes to the `dev` branch, GitHub Actions will spin up an environment, install dependencies, and run all tests automatically.
2. **Pull Request to `master`**: Whenever a PR is created aiming to merge `dev` into `master`, the tests are run again against the merged code.

### What the workflow does:
- Checks out the code.
- Sets up Python 3.12.
- Installs necessary system libraries (e.g., `xvfb` for GUI testing without a display).
- Converts and filters `requirements.txt` to Linux format.
- Installs Python dependencies.
- Runs tests using `xvfb-run -a python -m pytest -p no:pytest-qt tests/` with dummy database variables.

## Enforcing the Workflow in GitHub (Branch Protection)

To enforce this workflow so that code *cannot* be merged into `master` if tests fail, you must configure **Branch Protection Rules** in your GitHub repository settings.

### How to set up Branch Protection:

1. Open your repository on GitHub.
2. Go to **Settings** > **Branches** (under the "Code and automation" section).
3. Under **Branch protection rules**, click **Add branch protection rule**.
4. In the **Branch name pattern** box, type `master`.
5. Check the following options:
   - **Require a pull request before merging**: This forces you to make changes in `dev` and open a PR, preventing direct pushes to `master`.
   - **Require status checks to pass before merging**:
     - Check **Require branches to be up to date before merging**.
     - In the search bar for status checks, search for `test` (this is the name of the job in `ci.yml`). You may need to have run the action at least once for it to appear in the list. Check the box next to `test`.
6. Click **Create** to save the rule.

Now, whenever you try to merge `dev` into `master`, GitHub will block the merge unless the `test` action has finished successfully with a green checkmark. If tests fail, you will need to fix them in the `dev` branch and push again.
