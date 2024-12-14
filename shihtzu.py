#!/usr/bin/env python3

import sys

# Local imports
from core.bloodhound import *


BANNER = '''\
shihtzu [command] [term]?
    list-users             [filter-term]?          list all Active Directory users
    list-computers         [filter-term]?          list all Active Directory computers
    list-groups            [filter-term]?          list all Active Directory groups
    list-enabled-users     [filter-term]?          list all enabled Active Directory users
    list-enabled-computers [filter-term]?          list all enabled Active Directory computers
    describe-user          [search-term]           show information on the first user matching [search-term]
    describe-users         [search-term]           show information on all users matching [search-term]
    describe-computer      [search-term]           show information on the first computer matching [search-term]
    describe-computers     [search-term]           show information on all computers matching [search-term]
    describe-group         [search-term]           show information on the first group matching [search-term]
    describe-groups        [search-term]           show information on all groups matching [search-term]
    list-user-groups       [user-search-term]      list group memberships of the first user matching [user-search-term]
    list-computer-groups   [computer-search-term]  list group memberships of the first computer matching [computer-search-term]
    list-group-members     [group-search-term]     list all members of the first group matching [group-search-term]
    list-kerberoastable    [filter-term]?          list all domain users with SPNs set
    list-asrep-roastable   [filter-term]?          list all domain users that don't require Kerberos pre-authentication

    - For convenience, search terms match object ids, samaccountnames, descriptions, SPNs, etc.
    - Listing prints `samaccountname`; if it's empty, it’s object ID will be printed instead.
'''


def find_ad_object(ad_objects, search_term: str):
    for ado in ad_objects:
        if search_term in ado.search_string:
            return ado


def find_ad_objects(ad_objects, search_term: str):
    for ado in ad_objects:
        if search_term in ado.search_string:
            yield ado


