# WorkFlow for FWF

## Main Brach

The main repository will always hold two evergreen branches:

- `master`
- `stable`


The main branch should be considered origin/master and will be the main branch where the source code of HEAD always reflects a state with the latest delivered development changes for the next release. As a developer, you will be branching and merging from master.

Consider origin/stable to always represent the latest code deployed to production. During day to day development, the stable branch will not be interacted with.

When the source code in the master branch is stable and has been deployed, all of the changes will be merged into stable.



$ git checkout stable                               // change to the stable branch
$ git merge master                                  // forces creation of commit object during merge
$ git push origin stable --tags                     // push tag changes