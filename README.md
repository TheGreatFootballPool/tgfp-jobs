# tgfp
Repository containing all scripts / jobs / healthchecks, etc.. for The Great Football Pool

each top level folder will contain a docker compose file (to be deployed to my portainer instance) 
and complete instructions via a folder specific README

The intent is that each folder will execute one function / job

## Instructions for deployment after change
1. run [bump_version_and_deploy.sh](bump_version_and_deploy.sh)
2. from the host machine `git pull --rebase`
3. restart the `tgfp` stack (or optionally only restart the job containers for what you changed)