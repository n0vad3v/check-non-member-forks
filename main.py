#!/usr/bin/env python
__author__ = "Nova Kwok"
__license__ = "GPLv3"
import graphene
import csv
import datetime
import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-t','--token',required=True,help="The GitHub Token.")
parser.add_argument('-o','--org',required=True,help="Org name.")
args = parser.parse_args()

org_name = args.org

headers = {"Authorization": "token "+args.token}

def run_query(query):
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()['data']
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


repo_query = """
{{
  organization(login: "{0}") {{
    repositories(first: 100 {1}) {{
      pageInfo {{
        endCursor
        hasNextPage
        hasPreviousPage
        startCursor
      }}
      edges {{
        node {{
          nameWithOwner
        }}
      }}
    }}
  }}
}}
"""

member_query = """
{{
  organization(login: "{0}") {{
  	membersWithRole(first:100 {1}) {{
        pageInfo {{
            endCursor
            hasNextPage
            hasPreviousPage
            startCursor
        }}
  	  edges {{
  	    node {{
  	      login
  	    }}
  	  }}
  	}}
  }}
}}
"""

fork_query = """
{{
  repository(owner: "{0}", name: "{1}") {{
    forks(first: 100 {2}) {{
        pageInfo {{
            endCursor
            hasNextPage
            hasPreviousPage
            startCursor
        }}
        edges {{
            node {{
            nameWithOwner
            }}
        }}
    }}
  }}
}}
"""

# Get all the repos
print("Detecting Repos...")
this_query = repo_query.format(org_name,"")
result = run_query(this_query) # Execute the query
repo_list = []
for repo in result['organization']['repositories']['edges']:
    repo_list.append(repo['node']['nameWithOwner'])

## If there are multiple pages
hasNextPage = result['organization']['repositories']['pageInfo']['hasNextPage']
while hasNextPage:
    endCursor = result['organization']['repositories']['pageInfo']['endCursor']
    endCursor_stmt = ', after: "' + endCursor + '"'
    this_query = repo_query.format(org_name,endCursor_stmt)
    result = run_query(this_query)
    for repo in result['organization']['repositories']['edges']:
        repo_list.append(repo['node']['nameWithOwner'])
    hasNextPage = result['organization']['repositories']['pageInfo']['hasNextPage']

print("The Org " + org_name + " has the following repos:")
print(repo_list)
print("\n")

# Get all members
print("Checking members...")
member_query = member_query.format(org_name,"")
result = run_query(member_query) # Execute the query
member_list = []
for member in result['organization']['membersWithRole']['edges']:
    member_list.append(member['node']['login'])

## If there are multiple pages
hasNextPage = result['organization']['membersWithRole']['pageInfo']['hasNextPage']
while hasNextPage:
    endCursor = result['organization']['membersWithRole']['pageInfo']['endCursor']
    endCursor_stmt = ', after: "' + endCursor + '"'
    query = member_query.format(org_name,endCursor_stmt)
    result = run_query(query)
    for member in result['organization']['membersWithRole']['edges']:
        member_list.append(member['node']['login'])
    hasNextPage = result['organization']['membersWithRole']['pageInfo']['hasNextPage']
    

print("The Org " + org_name + " has the following members:")
print(member_list)
print("\n")

# Get all Fork members
print("Checking forks...")
repo_name_list = list(map(lambda x: x.split('/')[1],repo_list))
for repo_name in repo_name_list:
    fork_members_list = []
    query = fork_query.format(org_name,repo_name,"")
    result = run_query(query)
    fork_list = result['repository']['forks']['edges']
    for fork in fork_list:
        fork_members_list.append(fork['node']['nameWithOwner'].split('/')[0])
    hasNextPage = result['repository']['forks']['pageInfo']['hasNextPage']
    while hasNextPage:
        endCursor = result['repository']['forks']['pageInfo']['endCursor']
        endCursor_stmt = ', after: "' + endCursor + '"'
        query = fork_query.format(org_name,repo_name,endCursor_stmt)
        result = run_query(query)
        fork_list = result['repository']['forks']['edges']
        for fork in fork_list:
            fork_members_list.append(fork['node']['nameWithOwner'].split('/')[0])
        hasNextPage = result['repository']['forks']['pageInfo']['hasNextPage']

    print("The repo " + repo_name + " has the following fork members that doesn't belong to " + org_name + ":")

    outsiders = [x for x in fork_members_list if x not in member_list]
    print(outsiders)