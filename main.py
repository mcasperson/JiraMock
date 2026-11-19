import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def lambda_handler(event, context):
    """AWS Lambda entry point (API Gateway / function URL payload format 2.0)."""
    return handle_request(event)


def handle_request(event):
    """Shared handler used by both the Lambda entry point and the standalone server."""
    print(json.dumps(event))

    if event.get('rawPath') == '/rest/api/2/myself':
        return {
            'statusCode': 200,
            'body': 'ok'
        }

    # Check if the path matches
    if event.get('rawPath') != '/rest/api/2/search':
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'})
        }

    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON'})
        }

    # Extract JQL and fields
    jql = body.get('jql', '')
    fields = body.get('fields', [])
    max_results = int(body.get('maxResults', 100))

    # Extract IDs from JQL
    # Expected format: "id in Demo-1,Demo-2"
    id_pattern = r'id\s+in\s+\(([\w\-,\s]+)\)'
    match = re.search(id_pattern, jql)

    if not match:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JQL format'})
        }

    # Get the comma-separated IDs
    issue_keys = [key.strip() for key in match.group(1).split(',')]

    # Create response
    issues = []
    for i, key in enumerate(issue_keys):
        issue_id = str(10000 + i)

        # Create fields object with requested fields
        issue_fields = {}
        if 'summary' in fields:
            summaries = [
                "Some bug that needs fixing",
                "Another random bug description",
                "Critical issue in production",
                "Feature request for dashboard",
                "UI enhancement needed"
            ]
            issue_fields['summary'] = summaries[i % len(summaries)]

        if 'comment' in fields:
            issue_fields['comment'] = {
                "comments": [],
                "self": f"https://example.atlassian.net/rest/api/{i}/issue/{issue_id}/comment",
                "maxResults": 0,
                "total": 0,
                "startAt": 0
            }

        issues.append({
            "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields",
            "id": issue_id,
            "self": f"https://example.atlassian.net/rest/api/{i}/issue/{issue_id}",
            "key": key,
            "fields": issue_fields
        })

    response = {
        "expand": "names,schema",
        "startAt": 0,
        "maxResults": max_results,
        "total": len(issues),
        "issues": issues
    }

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(response)
    }


class RequestHandler(BaseHTTPRequestHandler):
    """Adapts HTTP requests into Lambda-style events and calls handle_request."""

    def _handle(self):
        length = int(self.headers.get('Content-Length') or 0)
        raw_body = self._read_body(length)
        event = {
            'rawPath': self.path.split('?', 1)[0],
            'rawQueryString': self.path.split('?', 1)[1] if '?' in self.path else '',
            'headers': {k.lower(): v for k, v in self.headers.items()},
            'requestContext': {'http': {'method': self.command}},
            'body': raw_body or '{}',
        }
        result = handle_request(event)

        payload = (result.get('body') or '').encode('utf-8')
        self.send_response(result.get('statusCode', 200))
        for name, value in (result.get('headers') or {}).items():
            self.send_header(name, value)
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _read_body(self, length):
        return self.rfile.read(length).decode('utf-8') if length else ''

    do_GET = do_POST = _handle

    def log_message(self, format, *args):
        pass  # handle_request already logs each event


def run_server(host='0.0.0.0', port=8080):
    server = ThreadingHTTPServer((host, port), RequestHandler)
    print(f'Listening on http://{host}:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    run_server(port=int(os.environ.get('PORT', 8080)))