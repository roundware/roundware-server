# Contributing to Roundware® Server

There are many ways to help the Roundware project including pull requests for bug fixes or new
features, updating the documentation, adding unit tests, and even simply running your own server to
test.

Roundware Server source code, issue queue and wiki is hosted on Github at:
https://github.com/roundware/roundware-server

## AGPLv3 License

Roundware Server is licensed under the [GNU Affero General Public License v3 (AGPLv3)]
(http://www.gnu.org/licenses/agpl-3.0.html). The effect of this licensing decision means the
complete source code for any Roundware Server installation must be made available to the users. You
may not make proprietary changes to the system.

## Contributor License Agreement (CLA)

Anyone who wishes to contribute code to Roundware must sign the Contributor License Agreement.
Signing the CLA means you are providing a license to Halsey Burgund (Roundware creator) to distribute
your code without restriction. The license agreement was adapted from the commonly-used Apache
CLA and is available at: https://roundware.org/files/RW_ICLA-blank.pdf

## Pull Request Procedures

Please follow these procedures while working on the Roundware Server code base and creating new
pull requests:

* Never create commits in the develop branch. Always use feature branches.
* Write clear concise commit messages stating *why* the change is being made.
* Keep commits organized into separate logical code change groups.
* Rebase your feature branches against the current develop branch before creating a pull request.
* Rebase your feature branches to squash all irrelevant commits.
* Close Github issues [via commit messages]
(https://help.github.com/articles/closing-issues-via-commit-messages/)
* Write unit tests for new features.
* Preferred branch naming method: [Issue Number]/[Short Description]
* Follow the [PEP8 - Style Guide for Python](https://www.python.org/dev/peps/pep-0008/) whenever
  possible/reasonable.
* Automate upgrade procedures whenever possible. Add upgrade procedure notes to UPGRADING.md in
  reverse chronological order.
* Document important changes in CHANGELOG.txt; use past tense phrases in reverse chronological
  order.
* New contributors, please add your name/info to AUTHORS.txt.

## Git/Github Development Workflow
Creating your local repository clone after forking on Github:
```bash
# Clone your Roundware Server fork repository
git clone git@github.com:<username>/roundware-server.git
cd roundware-server
# Add the primary Roundware Server repository as a remote called: upstream.
git remote add upstream https://github.com/roundware/roundware-server.git
```

Updating the `develop` branch in your local repository clone:
```bash
# Checkout the origin/develop branch.
git checkout develop
# Pull down the upstream/develop branch changes.
git pull upstream
# Push the changes to your origin/develop branch.
git push origin
```

Rebasing your `1/feature-name` branch verses the `develop` branch after updating:
```bash
# Switch to your feature branch.
git checkout 1/feature-name
# Rebase your new commits vs the existing commits.
git rebase develop
# Force update your feature branch with new commit history.
git push origin 1/feature-name --force
```
