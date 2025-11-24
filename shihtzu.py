#!/usr/bin/env python3

import argparse
import sys

# Local imports
from core.bloodhound import *


HELP_EPILOG = '''\
Queries:
  list-users                 list users
  list-computers             list computers
  list-groups                list groups
  describe-users             show information on users
  describe-computers         show information on computers
  describe-groups            show information on groups
  list-members               list members of groups
  list-user-memberships      list group memberships of users
  list-computer-memberships  list group memberships of computers
  list-kerberoastable        list domain users with SPNs set
  list-asrep-roastable       list domain users that don't require Kerberos pre-authentication

Examples:
  > shihtzu list-users
  > shihtzu list-kerberoastable
  > shihtzu -o describe-users elliot.alderson
  > shihtzu -oej list-members "Domain Admins"
  > shihtzu -o list-user-memberships elliot.alderson | shihtzu -f - describe-groups
'''

AVAILABLE_QUERIES = (
    'list-users',
    'list-computers',
    'list-groups',
    'describe-users',
    'describe-computers',
    'describe-groups',
    'list-members',
    'list-user-memberships',
    'list-computer-memberships',
    'list-kerberoastable',
    'list-asrep-roastable'
)


def parse_args():
    parser = argparse.ArgumentParser(
        prog='shihtzu',
        description='A small CLI parser for Bloodhound-generated files.',
        formatter_class=argparse.RawTextHelpFormatter,
        allow_abbrev=False,
        epilog=HELP_EPILOG
    )

    # Root-level parameters
    parser.add_argument(
        '-e', '--enabled',
        action='store_true',
        help="Only match enabled objects."
    )

    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help="Output objects in Bloodhound-compatible JSON."
    )

    parser.add_argument(
        '-m', '--max-matches',
        type=int,
        default=0,
        help="Stop after a specified number of matches (default: 0)."
    )

    parser.add_argument(
        '-f', '--input-file',
        help='Read search terms from a file (use "-" for stdin).'
    )

    parser.add_argument(
        '-P', '--match-properties',
        metavar='PROPERTIES',
        help='Match objects using only specific properties (example: samaccountname,description).'
    )

    parser.add_argument(
        'query',
        metavar='query',
        help='The query to be performed.'
    )

    parser.add_argument(
        'search_terms',
        metavar='search-terms',
        nargs='*',
        help='The search terms for the query.'
    )

    args = parser.parse_args()

    if args.query not in AVAILABLE_QUERIES:
        parser.error(f'Invalid query: {args.query}')

    if args.search_terms and args.input_file:
        parser.error('Search terms must be given either via an input file or CLI arguments')

    if args.input_file and args.input_file != '-':
        if not (os.path.isfile(args.input_file) and os.access(args.input_file, os.R_OK)):
            parser.error(f'Cannot read search terms from file: {args.input_file}')

    if args.max_matches < 0:
        parser.error(f'Invalid value for `-m`: {args.max_matches}')

    if args.match_properties:
        match_properties = [mp.strip() for mp in args.match_properties.split(',')]

        allowed_properties = set(
            DomainUser.SEARCH_PROPERTIES + DomainComputer.SEARCH_PROPERTIES + \
            DomainGroup.SEARCH_PROPERTIES
        )

        for mp in match_properties:
            if mp not in allowed_properties:
                parser.error(f'Invalid Bloodhound property: {mp}')

    return args


def find_ad_objects(ad_objects, search_terms: list[str], enabled=False, max_matches=0):
    matches = 0

    if not search_terms:
        for ado in ad_objects:
            if enabled and not ado.enabled:
                continue

            yield ado

            if max_matches:
                matches += 1

                if matches > max_matches:
                    return
    else:
        for ado in ad_objects:
            if enabled and not ado.enabled:
                continue

            for st in search_terms:
                if st not in ado.search_string:
                    continue

                yield ado

                if max_matches:
                    matches += 1

                    if matches > max_matches:
                        return


