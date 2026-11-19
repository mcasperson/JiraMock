# JiraMock

This is an AWS lambda that mocks just enough of the Jira API that Octopus can use it to extract issue details. Just configure Octopus to point to the function URL and any issues referenced in build information will return mock data.

## Run with Docker

The same handler is also available as a standalone web server, published as a Docker image to GitHub Container Registry:

```
docker run --rm -p 8080:8080 ghcr.io/mcasperson/jiramock:latest
```

Then query it locally:

```
curl -X POST http://localhost:8080/rest/api/2/search -H "Content-Type: application/json" -d '{"jql":"id in (DEMO-1)", "fields": ["summary", "comment"]}'
```

Set the `PORT` environment variable to change the listening port (default `8080`), e.g. `docker run --rm -e PORT=9000 -p 9000:9000 ghcr.io/mcasperson/jiramock:latest`.

To build the image yourself:

```
docker build -t jiramock .
docker run --rm -p 8080:8080 jiramock
```

## Push build information to Octopus

```
octo build-information --package-id=octopussolutionsengineering/octopub-selfcontained --version=0.3.113 --file=buildinfo.json --overwrite-mode=OverwriteExisting --space MySpace
```