# JiraMock

This is an AWS lambda that mocks just enough of the Jira API that Octopus can use it to extract issue details. Just configure Octopus to point to the function URL and any issues referenced in build information will return mock data.

## Example

```
curl -X POST https://s6dstgcfnk6h6rmcbk3uqqmkte0nvnee.lambda-url.ap-southeast-2.on.aws/rest/api/2/search -H "Content-Type: application/json" -d '{"jql":"id in (DEMO-1)", "fields": ["summary", "comment"]}'
```

## Push build information to Octopus

```
octo build-information --package-id=octopussolutionsengineering/octopub-selfcontained --version=0.3.113 --file=buildinfo.json --overwrite-mode=OverwriteExisting --space MySpace
```