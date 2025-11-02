import styles from "@/styles/Home.module.css";

function formatDate(value) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

export default function UserTable({
  users,
  isLoading,
  error,
  onEdit,
  onDelete,
  deletingId,
}) {
  return (
    <section className={styles.card}>
      <h2 className={styles.heading}>ユーザー一覧</h2>
      <p className={styles.subheading}>
        API から取得したデータを表示します。論理削除済みのユーザーは一覧に含まれません。
      </p>

      {isLoading && <p className={styles.muted}>読み込み中...</p>}
      {error && (
        <p className={styles.muted} style={{ color: "#b91c1c" }}>
          {error}
        </p>
      )}

      {!isLoading && !error && (
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>ID</th>
                <th>名前</th>
                <th>メールアドレス</th>
                <th>年齢</th>
                <th>作成日時</th>
                <th>更新日時</th>
                <th>状態</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 && (
                <tr>
                  <td colSpan={8}>
                    <span className={styles.muted}>
                      現在表示できるユーザーは存在しません。
                    </span>
                  </td>
                </tr>
              )}
              {users.map((user) => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>{user.name}</td>
                  <td>{user.email}</td>
                  <td>{user.age ?? "-"}</td>
                  <td>{formatDate(user.created_at)}</td>
                  <td>{formatDate(user.updated_at)}</td>
                  <td>
                    <span className={`${styles.tag} ${styles.active}`}>
                      Active
                    </span>
                  </td>
                  <td>
                    <div className={styles.actions}>
                      <button
                        className={`${styles.button} ${styles.secondary}`}
                        type="button"
                        onClick={() => onEdit(user)}
                      >
                        編集
                      </button>
                      <button
                        className={styles.button}
                        type="button"
                        style={{ background: "#dc2626" }}
                        onClick={() => onDelete(user)}
                        disabled={deletingId === user.id}
                      >
                        {deletingId === user.id ? "削除中..." : "削除"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
