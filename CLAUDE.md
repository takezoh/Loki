# forge

Linear 駆動 AI エージェント。Issue のステータス変更をトリガーに計画立案と実装を自動実行する。

## 構成

- `bin/forge.sh` — cron エントリポイント。ポーリング → Issue 振り分け → バックグラウンド実行
- `bin/poll.sh` — claude CLI + Linear MCP で指定ステータスの Issue を JSON 取得
- `bin/run-claude.sh` — Issue 単位で claude CLI を実行（planning / implementing）
- `prompts/` — 各フェーズのプロンプトテンプレート
- `config/forge.env` — 設定値
- `config/repos.conf` — Label → リポジトリパスのマッピング

## フロー

1. Planning: 親 Issue → コード調査 → Sub-issue 分割 → Pending Approval
2. Implementing: Sub-issue → worktree → 実装 → PR → In Review
