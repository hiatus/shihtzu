# shihtzu

`shihtzu` is a small CLI parser for Bloodhound-generated files. It will search for files matching `.*_(computers|groups|users)(_(0[1-9]|[1-9][0-9]))?\.json` in the current working directory and quickly provide information on Active Directory objects we generally rely on cumbersome `jq` queries to get.

## Queries
- `list-users`
- `list-computers`
- `list-groups`
- `describe-users`
- `describe-computers`
- `describe-groups`
- `list-user-memberships`
- `list-computer-memberships`
- `list-group-members`
- `list-kerberoastable`
- `list-asrep-roastable`
