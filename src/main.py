from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="User CRUD API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ユーザーモデル定義
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


# メモリ内データストア（簡単な実装）
users_db: dict[int, UserResponse] = {}
next_id = 1


def _assert_unique_constraints(
    *,
    name: Optional[str] = None,
    email: Optional[str] = None,
    exclude_id: Optional[int] = None,
) -> None:
    """指定されたユニーク制約を検証する。"""
    for uid, user in users_db.items():
        if uid == exclude_id:
            continue
        if user.deleted_at is not None:
            continue
        if email and user.email == email:
            raise HTTPException(
                status_code=400,
                detail=f"Email {email} already exists"
            )
        if name and user.name == name:
            raise HTTPException(
                status_code=400,
                detail=f"Name {name} already exists"
            )


# CREATE: ユーザーを作成
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate) -> UserResponse:
    """新しいユーザーを作成します

    Args:
        user: 作成したいユーザー情報。

    Returns:
        作成されたユーザーの状態（ID・タイムスタンプを含む）。
    """
    global next_id
    
    _assert_unique_constraints(name=user.name, email=user.email)
    
    now = datetime.now()
    new_user = UserResponse(
        id=next_id,
        name=user.name,
        email=user.email,
        age=user.age,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )
    
    users_db[next_id] = new_user
    next_id += 1
    
    return new_user


# READ: 全ユーザーを取得
@app.get("/users", response_model=List[UserResponse])
async def get_users() -> List[UserResponse]:
    """すべてのユーザーを取得します

    Returns:
        登録済みユーザーの一覧。
    """
    return [user for user in users_db.values() if user.deleted_at is None]


# READ: 特定のユーザーを取得
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> UserResponse:
    """IDで指定されたユーザーを取得します

    Args:
        user_id: 取得したいユーザーのID。

    Returns:
        該当ユーザーの状態。
    """
    if user_id not in users_db or users_db[user_id].deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    
    return users_db[user_id]


# UPDATE: ユーザーを更新
@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate) -> UserResponse:
    """IDで指定されたユーザーを更新します

    Args:
        user_id: 更新対象ユーザーのID。
        user_update: 更新したいフィールドの集合。

    Returns:
        更新後のユーザー状態。
    """
    if user_id not in users_db or users_db[user_id].deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    
    record = users_db[user_id]
    
    # メールアドレスの重複チェック（自分以外）
    target_email = user_update.email or record.email
    target_name = user_update.name or record.name
    _assert_unique_constraints(
        name=target_name,
        email=target_email,
        exclude_id=user_id,
    )
    
    # 更新フィールドを適用
    update_data = user_update.model_dump(exclude_unset=True)
    updated_user = record.model_copy(update=update_data)
    updated_user.updated_at = datetime.now()
    
    users_db[user_id] = updated_user
    
    return updated_user


# DELETE: ユーザーを削除
@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int) -> None:
    """IDで指定されたユーザーを削除します
    
    Args:
        user_id: 削除したいユーザーのID。
    
    Returns:
        None: 削除が成功したことを表します。
    """
    if user_id not in users_db or users_db[user_id].deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )

    record = users_db[user_id]
    now = datetime.now()
    deleted_user = record.model_copy(update={"deleted_at": now, "updated_at": now})
    users_db[user_id] = deleted_user
    return None


# ヘルスチェックエンドポイント
@app.get("/")
async def root() -> dict[str, str]:
    """APIのヘルスチェック

    Returns:
        API稼働状況を表すメッセージ。
    """
    return {"message": "User CRUD API is running"}
