# Modifying the project

Use the following steps to make bug fixes or feature enhancements to the ETL implementation.

## Step 1: Clone the repository
Begin by cloning the repository to your local machine.

```bash
git clone git@github.com:Su-informatics-lab/ardac-etl.git
```

> [!NOTE]
> The example above assumes that you are working from the command line and have SSH keys set up with GitHub. If you are using the GitHub desktop application or VSCode, you can clone the repository using the HTTPS URL instead.

## Step 2: Create a new branch
Create a new branch for your changes. The branch name should be descriptive of the changes you are making and be preceeded with a `feat/` or `bug/` string, such as: `feat/new-feature-name`.
> [!NOTE]
> We use [Gitflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) for development, so feature branches should be made from `develop` and then later merged into `main` for major releases (see below).
```bash
git checkout develop
git checkout -b feat/new-feature-name
```

## Step 3: Make your changes
Make your changes to the implementation in the new branch.  If you are making changes in an integrated development environment (IDE) on a local system (such as a lap top or desktop) and testing on a remote system you may need to make several commits locally and push them to the remote Git server to make them available on the remote system for testing.  This process should be repeated until the new feature is fully implemented and tested within the feature branch on the remote system.  Once the feature is completed and tested, proceed to Step (4).

To commit changes to the branch locally:
```bash
git commit -m "feat: Feature description or other updates to the feature"
```

To push the locally committed changes to the remote Git repository:
```bash
git push origin feat/new-feature-name
```

To pull the new branch on the remote system for the first time:
```bash
git fetch origin
git pull
git checkout feat/new-feature-name
```


## Step 4: Update the version identifiers
Modify the version identifiers in the Python scripts in the feature branch on your local system.  Open the `_constants.py` file in the `python/ardac` directory.  Update the `__mapping_version__` global variable to indicate the feature update.  The format of the version identifier is _major\_release_._minor\_release_._bug\_fix_.  Feature updates should be indicated by incrementing the _minor\_release_ value. If the branch is the first change to a major release, then that value should be incremented instead.  Bug fixes should be indicagted by increasing the _bug\_fix_ value.  If the branch is also the first change towards a new DCC data model, then the `__dcc_data_release__` value should also be updated to reflect support of a new data model.  Whenever the `__dcc_data_release__` value is updated, the `__mapping_version__` value should be reset to `1.0.0` to indicate the first ETL implementation for the new data model.

Next, modify the DCC data model version identifier in the Nextflow configuration, if neccessary.  Open the `nextflow.config.template` file and update the `dcc_release` value if the branch `__dcc_data_release__` value was updated for the Python scripts.

Once the version values have been changed, save the changes and commit the changes to the branch.

```bash
git add -u
git commit -m "feat: Updated version identifiers for feature"
git push origin feat/new-feature-name
```

Push the commit to the remote Git repository:
```bash
git push origin feat/new-feature-name
```

## Step 5: Merge the feature branch into the development branch
The feature branch can now be merged into the development branch. On your local system, perform:

```bash
git checkout develop
git pull
git merge feat/new-feature-name
```

Resolve any conflicts that might occur during the merge, then retest.  Continue retesting and fixing until the branch works properly.

Commit the fixes:

```bash
git add -u
git commit -m "Description of merge conflict resolution"
```

Push the commits to the remote Git repository:

```bash
git push origin develop
```

At this point you should most likely delete both the local and remote copies of your feature branch:

```bash
git push origin --delete feat/new-feature-name
git branch -d feat/new-feature-name
```

## Step 6: Test the develop branch
The `develop` branch is where many features are merged together and tested from different branches.  To ensure the `develop` branch is functioning properly you should test that branch.  If testing fails, then create a bug fix branch with the `bug/` branch name prefix, then repeat the testing, fixing, and merging process with the new bug branch.

## Step 7 (optional): Merge development branch into main branch
Now you are ready, but not required, to merge these changes onto `main` and create a new release. If there are additional updates planned, then repeat all of the above steps to continue adding new features onto the `develop` branch for the next release.

> [!NOTE]
> Release branches are created from main and immediately merged from develop in order to faciliate the pull request process (PR).

Begin by creating a release branch, and merge your development changes into this branch:
```bash
git checkout main
git pull
git checkout -b release/2.1.0
git merge develop
```

Test the new release branch using the process described for the development branches.  All changes should be committed and pushd to the remote Git repository:
```bash
git add -u
git commit -m "Describe any problems caused by the merge and how they were fixed"
git push origin release/2.1.0
```

When testing is complete, merge your changes into the `main` branch. Because the main branch is protected, you will need to create a pull request and have it reviewed by a team member. This process is most easily accomplished using the GitHub web interface or the GitHub desktop application. When creating a tag name for merged changes into `main`, the format should be `DCC_VERSION=__dcc_data_release__,MAPPING_VERSION=__mapping_version__`.  After the PR is closed and the changes are merged, you can (and should) remove the release branch. The Github web UI should prompt for this when completing the merge.


