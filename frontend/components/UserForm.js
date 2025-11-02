import styles from "@/styles/Home.module.css";

export default function UserForm({
  formState,
  setFormState,
  onSubmit,
  onCancelEdit,
  isSubmitting,
}) {
  const isEditing = Boolean(formState.id);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormState((prev) => ({
      ...prev,
      fields: {
        ...prev.fields,
        [name]: value,
      },
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit();
  };

  const handleCancel = () => {
    onCancelEdit?.();
  };

  return (
    <section className={styles.card}>
      <h1 className={styles.heading}>
        {isEditing ? "ユーザー更新" : "ユーザー作成"}
      </h1>
      <p className={styles.subheading}>
        FastAPI のユーザー CRUD API を Next.js から操作します。
      </p>

      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.field}>
          <label htmlFor="name">名前</label>
          <input
            id="name"
            name="name"
            placeholder="山田 太郎"
            value={formState.fields.name}
            onChange={handleChange}
            required
          />
        </div>
        <div className={styles.field}>
          <label htmlFor="email">メールアドレス</label>
          <input
            id="email"
            name="email"
            type="email"
            placeholder="taro@example.com"
            value={formState.fields.email}
            onChange={handleChange}
            required
          />
        </div>
        <div className={styles.field}>
          <label htmlFor="age">年齢 (任意)</label>
          <input
            id="age"
            name="age"
            type="number"
            min="0"
            placeholder="30"
            value={formState.fields.age}
            onChange={handleChange}
          />
        </div>
        <div className={styles.actions}>
          <button className={styles.button} type="submit" disabled={isSubmitting}>
            {isSubmitting
              ? "送信中..."
              : isEditing
              ? "ユーザーを更新"
              : "ユーザーを登録"}
          </button>
          {isEditing && (
            <button
              type="button"
              className={`${styles.button} ${styles.secondary}`}
              onClick={handleCancel}
              disabled={isSubmitting}
            >
              編集をキャンセル
            </button>
          )}
        </div>
      </form>

      {formState.message && (
        <p className={styles.muted}>{formState.message}</p>
      )}
      {formState.error && (
        <p className={styles.muted} style={{ color: "#b91c1c" }}>
          {formState.error}
        </p>
      )}
    </section>
  );
}
