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


# メモリ内データストア（簡単な実装）
users_db: dict[int, UserResponse] = {}
next_id = 1


# CREATE: ユーザーを作成
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """新しいユーザーを作成します"""
    global next_id
    
    # メールアドレスの重複チェック
    for existing_user in users_db.values():
        if existing_user.email == user.email:
            raise HTTPException(
                status_code=400,
                detail=f"Email {user.email} already exists"
            )
    
    now = datetime.now()
    new_user = UserResponse(
        id=next_id,
        name=user.name,
        email=user.email,
        age=user.age,
        created_at=now,
        updated_at=now
    )
    
    users_db[next_id] = new_user
    next_id += 1
    
    return new_user


# READ: 全ユーザーを取得
@app.get("/users", response_model=List[UserResponse])
async def get_users():
    """すべてのユーザーを取得します"""
    return list(users_db.values())


# READ: 特定のユーザーを取得
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """IDで指定されたユーザーを取得します"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    
    return users_db[user_id]


# UPDATE: ユーザーを更新
@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate):
    """IDで指定されたユーザーを更新します"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    
    existing_user = users_db[user_id]
    
    # メールアドレスの重複チェック（自分以外）
    if user_update.email:
        for uid, u in users_db.items():
            if u.email == user_update.email and uid != user_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Email {user_update.email} already exists"
                )
    
    # 更新フィールドを適用
    update_data = user_update.model_dump(exclude_unset=True)
    updated_user = existing_user.model_copy(update=update_data)
    updated_user.updated_at = datetime.now()
    
    users_db[user_id] = updated_user
    
    return updated_user


# DELETE: ユーザーを削除
@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """IDで指定されたユーザーを削除します"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    
    del users_db[user_id]
    return None


# ヘルスチェックエンドポイント
@app.get("/")
async def root():
    """APIのヘルスチェック"""
    return {"message": "User CRUD API is running"}

