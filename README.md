# codex-lecture

FastAPI で実装したユーザー CRUD API と Next.js 製の管理フロントエンドのサンプルです。

## バックエンド (FastAPI)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows の場合は .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

API は `http://localhost:8001` で起動し、`/users` に CRUD エンドポイントを提供します。

## フロントエンド (Next.js)

```bash
cd frontend
npm install
npm run dev
```

ブラウザで `http://localhost:8000` を開くと、FastAPI と連携したユーザー管理 UI が表示されます。

必要に応じて `frontend/.env.local` に `NEXT_PUBLIC_API_BASE_URL` を設定すると接続先を変更できます (デフォルトは `http://localhost:8001`)。
