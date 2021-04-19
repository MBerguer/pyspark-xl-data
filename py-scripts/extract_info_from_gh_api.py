#!/usr/bin/env python3

import asyncio
import json
import http.client
import sys
import os

from dataclasses import dataclass
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import requests
from typing import Sequence

@dataclass(init=True)
class Repo:
    name: str
    owner: str

class RepoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Repo):
            return obj.__dict__
        # Base class default() raises TypeError:
        return json.JSONEncoder.default(self, obj)

async def fetch_github_repo(repo: Repo):
    """
    Keyword arguments:
    repo -- a repo object  
    """
    transport = AIOHTTPTransport(url="https://api.github.com/graphql", headers={"authorization": f"Bearer {os.getenv('GH_TOKEN')}"})

    # Using `async with` on the client will start a connection on the transport
    # and provide a `session` variable to execute queries on this connection
    async with Client(
        transport=transport, fetch_schema_from_transport=True,
    ) as session:
        # Execute single query
        repoId = f"{repo.owner}/{repo.name}"
        query = gql(
        f"""
        query {{
            closePRs: search(first: 1, type: ISSUE, query: "is:PR is:closed repo:{repoId}") {{
                issueCount
            }}
            mergedPRs: search(first: 1, type: ISSUE, query: "is:PR is:merged repo:{repoId}") {{
                issueCount
            }}
            openPRs: search(first: 1, type: ISSUE, query: "is:PR is:open repo:{repoId}") {{
                issueCount
            }}
            closedIssues: search(first: 1, type: ISSUE, query: "is:issue is:closed repo:{repoId}") {{
                issueCount
            }}
            openIssues: search(first: 1, type: ISSUE, query: "is:issue is:open repo:{repoId}") {{
                issueCount
            }}
            repository(owner: "{repo.owner}", name: "{repo.name}") {{
                createdAt
                forkCount
                issues {{
                    totalCount
                }}
                files: object(expression: "HEAD:") {{
                    ... on Tree {{
                        entries {{
                            name
                            extension
                        }}
                    }}
                }}
                name
                pullRequests(last: 10) {{
                    totalCount
                    nodes {{
                        commits(last: 1) {{
                            nodes {{
                                commit {{
                                    status {{
                                        state
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
                releases(last: 100) {{
                    totalCount
                    nodes {{
                        name
                        tagName
                    }}
                }}
                stargazerCount
            }} 
        }}
        """
        )
        result = await session.execute(query)
        return result

def get_next_page_from_link_header(link: str):
    if not link:
        return None

    link_list = list(map(lambda x: x.split('; '), link.split(',')))
    next_link = next(iter([i[0].replace('<', '').replace('>', '') for i in link_list if i[1] == 'rel="next"']), None)
    return next_link

async def fetch_github_repo_contributors(repo: Repo):
    contributors = []
    next_link = f'https://api.github.com/repos/{repo.owner}/{repo.name}/contributors?per_page=100'

    while next_link != None:
        response = requests.get(next_link)
        json = response.json()
        next_link = get_next_page_from_link_header(response.headers.get('link'))
        contributors.extend([c for c in json])

    return contributors

def write_repos_to_file(repos: Sequence[Repo], file='output/repos.json'):
    folder = os.path.dirname(file)
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(file, 'w') as f:
        for repo in repos:
            f.write(json.dumps(repo, cls=RepoEncoder, separators=(',', ':')))
            f.write('\n')
    f.close()

def parse_repo_url(url: str):
    parts = url.strip().split('/')
    return (parts[-2], parts[-1])

def load_repos(file='repos.txt'):
    repos = []
    with open(file, 'r') as f:
        for line in f.readlines():
            owner, name = parse_repo_url(line)
            repos.append(Repo(owner=owner, name=name))
    f.close()
    return repos

async def main():
    args = sys.argv[1:]
    input_repos_file = args[0]
    repos = load_repos()
    repos_data = []
    for repo in repos:
        print(f'Downloading repo: {repo}')
        info = await fetch_github_repo(repo=repo)
        contributors = await fetch_github_repo_contributors(repo=repo)
        repos_data.append(info | {'contributors': contributors})

    write_repos_to_file(repos=repos_data)

asyncio.run(main())