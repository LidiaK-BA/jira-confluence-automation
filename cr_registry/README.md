# CR registry list

The `list` command reads confirmed CRs from `cr-registry/registry.csv` and writes
matching rows as CSV to standard output. Filters can be combined; records must
match every supplied filter. Results stay in registry order, drafts are
excluded, and the `cost` field is never included in the output.

```powershell
python -m cr_registry list
python -m cr_registry list --sub-project "Sub-project A" --status Dev
python -m cr_registry list --priority High --owner "Alex Smith"
```

Set the configured project names in `cr-registry/config.json` before using the
`--sub-project` filter. The names are intentionally unpopulated until the
project's open question about sub-projects is resolved. Status and priority
filters accept the values defined in the technical specification. Invalid
filters are reported on standard error and exit with status 2.

For other registry or config paths, use `--registry` and `--config`.