def main():
    args = parse_args()

    match_properties = []

    if args.match_properties:
        match_properties = [mp.strip() for mp in args.match_properties.split(',')]

    search_terms = [st.lower() for st in args.search_terms]

    if args.input_file == '-':
        search_terms = [l.strip().lower() for l in sys.stdin.readlines()]
    elif args.input_file:
        with open(args.input_file, 'rt') as fo:
            search_terms = [l.strip().lower() for l in fo.readlines()]

    if args.query == 'list-users':
        dus = None

        if match_properties:
            dus = DomainUser.load_files(search_properties=match_properties)

        for u in find_ad_objects(dus or DomainUser.load_files(), search_terms, enabled=args.enabled,
                                 max_matches=args.max_matches):
            if args.enabled and not u.enabled:
                continue

            print(
                u.json if args.json else u.sam_account_name if u.sam_account_name else u.object_id
            )

        sys.exit(0)

    if args.query == 'list-computers':
        dcs = None

        if match_properties:
            dcs = DomainComputer.load_files(search_properties=match_properties)

        for c in find_ad_objects(dcs or DomainComputer.load_files(), search_terms,
                                 enabled=args.enabled, max_matches=args.max_matches):
            if args.enabled and not c.enabled:
                continue

            print(
                c.json if args.json else c.sam_account_name if c.sam_account_name else c.object_id
            )

        sys.exit(0)

    if args.query == 'list-groups':
        dgs = None

        if match_properties:
            dgs = DomainGroup.load_files(search_properties=match_properties)

        for g in find_ad_objects(dgs or DomainGroup.load_files(), search_terms,
                                 max_matches=args.max_matches):
            print(
                g.json if args.json else g.sam_account_name if g.sam_account_name else g.object_id
            )

        sys.exit(0)

    if args.query == 'describe-users':
        dus = None

        if match_properties:
            dus = DomainUser.load_files(search_properties=match_properties)

        for u in find_ad_objects(dus or DomainUser.load_files(), search_terms,
                                 enabled=args.enabled, max_matches=args.max_matches):
            print(u.json if args.json else f'\n{u}')

        sys.exit(0)

    if args.query == 'describe-computers':
        dcs = None

        if match_properties:
            dcs = DomainComputer.load_files(search_properties=match_properties)

        for c in find_ad_objects(dcs or DomainComputer.load_files(), search_terms,
                                 enabled=args.enabled, max_matches=args.max_matches):
            print(c.json if args.json else f'\n{c}')

        sys.exit(0)

    if args.query == 'describe-groups':
        dgs = None

        if match_properties:
            dgs = DomainGroup.load_files(search_properties=match_properties)

        for g in find_ad_objects(dgs or DomainGroup.load_files(), search_terms,
                                 max_matches=args.max_matches):
            print(g.json if args.json else f'\n{g}')

        sys.exit(0)

    if args.query == 'list-members':
        dgs = None

        if match_properties:
            dgs = DomainGroup.load_files(search_properties=match_properties)

        for g in find_ad_objects(DomainGroup.load_files(), search_terms,
                                 max_matches=args.max_matches):
            for u in DomainUser.load_files():
                if args.enabled and not u.enabled:
                    continue

                if g.contains(u.object_id):
                    print(
                        u.json if args.json else \
                        u.sam_account_name if u.sam_account_name else u.object_id
                    )

            for c in DomainComputer.load_files():
                if args.enabled and not c.enabled:
                    continue

                if g.contains(c.object_id):
                    print(
                        c.json if args.json else \
                        c.sam_account_name if c.sam_account_name else c.object_id
                    )

        sys.exit(0)

    if args.query == 'list-user-memberships':
        dus = None

        if match_properties:
            dus = DomainUser.load_files(search_properties=match_properties)

        for u in find_ad_objects(dus or DomainUser.load_files(), search_terms,
                                 enabled=args.enabled, max_matches=args.max_matches):
            for g in DomainGroup.load_files():
                if g.contains(u.object_id):
                    print(
                        g.json if args.json else \
                        g.sam_account_name if g.sam_account_name else g.object_id
                    )

        sys.exit(0)

    if args.query == 'list-computer-memberships':
        dcs = None

        if match_properties:
            dcs = DomainComputer.load_files(search_properties=match_properties)

        for c in find_ad_objects(dcs or DomainComputer.load_files(), search_terms,
                                 enabled=args.enabled, max_matches=args.max_matches):
            for g in DomainGroup.load_files():
                if g.contains(c.object_id):
                    print(
                        g.json if args.json else \
                        g.sam_account_name if g.sam_account_name else g.object_id
                    )

        sys.exit(0)

    if args.query == 'list-kerberoastable':
        dus = None

        if match_properties:
            dus = DomainUser.load_files(search_properties=match_properties)

        for u in find_ad_objects(DomainUser.load_files(), search_terms, enabled=args.enabled,
                                 max_matches=args.max_matches):
            if not u.spns:
                continue

            print(
                u.json if args.json else u.sam_account_name if u.sam_account_name else u.object_id
            )

        sys.exit(0)

    if args.query == 'list-asrep-roastable':
        dus = None

        if match_properties:
            dus = DomainUser.load_files(search_properties=match_properties)

        for u in find_ad_objects(dus or DomainUser.load_files(), search_terms,
                                 enabled=args.enabled, max_matches=args.max_matches):
            if not u.dont_req_preauth:
                continue

            print(
                u.json if args.json else u.sam_account_name if u.sam_account_name else u.object_id
            )

        sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'{type(e).__name__}: {e}')
        sys.exit(1)
