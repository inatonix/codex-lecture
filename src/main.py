from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="User CRUD API", version="1.0.0")


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


class UserRecord(UserResponse):
    deleted: bool = False


# メモリ内データストア（簡単な実装）
users_db: dict[int, UserRecord] = {}
next_id = 1


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
    
    # メールアドレスの重複チェック
    for existing_user in users_db.values():
        if not existing_user.deleted and existing_user.email == user.email:
            raise HTTPException(
                status_code=400,
                detail=f"Email {user.email} already exists"
            )
    
    now = datetime.now()
    new_user = UserRecord(
        id=next_id,
        name=user.name,
        email=user.email,
        age=user.age,
        created_at=now,
        updated_at=now,
        deleted=False
    )
    
    users_db[next_id] = new_user
    next_id += 1
    
    return UserResponse.model_validate(new_user)


# READ: 全ユーザーを取得
@app.get("/users", response_model=List[UserResponse])
async def get_users() -> List[UserResponse]:
    """すべてのユーザーを取得します

    Returns:
        登録済みユーザーの一覧。
    """
    return [
        UserResponse.model_validate(user)
        for user in users_db.values()
        if not user.deleted
    ]


# READ: 特定のユーザーを取得
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> UserResponse:
    """IDで指定されたユーザーを取得します

    Args:
        user_id: 取得したいユーザーのID。

    Returns:
        該当ユーザーの状態。
    """
    record = users_db.get(user_id)
    if record is None or record.deleted:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    
    return UserResponse.model_validate(record)


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
    record = users_db.get(user_id)
    if record is None or record.deleted:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    
    # メールアドレスの重複チェック（自分以外）
    if user_update.email:
        for uid, u in users_db.items():
            if (
                uid != user_id
                and not u.deleted
                and u.email == user_update.email
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"Email {user_update.email} already exists"
                )
    
    # 更新フィールドを適用
    update_data = user_update.model_dump(exclude_unset=True)
    updated_user = record.model_copy(update=update_data)
    updated_user.updated_at = datetime.now()
    
    users_db[user_id] = updated_user
    
    return UserResponse.model_validate(updated_user)


# DELETE: ユーザーを削除
@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int) -> None:
    """IDで指定されたユーザーを論理削除します
    
    Args:
        user_id: 削除したいユーザーのID。
    
    Returns:
        None: 削除が成功したことを表します。
    """
    record = users_db.get(user_id)
    if record is None or record.deleted:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    
    record.deleted = True
    record.updated_at = datetime.now()
    users_db[user_id] = record
    return None


# ヘルスチェックエンドポイント
@app.get("/")
async def root() -> dict[str, str]:
    """APIのヘルスチェック

    Returns:
        API稼働状況を表すメッセージ。
    """
    return {"message": "User CRUD API is running"}
