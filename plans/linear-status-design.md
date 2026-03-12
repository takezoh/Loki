# Linear ステータス設計 & AI エージェントワークフロー

## ワークフロー概要

```
1. 人間が親 Issue を作成（Backlog）
        ↓ Issue Status を Planning に変更
2. エージェントが Issue を MCP で取得・分析
3. エージェントが Sub-issue を作成（計画立案）
4. エージェントが Status を Pending Approval に変更
        ↓ Slack 通知 → 人間が計画を確認
5. 人間が Status を Implementing に変更（承認）
        ↓
6. エージェントが Sub-issue を順次実装・PR 作成
7. エージェントが Status を In Review に変更
        ↓ Slack 通知 → 人間が PR をレビュー・マージ
8. 人間が Status を Done に変更
        ↓
9. 全 Sub-issue が Done → 親 Issue も自動 Done
```

---

## Issue Status 設計

Team 単位でカスタマイズ（Settings → Teams → Issue statuses & automations）

| Status | カテゴリ | 担当 | 意味 |
|--------|---------|------|------|
| `Backlog` | Backlog | 人間 | 未着手・積み残し |
| `Planning` | Started | エージェント | Sub-issue 立案中 |
| `Pending Approval` | Started | 人間 | 計画承認待ち |
| `Implementing` | Started | エージェント | 実装中 |
| `In Review` | Started | 人間 | PR レビュー中 |
| `Done` | Completed | 自動 | 完了 |
| `Cancelled` | Cancelled | 人間 | 中止 |

```
Backlog → Planning → Pending Approval → Implementing → In Review → Done
                                                                  ↘ Cancelled
```

---

## Project Status 設計

ロードマップ・進捗の大枠を人間が管理する。エージェントは操作しない。

| Status | 意味 |
|--------|------|
| `Planned` | 計画済み・未着手 |
| `In Progress` | 配下の Issue が進行中 |
| `Completed` | 全 Issue 完了 |
| `Cancelled` | 中止 |

```
Planned → In Progress → Completed
        ↘ Cancelled
```

---

## 役割の分離

| レイヤー | 用途 | 操作者 |
|---------|------|--------|
| Project Status | ロードマップ・進捗の大枠 | 人間 |
| Issue Status | エージェントと人間の作業フロー | エージェント + 人間 |
| Sub-issue | 実装タスクの細分化 | エージェント |
| Label | 性質の分類（repo:xxx, Bug, Feature など） | エージェント + 人間 |

---

## Webhook トリガー設計

| Issue Status 変化 | 検知 | アクション |
|------------------|------|-----------|
| `Backlog` → `Planning` | Webhook | エージェントが計画開始 |
| `Planning` → `Pending Approval` | Webhook | 人間に Slack 通知 |
| `Pending Approval` → `Implementing` | Webhook | エージェントが実装開始 |
| `Implementing` → `In Review` | Webhook | 人間に Slack 通知 |

---

## Sub-issue 自動化設定

Settings → Teams → Workflow で以下を有効化する。

- **全 Sub-issue が Done になったら親 Issue も自動 Done**
- **親 Issue が Cancelled になったら全 Sub-issue も自動 Cancelled**
