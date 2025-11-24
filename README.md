# shihtzu

`shihtzu` is a small CLI parser for Bloodhound-generated files. It will search for files matching `.*_(computers|groups|users)(_(0[1-9]|[1-9][0-9]))?\.json` in the current working directory and quickly provide information on Active Directory objects we generally rely on cumbersome `jq` queries to get.

## Help Banner

```
usage: shihtzu [-h] [-e] [-j] [-n MAX_MATCHES] [-f INPUT_FILE] [-m PROPERTIES] query [search-terms ...]

A small CLI parser for Bloodhound-generated files.

positional arguments:
  query                 The query to be performed.
  search-terms          The search terms for the query.

options:
  -h, --help            show this help message and exit
  -e, --enabled         Only match enabled objects.
  -j, --json            Output objects in Bloodhound-compatible JSON.
  -n, --max-matches MAX_MATCHES
                        Stop after a specified number of matches (default: 0).
  -f, --input-file INPUT_FILE
                        Read search terms from a file (use "-" for stdin).
  -m, --match-properties PROPERTIES
                        Match objects using only specific properties (example: samaccountname,description).

Queries:
  list-users, lu                  list users
  list-computers, lc              list computers
  list-groups, lg                 list groups
  describe-users, du              show information on users
  describe-computers, dc          show information on computers
  describe-groups, dg             show information on groups
  list-group-members, lgm         list members of groups
  list-user-memberships, lum      list group memberships of users
  list-computer-memberships, lcm  list group memberships of computers
  list-kerberoastable, lk         list domain users with SPNs set
  list-asrep-roastable, la        list domain users that don't require Kerberos pre-authentication

Examples:
  > List all Active Directory users:
    shihtzu list-users
  > List the first user whose samaccountname property matches "elliot.alderson":
    shihtzu -n 1 -m samaccountname du elliot.alderson
  > Dump the full Bloodhound JSON for enabled users that are members of the group "Domain Admins":
    shihtzu -ej list-group-members "Domain Admins"
  > Describe the groups of which users matching "alderson" are members:
    shihtzu list-user-memberships alderson | shihtzu -f - describe-groups
```
