import pytest
from fastapi.testclient import TestClient

from src import main


client = TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_state():
    """各テスト実行前後でインメモリDBをリセットする。"""
    main.users_db.clear()
    main.next_id = 1
    yield
    main.users_db.clear()
    main.next_id = 1


# CREATE 正常系: 新規ユーザー作成と同時に取得APIでも参照できることを担保する。
def test_create_user_returns_created_user():
    payload = {"name": "Alice", "email": "alice@example.com", "age": 30}

    response = client.post("/users", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data["age"] == payload["age"]
    assert "created_at" in data
    assert "updated_at" in data
    assert data["deleted_at"] is None

    # ensure persisted for subsequent reads
    get_response = client.get("/users/1")
    assert get_response.status_code == 200


# CREATE 異常系: メールアドレスのユニーク制約違反で作成できないことを担保する。
def test_create_user_duplicate_email_returns_400():
    payload = {"name": "Bob", "email": "bob@example.com", "age": 25}
    client.post("/users", json=payload)

    response = client.post("/users", json={"name": "Bobby", "email": "bob@example.com"})

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


# READ 正常系: ユーザー一覧取得が全レコードを返すことを担保する。
def test_get_users_returns_all_records():
    client.post("/users", json={"name": "Alice", "email": "alice@example.com"})
    client.post("/users", json={"name": "Bob", "email": "bob@example.com"})

    response = client.get("/users")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    returned_names = {item["name"] for item in data}
    assert returned_names == {"Alice", "Bob"}
    assert all(item["deleted_at"] is None for item in data)


# READ 異常系: 存在しないユーザー取得時に404が返ることを担保する。
def test_get_user_not_found_returns_404():
    response = client.get("/users/999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# UPDATE 正常系: ユーザー更新でフィールドと更新日時が変わることを担保する。
def test_update_user_mutates_fields():
    created = client.post("/users", json={"name": "Alice", "email": "alice@example.com"})
    user = created.json()

    response = client.put(
        f"/users/{user['id']}",
        json={"name": "Alicia", "age": 31},
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Alicia"
    assert updated["age"] == 31
    assert updated["email"] == user["email"]
    assert updated["updated_at"] != user["updated_at"]


# UPDATE 異常系: 更新時もユニーク制約が守られることを担保する。
def test_update_user_prevents_duplicate_email():
    client.post("/users", json={"name": "Alice", "email": "alice@example.com"})
    second = client.post("/users", json={"name": "Bob", "email": "bob@example.com"})
    second_id = second.json()["id"]

    response = client.put(
        f"/users/{second_id}",
        json={"email": "alice@example.com"},
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


# DELETE 正常系: 論理削除後に対象ユーザーへアクセスできずレコードが残ることを担保する。
def test_delete_user_marks_record_as_deleted():
    created = client.post("/users", json={"name": "Carol", "email": "carol@example.com"})
    user_id = created.json()["id"]

    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

    # ensure the record stays stored but flagged as deleted
    stored = main.users_db[user_id]
    assert stored.deleted_at is not None
    assert user_id not in {user["id"] for user in client.get("/users").json()}