def main():
    if sys.argv[1] == 'list-users':
        if len(sys.argv) == 2:
            for u in DomainUser.load_files():
                print(u.sam_account_name if u.sam_account_name else u.object_id)

            sys.exit(0)

        search_term = sys.argv[2].lower()

        for u in DomainUser.load_files():
            if search_term in u.search_string:
                print(u.sam_account_name if u.sam_account_name else u.object_id)

        sys.exit(0)

    if sys.argv[1] == 'list-computers':
        if len(sys.argv) == 2:
            for c in DomainComputer.load_files():
                print(c.sam_account_name if c.sam_account_name else c.object_id)

            sys.exit(0)

        search_term = sys.argv[2].lower()

        for c in DomainComputer.load_files():
            if search_term in c.search_string:
                print(c.sam_account_name if c.sam_account_name else c.object_id)

        sys.exit(0)

    if sys.argv[1] == 'list-groups':
        if len(sys.argv) == 2:
            for g in DomainGroup.load_files():
                print(g.sam_account_name if g.sam_account_name else g.object_id)

            sys.exit(0)

        search_term = sys.argv[2].lower()

        for g in DomainGroup.load_files():
            if search_term in g.search_string:
                print(g.sam_account_name if g.sam_account_name else g.object_id)

        sys.exit(0)

    if sys.argv[1] == 'list-enabled-users':
        if len(sys.argv) == 2:
            for u in DomainUser.load_files():
                if not u.enabled:
                    continue

                print(u.sam_account_name if u.sam_account_name else u.object_id)

            sys.exit(0)

        search_term = sys.argv[2].lower()

        for u in DomainUser.load_files():
            if not u.enabled:
                continue

            if search_term in u.search_string:
                print(u.sam_account_name if u.sam_account_name else u.object_id)

        sys.exit(0)

    if sys.argv[1] == 'list-enabled-computers':
        if len(sys.argv) == 2:
            for c in DomainComputer.load_files():
                if not c.enabled:
                    continue

                print(c.sam_account_name if c.sam_account_name else c.object_id)

            sys.exit(0)

        search_term = sys.argv[2].lower()

        for c in DomainComputer.load_files():
            if not c.enabled:
                continue

            if search_term in c.search_string:
                print(c.sam_account_name if c.sam_account_name else c.object_id)

        sys.exit(0)

    if sys.argv[1] == 'describe-user':
        if (user := find_ad_object(DomainUser.load_files(), sys.argv[2].lower())) is None:
            print('[!] User not found')
            sys.exit(1)

        print(user)
        sys.exit(0)

    if sys.argv[1] == 'describe-users':
        for u in find_ad_objects(DomainUser.load_files(), sys.argv[2].lower()):
            print(f'\n{u}')

        sys.exit(0)

    if sys.argv[1] == 'describe-computer':
        if (computer := find_ad_object(DomainComputer.load_files(), sys.argv[2].lower())) is None:
            print('[!] Computer not found')
            sys.exit(1)

        print(computer)
        sys.exit(0)

    if sys.argv[1] == 'describe-computers':
        for c in find_ad_objects(DomainComputer.load_files(), sys.argv[2].lower()):
            print(f'\n{c}')

        sys.exit(0)

    if sys.argv[1] == 'describe-group':
        if (group := find_ad_object(DomainGroup.load_files(), sys.argv[2].lower())) is None:
            print('[!] Group not found')
            sys.exit(1)

        print(group)
        sys.exit(0)

    if sys.argv[1] == 'describe-groups':
        for g in find_ad_objects(DomainGroup.load_files(), sys.argv[2].lower()):
            print(f'\n{g}')

        sys.exit(0)

    if sys.argv[1] == 'list-user-groups':
        if (user := find_ad_object(DomainUser.load_files(), sys.argv[2].lower())) is None:
            print('[!] User not found')
            sys.exit(1)

        for g in DomainGroup.load_files():
            if g.contains(user.object_id):
                print(g.sam_account_name if g.sam_account_name else g.object_id)

        sys.exit(0)

    if sys.argv[1] == 'list-computer-groups':
        if (computer := find_ad_object(DomainComputer.load_files(), sys.argv[2].lower())) is None:
            print('[!] User not found')
            sys.exit(1)

        for g in DomainGroup.load_files():
            if g.contains(computer.object_id):
                print(g.sam_account_name if g.sam_account_name else g.object_id)

        sys.exit(0)

    if sys.argv[1] == 'list-group-members':
        if (group := find_ad_object(DomainGroup.load_files(), sys.argv[2].lower())) is None:
            print('[!] Group not found')
            sys.exit(1)

        for u in DomainUser.load_files():
            if group.contains(u.object_id):
                print(u.sam_account_name if u.sam_account_name else u.object_id)

        for c in DomainComputer.load_files():
            if group.contains(c.object_id):
                print(c.sam_account_name if c.sam_account_name else c.object_id)

        sys.exit(0)

    if sys.argv[1] == 'list-kerberoastable':
        if len(sys.argv) == 2:
            for u in DomainUser.load_files():
                if not u.spns:
                    continue

                print(u.sam_account_name if u.sam_account_name else u.object_id)

            sys.exit(0)

        search_term = sys.argv[2].lower()

        for u in DomainUser.load_files():
            if not u.spns:
                continue

            if search_term in u.search_string and u.spns:
                print(u.sam_account_name if u.sam_account_name else u.object_id)

        sys.exit(0)

    if sys.argv[1] == 'list-asrep-roastable':
        if len(sys.argv) == 2:
            for u in DomainUser.load_files():
                if not u.dont_req_preauth:
                    continue

                print(u.sam_account_name if u.sam_account_name else u.object_id)

            sys.exit(0)

        search_term = sys.argv[2].lower()

        for u in DomainUser.load_files():
            if not u.dont_req_preauth:
                continue

            if search_term in u.search_string and u.spns:
                print(u.sam_account_name if u.sam_account_name else u.object_id)

        sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'{BANNER}\n\n{type(e).__name__}: {e}')
        sys.exit(1)
