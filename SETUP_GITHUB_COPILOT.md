# GitHub Copilot用 Vectorworks RAG + MCP セットアップ手順書

このドキュメントは、Windows 11環境でVectorworks RAG + MCPシステムをセットアップし、**GitHub Copilot**に統合するための詳細な手順を記載しています。

> **注意**: このドキュメントはGitHub Copilot用です。Claude Dev用のセットアップは [SETUP_GUIDE.md](SETUP_GUIDE.md) を参照してください。

## 目次

1. [概要](#概要)
2. [前提条件](#前提条件)
3. [システムのセットアップ](#システムのセットアップ)
4. [GitHub CopilotへのMCP統合](#github-copilotへのmcp統合)
5. [動作確認](#動作確認)
6. [トラブルシューティング](#トラブルシューティング)
7. [使用方法](#使用方法)
8. [Claude Devとの併用](#claude-devとの併用)

---

## 概要

### このシステムができること

- **Vectorworksドキュメントの統合検索**: Python/VectorScriptのドキュメントをローカルに保存し、FAISSベクトル検索で横断的に検索
- **Web UIでの検索**: ブラウザから簡単にドキュメントを検索・参照
- **GitHub Copilot統合**: Copilot Chatから直接Vectorworksドキュメントを検索し、AIが回答を生成

### アーキテクチャ

```
┌─────────────────┐   MCP Protocol    ┌──────────────┐
│  VS Code        │◄────(stdio)──────►│ MCP Bridge   │
│ (GitHub Copilot)│                    │ (Node.js)    │
└─────────────────┘                    └──────────────┘
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

### GitHub CopilotのMCP対応状況

- **VS Code**: バージョン 1.102以降でMCP GA（Generally Available）
- **対応プラン**:
  - ✅ Copilot Free/Pro/Pro+ - 制限なし
  - ⚠️ Copilot Business/Enterprise - 管理者によるMCPポリシー有効化が必要
- **サーバータイプ**: ローカルMCPサーバー、リモートMCPサーバー両方対応

---

## 前提条件

### 必須環境

- **OS**: Windows 11
- **Docker Desktop**: インストール済み・起動中
- **VS Code**: バージョン 1.102以降（MCP対応版）
- **GitHub Copilot拡張機能**: VS Codeにインストール済み
- **GitHub Copilotサブスクリプション**: Free/Pro/Pro+/Business/Enterprise
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
cd C:\Users\<ユーザー名>\Documents\works

# 自分のフォークをクローン（<あなたのユーザー名>を実際のユーザー名に置き換えてください）
git clone https://github.com/<あなたのユーザー名>/vectorworks-mcp.git

# クローンしたディレクトリに移動
cd vectorworks-mcp\vectorworks-mcp
```

**このドキュメントの手順は、上記でクローンしたローカルディレクトリで実行することを想定しています。**

### 環境確認

以下のコマンドで環境を確認してください：

```bash
# VS Codeのバージョン確認（1.102以降が必要）
code --version

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

### GitHub Copilot拡張機能の確認

VS Codeで以下を確認してください：

1. 拡張機能パネルを開く（`Ctrl+Shift+X`）
2. "GitHub Copilot" で検索
3. インストール済みであることを確認
4. Copilot Chatアイコンがサイドバーに表示されていることを確認

---

## システムのセットアップ

### ステップ1: Dockerイメージのビルド

プロジェクトディレクトリに移動し、Dockerイメージをビルドします。

```bash
# プロジェクトディレクトリに移動（クローンしたディレクトリのパスに置き換えてください）
cd C:\Users\<ユーザー名>\Documents\works\vectorworks-mcp\vectorworks-mcp

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

**Web UIで動作確認**: ブラウザで http://localhost:8001 を開き、検索が動作することを確認してください。

---

## GitHub CopilotへのMCP統合

### ステップ5: MCPブリッジのセットアップ

#### 5-1. package.jsonの確認

プロジェクトディレクトリに`package.json`が存在することを確認します（既に作成済みの場合はスキップ）。

**ファイルパス**: `vectorworks-mcp/package.json`

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

#### 5-3. MCPブリッジスクリプトの確認

**ファイルパス**: `vectorworks-mcp/mcp-bridge.js`

このファイルは既に作成されています。MCPブリッジは以下の役割を果たします：

- VS Code（stdio）とWebSocketサーバー間の通信を橋渡し
- MCP標準プロトコル（initialize、tools/list、tools/call）を実装
- ツール呼び出しを内部WebSocketメソッドに変換

### ステップ6: GitHub Copilot MCP設定の追加

GitHub Copilotは2つの方法でMCPサーバーを設定できます。

#### 方法1: リポジトリ固有の設定（推奨）

プロジェクトディレクトリに `.vscode/mcp.json` を作成します。

**ファイルパス**: `vectorworks-mcp/.vscode/mcp.json`

```json
{
  "servers": {
    "vectorworks-docs": {
      "command": "node",
      "args": [
        "C:\\Users\\<ユーザー名>\\Documents\\works\\vectorworks-mcp\\vectorworks-mcp\\mcp-bridge.js"
      ]
    }
  }
}
```

**注意**: `args`のパスは**絶対パス**で、実際の環境に合わせて修正してください。

**手順**:

```bash
# .vscodeディレクトリを作成（存在しない場合）
mkdir -p .vscode

# mcp.jsonを作成（VS Codeやテキストエディタで作成）
# 上記のJSONをコピーして保存し、パスを修正してください
```

#### 方法2: VS Code個人設定（グローバル）

VS Codeの `settings.json` に追加することもできます。

**ファイルパス**: `C:\Users\<ユーザー名>\AppData\Roaming\Code\User\settings.json`

VS Codeで設定を開く：
1. `Ctrl+Shift+P` でコマンドパレットを開く
2. "Preferences: Open User Settings (JSON)" を選択
3. 以下を追加：

```json
{
  "github.copilot.chat.mcp.servers": {
    "vectorworks-docs": {
      "command": "node",
      "args": [
        "C:\\Users\\<ユーザー名>\\Documents\\works\\vectorworks-mcp\\vectorworks-mcp\\mcp-bridge.js"
      ]
    }
  }
}
```

**推奨**: リポジトリ固有の設定（方法1）の方が、プロジェクトごとに管理しやすいです。

### ステップ7: VS Codeの再起動

**重要**: MCPサーバーを有効化するには、VS Codeの完全な再起動が必要です。

1. **すべてのVS Codeウィンドウを閉じる**
2. **VS Codeを再起動**
3. GitHub Copilotが自動的にMCPサーバーに接続

---

## 動作確認

### Web UIでの確認

ブラウザで以下にアクセスし、検索機能をテストします：

**URL**: http://localhost:8001

**検索例**:
- キーワード: `PushAttrs`
- キーワード: `VectorScript`
- キーワード: `record format`

### GitHub Copilot ChatでのMCPツール確認

VS Code再起動後、Copilot Chatで以下のように質問してください：

#### 基本的な質問

```
@workspace VectorScriptのPushAttrs関数について教えてください
```

```
Vectorworksのrecord formatの使い方を調べてください
```

```
VectorScriptでオブジェクトの属性を操作する方法は？
```

#### MCPツールの動作確認

GitHub Copilotが以下のツールを利用していることを確認：

- `vw_search` - ドキュメント検索
- `vw_answer` - 質問応答（出典付き）
- `vw_get` - 特定チャンク取得

Copilot Chatの応答に「ツールを使用しました」や「vw_search」などの表示が出れば成功です。

### 利用可能なMCPツール

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

### 問題2: GitHub CopilotがMCPサーバーを認識しない

**確認事項**:

1. **VS Codeのバージョン確認**:
   ```bash
   code --version
   ```
   バージョン 1.102以降が必要です。

2. **Dockerコンテナが起動しているか確認**:
   ```bash
   docker compose ps
   ```

3. **MCPサーバーが動作しているか確認**:
   ```bash
   curl http://localhost:8001
   ```

4. **mcp.jsonのパスが正しいか確認**:
   - `.vscode/mcp.json` の `args` に記載されたパスが正しいか確認
   - Windowsパスは `\\` でエスケープする必要があります

**対処法**:

1. システムが起動しているか確認: `docker compose up -d`
2. VS Codeを完全に再起動
3. VS Code開発者コンソールでエラー確認: `Ctrl+Shift+I`（Console タブ）
4. GitHub Copilot Output パネルでログ確認:
   - `Ctrl+Shift+P` → "Output: Show Output Channels" → "GitHub Copilot Chat" を選択

### 問題3: MCP設定が反映されない

**確認事項**:

```bash
# mcp.jsonファイルが存在するか確認
ls -la .vscode/mcp.json

# JSON構文が正しいか確認（JSONパーサーでチェック）
```

**対処法**:

1. `.vscode/mcp.json` のJSON構文を確認（カンマ、括弧など）
2. パスに日本語や特殊文字が含まれていないか確認
3. VS Codeでプロジェクトフォルダを開き直す
4. VS Codeを完全に再起動

### 問題4: MCPブリッジがWebSocketに接続できない

**確認事項**:

```bash
# MCPブリッジを手動で起動してエラーを確認
node mcp-bridge.js

# 出力例:
# [MCP Bridge] Connected to Vectorworks MCP server
```

**対処法**:

1. Dockerコンテナが起動していることを確認
2. ポート8765が使用可能か確認
3. `mcp-bridge.js` のWebSocket URL（`ws://localhost:8765`）を確認

### 問題5: ドキュメントが検索できない

**確認事項**:

```bash
# インデックスが生成されているか確認
ls -la index/

# 出力例:
# vw.faiss
# meta.jsonl
```

**対処法**:

```bash
# インデックスを再生成
docker compose run --rm app python -m app.indexer --rebuild
```

### 問題6: 組織/エンタープライズでMCPが無効

**Copilot Business/Enterpriseの場合**:

GitHub Copilot for Business/Enterpriseを使用している場合、組織管理者が「MCP servers in Copilot」ポリシーを有効化している必要があります。

**確認方法**:
1. 組織の管理者に連絡
2. GitHub Enterprise設定で "Policies for Copilot in your enterprise" を確認
3. "MCP servers in Copilot" が有効化されているか確認

**対処法**:
- 組織管理者にMCPポリシーの有効化を依頼
- または、個人のCopilot Pro/Pro+アカウントで使用

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

### GitHub Copilot Chatでの活用例

#### 例1: 関数の使い方を調べる

**プロンプト**:
```
@workspace VectorScriptのPushAttrs関数の使い方を教えてください。サンプルコードも含めてください。
```

**期待される動作**:
- Copilotが `vw_search` または `vw_answer` ツールを使用
- Vectorworksドキュメントから関連情報を取得
- 関数の説明とサンプルコードを提示

#### 例2: 特定の処理方法を質問

**プロンプト**:
```
Vectorworksでrecord formatを使ってカスタムデータを保存する方法を教えてください
```

**期待される動作**:
- `vw_answer` ツールで質問に回答
- 出典付きで詳細な手順を説明

#### 例3: エラーのトラブルシューティング

**プロンプト**:
```
VectorScriptで「Undefined symbol」エラーが出ました。どう対処すればいいですか？
```

**期待される動作**:
- ドキュメントから関連情報を検索
- エラーの原因と対処法を提示

#### 例4: コード作成時にドキュメント参照

**プロンプト**:
```
Vectorworksでレイヤーの表示/非表示を切り替えるスクリプトを作成してください。
関連するVectorScript関数を調べて使ってください。
```

**期待される動作**:
- `vw_search` でレイヤー操作関連の関数を検索
- 検索結果を元にスクリプトを作成
- 適切な関数（例: `SetObjectVariableBoolean`）を使用

### APIを直接使用（オプション）

GitHub Copilot以外でも、APIを直接使用できます。

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

---

## Claude Devとの併用

このシステムは、GitHub CopilotとClaude Devの**両方で同時に使用できます**。

### 設定ファイルの違い

| 項目 | Claude Dev | GitHub Copilot |
|------|------------|----------------|
| 設定ファイル | `cline_mcp_settings.json` | `.vscode/mcp.json` |
| 設定場所 | `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\` | プロジェクトルート `.vscode\` |
| フォーマット | `mcpServers` キー | `servers` キー |

### 両方で使用する方法

1. **Claude Devのセットアップ**: [SETUP_GUIDE.md](SETUP_GUIDE.md) を参照
2. **GitHub Copilotのセットアップ**: このドキュメントの手順を実行
3. **同じMCPブリッジを共有**: 両方とも `mcp-bridge.js` を使用

**メリット**:
- 用途に応じてClaude DevとGitHub Copilotを使い分け可能
- 同じドキュメントデータベースを共有
- 追加コストなし

---

## システム構成

### ディレクトリ構成

```
vectorworks-mcp/
├── .vscode/
│   └── mcp.json                # GitHub Copilot MCP設定
├── app/                         # アプリケーション本体
│   ├── api.py                  # FastAPI アプリ
│   ├── mcp_server.py           # MCP WebSocketサーバー
│   ├── indexer.py              # ドキュメント取込・ベクター化
│   ├── search.py               # 検索・回答ロジック
│   └── ...
├── scripts/                     # スクリプト
│   ├── fetch_docs_minimal.sh           # 最小限ドキュメント取得
│   └── fetch_github_vectorworks.sh     # GitHubリポジトリ取得
├── data/                        # ドキュメント保存先
│   ├── vw-app-help/            # App Help
│   ├── vw-jp-ref/              # 日本語リファレンス
│   ├── vw-devwiki/             # Developer Wiki
│   └── github/vectorworks/     # GitHubリポジトリ
├── index/                       # 検索インデックス
│   ├── vw.faiss                # FAISSインデックス
│   └── meta.jsonl              # メタデータ
├── mcp-bridge.js               # MCPブリッジスクリプト
├── package.json                # Node.js設定
├── Dockerfile                  # Dockerイメージ定義
├── docker-compose.yml          # Docker Compose設定
├── requirements.txt            # Python依存関係
├── README.md                   # プロジェクト説明
├── SETUP_GUIDE.md              # Claude Dev用セットアップガイド
└── SETUP_GITHUB_COPILOT.md     # このドキュメント
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

- [ ] VS Code バージョン 1.102以降がインストールされている
- [ ] GitHub Copilot拡張機能がインストール・有効化されている
- [ ] Dockerイメージがビルドされている
- [ ] ドキュメントが取得されている（`data/`配下）
- [ ] ベクトルインデックスが生成されている（`index/vw.faiss`）
- [ ] Dockerコンテナが起動している（`docker compose ps`で確認）
- [ ] Web UIにアクセスできる（http://localhost:8001）
- [ ] Node.js依存関係がインストールされている（`node_modules/ws`）
- [ ] MCPブリッジスクリプトが作成されている（`mcp-bridge.js`）
- [ ] `.vscode/mcp.json` が作成され、パスが正しく設定されている
- [ ] VS Codeを再起動している
- [ ] GitHub Copilot ChatからMCPツールが利用できる

---

## 参考情報

### GitHub CopilotのMCP関連ドキュメント

- [Extending GitHub Copilot Chat with MCP - GitHub Docs](https://docs.github.com/en/copilot/customizing-copilot/extending-copilot-chat-with-mcp)
- [Model Context Protocol (MCP) support in VS Code - GitHub Changelog](https://github.blog/changelog/2025-07-14-model-context-protocol-mcp-support-in-vs-code-is-generally-available/)
- [Building your first MCP server - The GitHub Blog](https://github.blog/ai-and-ml/github-copilot/building-your-first-mcp-server-how-to-extend-ai-tools-with-custom-capabilities/)

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
3. VS Code開発者コンソールを確認: `Ctrl+Shift+I`
4. GitHub Copilot Outputパネルを確認
5. GitHubリポジトリのIssuesを確認

---

**セットアップ完了おめでとうございます！**

VS Codeを再起動して、GitHub Copilot ChatからVectorworksドキュメントを検索してみてください。

**使用例**:
```
@workspace VectorScriptのPushAttrs関数について教えてください
```
