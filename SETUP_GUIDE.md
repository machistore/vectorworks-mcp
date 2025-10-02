# Vectorworks RAG + MCP セットアップ手順書

このドキュメントは、Windows 11環境でVectorworks RAG + MCPシステムをセットアップし、VS Codeに統合するための詳細な手順を記載しています。

## 目次

1. [概要](#概要)
2. [前提条件](#前提条件)
3. [システムのセットアップ](#システムのセットアップ)
4. [VS CodeへのMCP統合](#vs-codeへのmcp統合)
5. [動作確認](#動作確認)
6. [トラブルシューティング](#トラブルシューティング)
7. [使用方法](#使用方法)

---

## 概要

### このシステムができること

- **Vectorworksドキュメントの統合検索**: Python/VectorScriptのドキュメントをローカルに保存し、FAISSベクトル検索で横断的に検索
- **Web UIでの検索**: ブラウザから簡単にドキュメントを検索・参照
- **MCP（Model Context Protocol）連携**: VS CodeのClaude Devから直接ドキュメントを検索し、AIが回答を生成

### アーキテクチャ

```
┌─────────────┐     MCP Protocol      ┌──────────────┐
│  VS Code    │◄─────(stdio)─────────►│ MCP Bridge   │
│ (Claude Dev)│                        │ (Node.js)    │
└─────────────┘                        └──────────────┘
                                              │
                                              │ WebSocket
                                              ▼
                                       ┌──────────────┐
                                       │ MCP Server   │
                                       │ (FastAPI)    │
                                       └──────────────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │ FAISS Index  │
                                       │ + Metadata   │
                                       └──────────────┘
```

---

## 前提条件

### 必須環境

- **OS**: Windows 11
- **Docker Desktop**: インストール済み・起動中
- **VS Code**: インストール済み
- **Claude Dev拡張機能**: VS Codeにインストール済み
- **Node.js**: インストール済み（npm含む）
- **Git**: インストール済み（リポジトリのクローンに使用）
- **GitHubアカウント**: プロジェクトのフォークに必要

### プロジェクトの取得

このセットアップは、以下の手順でGitHubからプロジェクトを取得していることを前提としています。

#### ステップ0-1: GitHubでプロジェクトをフォーク

1. 元のプロジェクトにアクセス: https://github.com/togawamanabu/vectorworks-mcp
2. 画面右上の **Fork** ボタンをクリック
3. 自分のGitHubアカウントにリポジトリがフォークされます
4. フォーク先URL例: `https://github.com/<あなたのユーザー名>/vectorworks-mcp`

#### ステップ0-2: フォークしたプロジェクトをローカルにクローン

```bash
# 作業ディレクトリに移動（例）
cd C:\Users\<ユーザー名>\Documents\works\flowworks

# 自分のフォークをクローン（<あなたのユーザー名>を実際のユーザー名に置き換えてください）
git clone https://github.com/<あなたのユーザー名>/vectorworks-mcp.git

# クローンしたディレクトリに移動
cd vectorworks-mcp\vectorworks-mcp
```

**このドキュメントの手順は、上記でクローンしたローカルディレクトリで実行することを想定しています。**

### 環境確認

以下のコマンドで環境を確認してください：

```bash
# Dockerのバージョン確認
docker --version
# 出力例: Docker version 28.4.0, build d8eb465

# Docker Composeのバージョン確認
docker compose version
# 出力例: Docker Compose version v2.39.4-desktop.1

# Node.jsのバージョン確認
node --version
# 出力例: v18.x.x 以上推奨

# npmのバージョン確認
npm --version
# 出力例: v9.x.x 以上推奨

# Gitのバージョン確認
git --version
# 出力例: git version 2.x.x 以上推奨
```

---

## システムのセットアップ

### ステップ1: Dockerイメージのビルド

プロジェクトディレクトリに移動し、Dockerイメージをビルドします。

```bash
cd C:\Users\<ユーザー名>\Documents\works\flowworks\vectorworks-mcp\vectorworks-mcp

# Dockerイメージをビルド（初回は10分程度かかります）
docker compose build
```

**成功時の出力例**:
```
✓ vectorworks-mcp-app  Built
```

### ステップ2: ドキュメントの取得

#### 2-1. 最小限のドキュメント取得（基本）

```bash
# 基本的なVectorworksドキュメントを取得
docker compose run --rm app bash scripts/fetch_docs_minimal.sh
```

**取得されるドキュメント**:
- App Help: Scripting基本ページ（2022/2023/2024）
- 日本語サイト: VectorScript関数索引
- Developer Wiki: VS Function Reference

#### 2-2. GitHubリポジトリの取得（推奨）

```bash
# VectorworksのGitHubリポジトリをクローン
docker compose run --rm app bash scripts/fetch_github_vectorworks.sh
```

**取得されるリポジトリ**:
- `Vectorworks/developer-scripting`
- `Vectorworks/developer-sdk`
- `Vectorworks/developer-worksheets`

**成功時の出力例**:
```
[info] Syncing 3 repositories
[clone] Vectorworks/developer-scripting -> /app/data/github/vectorworks/developer-scripting
[clone] Vectorworks/developer-sdk -> /app/data/github/vectorworks/developer-sdk
[clone] Vectorworks/developer-worksheets -> /app/data/github/vectorworks/developer-worksheets
[done] Repositories synced under: /app/data/github/vectorworks
```

### ステップ3: ベクトルインデックスの生成

ドキュメントをベクトル化し、FAISS検索インデックスを作成します。

```bash
# ベクトルインデックスを生成（初回は埋め込みモデルのダウンロードで5-10分程度）
docker compose run --rm app python -m app.indexer
```

**成功時の出力例**:
```
Indexed 3956 chunks → /app/index/vw.faiss
```

**生成されるファイル**:
- `index/vw.faiss` - FAISSインデックス
- `index/meta.jsonl` - メタデータ（ドキュメントID、チャンクIDなど）

### ステップ4: システムの起動

```bash
# システムをバックグラウンドで起動
docker compose up -d

# コンテナの状態確認
docker compose ps
```

**成功時の出力例**:
```
NAME                    STATUS          PORTS
vectorworks-mcp-app-1   Up 10 seconds   0.0.0.0:8765->8765/tcp, 0.0.0.0:8001->8000/tcp
```

**アクセスURL**:
- **Web UI**: http://localhost:8001
- **MCP Server (WebSocket)**: ws://localhost:8765

---

## VS CodeへのMCP統合

### ステップ5: MCPブリッジのセットアップ

#### 5-1. package.jsonの作成

プロジェクトディレクトリに`package.json`を作成します（既に作成済みの場合はスキップ）。

**ファイルパス**: `C:\Users\<ユーザー名>\Documents\works\flowworks\vectorworks-mcp\vectorworks-mcp\package.json`

```json
{
  "name": "vectorworks-mcp-bridge",
  "version": "1.0.0",
  "description": "MCP bridge for Vectorworks documentation RAG system",
  "main": "mcp-bridge.js",
  "scripts": {
    "start": "node mcp-bridge.js"
  },
  "dependencies": {
    "ws": "^8.18.0"
  }
}
```

#### 5-2. Node.js依存関係のインストール

```bash
# WebSocketモジュールをインストール
npm install
```

**成功時の出力例**:
```
added 1 package, and audited 2 packages in 1s
found 0 vulnerabilities
```

#### 5-3. MCPブリッジスクリプトの作成

**ファイルパス**: `C:\Users\<ユーザー名>\Documents\works\flowworks\vectorworks-mcp\vectorworks-mcp\mcp-bridge.js`

このファイルは既に作成されています。MCPブリッジは以下の役割を果たします：

- VS Code（stdio）とWebSocketサーバー間の通信を橋渡し
- MCP標準プロトコル（initialize、tools/list、tools/call）を実装
- ツール呼び出しを内部WebSocketメソッドに変換

### ステップ6: Claude Dev MCP設定の追加

#### 6-1. MCP設定ファイルの編集

**ファイルパス**: `C:\Users\<ユーザー名>\AppData\Roaming\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

このファイルに以下の内容を設定します（既に設定済み）：

```json
{
  "mcpServers": {
    "vectorworks-docs": {
      "command": "node",
      "args": [
        "C:\\Users\\<ユーザー名>\\Documents\\works\\flowworks\\vectorworks-mcp\\vectorworks-mcp\\mcp-bridge.js"
      ],
      "disabled": false
    }
  }
}
```

**設定内容の説明**:
- `mcpServers`: MCPサーバーの定義
- `vectorworks-docs`: サーバー名（Claude Devで表示される）
- `command`: 実行コマンド（Node.js）
- `args`: MCPブリッジスクリプトのフルパス
- `disabled`: false（有効化）

### ステップ7: VS Codeの再起動

**重要**: MCPサーバーを有効化するには、VS Codeの完全な再起動が必要です。

1. **すべてのVS Codeウィンドウを閉じる**
2. **VS Codeを再起動**
3. Claude Dev拡張機能が自動的にMCPサーバーに接続

---

## 動作確認

### Web UIでの確認

ブラウザで以下にアクセスし、検索機能をテストします：

**URL**: http://localhost:8001

**検索例**:
- キーワード: `PushAttrs`
- キーワード: `VectorScript`
- キーワード: `record format`

### MCPツールの確認（VS Code）

VS Code再起動後、Claude Devで以下のように質問してください：

```
VectorScriptのPushAttrs関数について教えてください
```

Claudeが自動的に`vw_search`または`vw_answer`ツールを使用して、Vectorworksドキュメントから情報を取得して回答します。

### 利用可能なMCPツール

Claude Devから利用できるツール：

#### 1. **vw_search**
- **説明**: Vectorworksドキュメントを検索
- **パラメータ**:
  - `query` (string, 必須): 検索クエリ
  - `k` (number, オプション): 結果数（デフォルト: 6）
- **戻り値**: 関連ドキュメントチャンクのリスト

**使用例**:
```
PushAttrs関数について調べてください
```

#### 2. **vw_answer**
- **説明**: Vectorworksスクリプトに関する質問に回答（出典付き）
- **パラメータ**:
  - `query` (string, 必須): 質問
  - `k` (number, オプション): 参照ドキュメント数（デフォルト: 6）
- **戻り値**: ドラフト回答と出典

**使用例**:
```
record formatの使い方を教えてください
```

#### 3. **vw_get**
- **説明**: 特定のドキュメントチャンクを取得
- **パラメータ**:
  - `doc_id` (string, 必須): ドキュメントID
  - `chunk_id` (number, 必須): チャンクID
- **戻り値**: ドキュメントチャンクの内容

---

## トラブルシューティング

### 問題1: Dockerコンテナが起動しない

**確認事項**:
```bash
# Docker Desktopが起動しているか確認
docker info

# コンテナのログを確認
docker compose logs app
```

**対処法**:
- Docker Desktopを起動
- ポート競合を確認（8001、8765が使用中でないか）

### 問題2: MCPサーバーが認識されない

**確認事項**:
```bash
# Dockerコンテナが起動しているか確認
docker compose ps

# MCPサーバーが動作しているか確認
curl http://localhost:8001
```

**対処法**:
1. システムが起動しているか確認: `docker compose up -d`
2. VS Codeを完全に再起動
3. VS Code開発者コンソールでエラー確認: `Ctrl+Shift+I`

### 問題3: ドキュメントが検索できない

**確認事項**:
```bash
# インデックスが生成されているか確認
ls -la index/

# インデックスを再生成
docker compose run --rm app python -m app.indexer --rebuild
```

### 問題4: Web UIは動作するがMCPが動作しない

**確認事項**:
1. `mcp-bridge.js`のパスが正しいか確認
2. Node.js依存関係がインストールされているか確認: `npm list`
3. MCPブリッジを手動で起動してエラーを確認:
   ```bash
   node mcp-bridge.js
   ```

---

## 使用方法

### 日常的な使用

#### システムの起動

```bash
# システムを起動
docker compose up -d

# 起動確認
docker compose ps
```

#### システムの停止

```bash
# システムを停止
docker compose down
```

#### ドキュメントの更新

ドキュメントを追加・更新した場合：

```bash
# ドキュメントを再取得
docker compose run --rm app bash scripts/fetch_github_vectorworks.sh

# インデックスを再生成
docker compose run --rm app python -m app.indexer --rebuild

# システムを再起動
docker compose restart
```

### APIを直接使用

#### 検索API

```bash
# 検索（6件取得）
curl -s "http://localhost:8001/search?q=PushAttrs&k=6" | jq .

# 結果例:
# {
#   "results": [
#     {
#       "doc_id": "data/vw-app-help/VW2022_Scripting.htm",
#       "chunk_id": 0,
#       "score": 0.85,
#       "text": "PushAttrs() function description..."
#     }
#   ]
# }
```

#### 質問応答API

```bash
# 質問
curl -s "http://localhost:8001/answer?q=record+formatの使い方" | jq .

# 結果例:
# {
#   "answer": "record formatは...",
#   "sources": [...]
# }
```

#### ドキュメント取得API

```bash
# 特定チャンク取得
curl -s "http://localhost:8001/get?doc_id=data/vw-app-help/VW2022_Scripting.htm&chunk_id=0" | jq .
```

---

## システム構成

### ディレクトリ構成

```
vectorworks-mcp/
├── app/                      # アプリケーション本体
│   ├── api.py               # FastAPI アプリ
│   ├── mcp_server.py        # MCP WebSocketサーバー
│   ├── indexer.py           # ドキュメント取込・ベクター化
│   ├── search.py            # 検索・回答ロジック
│   ├── chunking.py          # チャンク分割
│   └── ...
├── scripts/                  # スクリプト
│   ├── fetch_docs_minimal.sh       # 最小限ドキュメント取得
│   └── fetch_github_vectorworks.sh # GitHubリポジトリ取得
├── templates/                # Web UIテンプレート
├── data/                     # ドキュメント保存先
│   ├── vw-app-help/         # App Help
│   ├── vw-jp-ref/           # 日本語リファレンス
│   ├── vw-devwiki/          # Developer Wiki
│   └── github/vectorworks/  # GitHubリポジトリ
├── index/                    # 検索インデックス
│   ├── vw.faiss             # FAISSインデックス
│   └── meta.jsonl           # メタデータ
├── mcp-bridge.js            # MCPブリッジスクリプト
├── package.json             # Node.js設定
├── Dockerfile               # Dockerイメージ定義
├── docker-compose.yml       # Docker Compose設定
├── requirements.txt         # Python依存関係
└── README.md                # プロジェクト説明
```

### 環境変数（任意カスタマイズ）

`docker-compose.yml`または環境変数で設定可能：

```yaml
environment:
  - DATA_DIR=/app/data              # データディレクトリ
  - INDEX_DIR=/app/index            # インデックスディレクトリ
  - EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2  # 埋め込みモデル
  - CHUNK_CHARS=2800                # チャンク文字数
  - CHUNK_OVERLAP=480               # オーバーラップ文字数
  - API_HOST=0.0.0.0
  - API_PORT=8000
  - MCP_HOST=0.0.0.0
  - MCP_PORT=8765
```

---

## セットアップ完了確認チェックリスト

- [ ] Dockerイメージがビルドされている
- [ ] ドキュメントが取得されている（`data/`配下）
- [ ] ベクトルインデックスが生成されている（`index/vw.faiss`）
- [ ] Dockerコンテナが起動している（`docker compose ps`で確認）
- [ ] Web UIにアクセスできる（http://localhost:8001）
- [ ] Node.js依存関係がインストールされている（`node_modules/ws`）
- [ ] MCPブリッジスクリプトが作成されている（`mcp-bridge.js`）
- [ ] Claude Dev MCP設定が追加されている（`cline_mcp_settings.json`）
- [ ] VS Codeを再起動している
- [ ] Claude DevからMCPツールが利用できる

---

## 参考情報

### システム要件

- **ディスク容量**: 約3GB（ドキュメント + モデル + インデックス）
- **メモリ**: 最低4GB推奨（Docker含む）
- **ネットワーク**: 初回セットアップ時にインターネット接続が必要

### パフォーマンス

- **インデックス作成時間**: 初回5-10分（埋め込みモデルダウンロード含む）
- **検索速度**: 1クエリあたり100-500ms
- **インデックスサイズ**: 約3956チャンク（ドキュメント量により変動）

### ライセンス・注意事項

- このシステムはドキュメントを含みません
- 各自の利用規約・著作権に従ってドキュメントを配置してください
- `answer` APIは抜粋ベースの簡易ドラフトです。最終判断は原文を確認してください

---

## サポート

### 問題が解決しない場合

1. プロジェクトのREADME.mdを確認
2. Dockerログを確認: `docker compose logs app`
3. GitHubリポジトリのIssuesを確認

### セットアップ日時

- **セットアップ実施日**: 2025年10月2日
- **環境**: Windows 11, Docker 28.4.0, Docker Compose v2.39.4
- **インデックスチャンク数**: 3956

---

**セットアップ完了おめでとうございます！**

VS Codeを再起動して、Claude DevからVectorworksドキュメントを検索してみてください。
