#!/usr/bin/env python3
"""Linear ポーリング: 指定ステータスの Issue を JSON 配列で出力する。"""

import json
import os
import sys
import urllib.request

def load_env():
    env = {}
    conf = os.path.join(os.path.dirname(__file__), "..", "config", "forge.env")
    with open(conf) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            k, _, v = line.partition("=")
            env[k] = v.strip('"').strip("'")
    return env

def graphql(api_key: str, query: str, variables: dict = None) -> dict:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=payload,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

ISSUES_QUERY = """
query($teamId: ID!, $stateName: String!) {
  issues(filter: {
    team: { id: { eq: $teamId } }
    state: { name: { eq: $stateName } }
  }) {
    nodes {
      id
      identifier
      title
      labels {
        nodes {
          name
          parent {
            name
          }
        }
      }
    }
  }
}
"""

def poll(status: str) -> list[dict]:
    env = load_env()
    api_key = env.get("LINEAR_API_KEY") or os.environ.get("LINEAR_API_KEY", "")
    if not api_key:
        print("LINEAR_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    team_id = env["FORGE_TEAM_ID"]
    data = graphql(api_key, ISSUES_QUERY, {"teamId": team_id, "stateName": status})

    issues = []
    for node in data.get("data", {}).get("issues", {}).get("nodes", []):
        labels = []
        for label in node.get("labels", {}).get("nodes", []):
            parent = label.get("parent")
            name = label["name"]
            labels.append(f"{parent['name']}:{name}" if parent else name)
        issues.append({
            "id": node["id"],
            "identifier": node["identifier"],
            "title": node["title"],
            "labels": labels,
        })
    return issues

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: poll.py <status_name>", file=sys.stderr)
        sys.exit(1)
    issues = poll(sys.argv[1])
    print(json.dumps(issues))
