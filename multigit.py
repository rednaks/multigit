#!/usr/bin/env python
# -*- coding: utf-8 -*-

from github import Github

import json
from argparse import ArgumentParser
import os


# First create a Github instance:

# using an access token
g = Github(os.environ['GH_TOKEN'])

# Then play with your Github objects:


def main(args, config):
    org_name = config.get('org_name')
    for repo in config.get('repos', []):
        repo_path = f'{org_name}/{repo}'
        # check if it has branch
        r = g.get_repo(repo_path)
        branches = [ b.name for b in list(r.get_branches()) ]
        #print(branches)
        source_branch_exists = args._from in branches
        if not source_branch_exists:
            print(f"source branch {args._from} doesn't not exist for repo {repo_path}")
            if args.create_branches:
                print(f"Creating source branch {args._from} for {repo_path}")
            else:
                print("Skipping ...")
                continue


        target_branch_exists = args.to in branches
        if not target_branch_exists:
            print(f"target branch {args.to} doesn't not exist for repo {repo_path}")
            print('Skipping ...')
            if args.create_branches:
                print(f"Creating target branch {args.to} for {repo_path}")
            else:
                print("Skipping ...")
                continue

        comp = r.compare(args.to, args._from)

        pr_to_merge = None
        if args.create or args.list or args.merge:
            open_prs = list(r.get_pulls(head=args._from, base=args.to))
            print(open_prs)
            try:
                pr_to_merge = open_prs[0]
            except IndexError:
                ...

        if comp.total_commits > 0 and args.create and pr_to_merge is None:
            # create pull request
            r.create_pull(
                title=f"Merge {args._from} into {args.to}",
                body=f"{args.ref}",
                head=args._from,
                base=args.to
            )
        else:
            print(f'No diff, no PR to create for {repo_path}')

        if args.merge and pr_to_merge is not None:
            print(f"merging {pr_to_merge} for {repo_path}")
            status = pr_to_merge.merge()
            print(status)



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--from", dest='_from', help="source branche to create pull request",
                         required=True)
    parser.add_argument("--to", help="destination branche to create pull request",
                        required=True)
    parser.add_argument("--ref", help="reference branche: org/project#issue_number",
                        required=True)

    parser.add_argument("--create", action="store_true", help="create pull requests")
    parser.add_argument("--merge", action="store_true", help="create pull requests")
    parser.add_argument("--list", action="store_true", help="create pull requests")
    parser.add_argument("--create-branches", action="store_true", help="create branches if doesn't exist")
    parser.add_argument("--delete-branches", action="store_true", help="delete branches")


    config = None
    with open('config.json') as fp:
        config = json.load(fp)

    main(parser.parse_args(), config)



