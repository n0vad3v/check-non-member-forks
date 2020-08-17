# check-non-member-forks

Normally, when you leave an Organization, your forks from the Org private repo will be deleted, while GitHub has made a mistake that the private fork might not be removed.

This script is used to check all the repos for forks made by non-Org members, using GitHub's GraphQL API.

## Usage

```
python main.py -t <GitHub Personal Access Token> -o <Org name>
```

## Example runout


```
➜  python main.py -t <GitHub Personal Access Token> -o ecenpac

Detecting Repos...
The Org ecenpac has the following repos:
['ECENPAC/team.ecenpac.com', 'ECENPAC/Artwork']


Checking members...
The Org ecenpac has the following members:
['n0vad3v']


Checking forks...
The repo team.ecenpac.com has the following fork members that doesn't belong to ecenpac:
['KnifeC']
The repo Artwork has the following fork members that doesn't belong to ecenpac:
[]
```