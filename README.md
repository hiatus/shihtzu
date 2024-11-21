# shihtzu

`shihtzu` is a small CLI parser for Bloodhound-generated files. It will search for files matching `[0-9]{14}_(computers|groups|users)(_(0[1-9]|[1-9][0-9]))?\.json` in the current working directory and quickly provide information on Active Directory objects we generally rely on cumbersome `jq` queries to get.

## Queries
- `list-users`
- `list-computers`
- `list-groups`
- `describe-user`
- `describe-computer`
- `describe-group`
- `list-user-groups`
- `list-computer-groups`
- `list-group-members`
- `list-kerberoastable`
