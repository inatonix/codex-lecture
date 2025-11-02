import { useCallback, useMemo, useState } from "react";
import Head from "next/head";
import useSWR from "swr";

import UserForm from "@/components/UserForm";
import UserTable from "@/components/UserTable";
import styles from "@/styles/Home.module.css";
import {
  createUser,
  deleteUser,
  fetchUsers,
  updateUser,
} from "@/lib/api";

const initialFormState = {
  id: null,
  fields: { name: "", email: "", age: "" },
  message: null,
  error: null,
};

export default function HomePage() {
  const { data, error, isLoading, mutate } = useSWR("users", fetchUsers);
  const users = useMemo(() => data ?? [], [data]);

  const [formState, setFormState] = useState(initialFormState);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

  const handleEdit = useCallback((user) => {
    setFormState((prev) => ({
      ...prev,
      id: user.id,
      fields: {
        name: user.name ?? "",
        email: user.email ?? "",
        age: user.age ?? "",
      },
      message: null,
      error: null,
    }));
  }, []);

  const resetForm = useCallback(
    ({ message = null, errorMessage = null } = {}) => {
      setFormState({
        ...initialFormState,
        message,
        error: errorMessage,
      });
      setIsSubmitting(false);
    },
    []
  );

  const handleSubmit = useCallback(async () => {
    setIsSubmitting(true);
    setFormState((prev) => ({
      ...prev,
      message: null,
      error: null,
    }));

    try {
      const payload = {
        name: formState.fields.name.trim(),
        email: formState.fields.email.trim(),
        age:
          formState.fields.age === "" || formState.fields.age === null
            ? null
            : Number(formState.fields.age),
      };

      if (Number.isNaN(payload.age)) {
        throw new Error("年齢は数値で入力してください。");
      }

      if (formState.id) {
        await updateUser(formState.id, payload);
        resetForm({
          message: `ユーザー (ID: ${formState.id}) を更新しました。`,
        });
      } else {
        const created = await createUser(payload);
        resetForm({
          message: `ユーザー (ID: ${created.id}) を作成しました。`,
        });
      }

      await mutate();
    } catch (submitError) {
      resetForm({
        errorMessage: submitError.message || "送信中にエラーが発生しました。",
      });
    } finally {
      setIsSubmitting(false);
    }
  }, [formState, mutate, resetForm]);

  const handleCancelEdit = useCallback(() => {
    resetForm();
  }, [resetForm]);

  const handleDelete = useCallback(
    async (user) => {
      if (
        typeof window !== "undefined" &&
        !window.confirm(`ユーザー「${user.name}」を削除しますか？`)
      ) {
        return;
      }

      setDeletingId(user.id);
      try {
        await deleteUser(user.id);
        await mutate();
        setFormState((prev) => ({
          ...prev,
          message: `ユーザー (ID: ${user.id}) を削除しました。`,
        }));
      } catch (deleteError) {
        setFormState((prev) => ({
          ...prev,
          error: deleteError.message || "削除に失敗しました。",
        }));
      } finally {
        setDeletingId(null);
      }
    },
    [mutate]
  );

  return (
    <>
      <Head>
        <title>User CRUD Dashboard</title>
      </Head>
      <main className={styles.container}>
        <UserForm
          formState={formState}
          setFormState={setFormState}
          onSubmit={handleSubmit}
          onCancelEdit={handleCancelEdit}
          isSubmitting={isSubmitting}
        />
        <UserTable
          users={users}
          isLoading={isLoading}
          error={error?.message}
          onEdit={handleEdit}
          onDelete={handleDelete}
          deletingId={deletingId}
        />
        <section className={styles.card}>
          <h2 className={styles.heading}>接続情報</h2>
          <p className={styles.subheading}>
            Next.js フロントエンドと FastAPI バックエンドの接続設定です。
          </p>
          <p className={styles.muted}>
            API ベース URL: <code>{apiBaseUrl}</code>
          </p>
          <p className={styles.muted}>
            `requirements.txt` の FastAPI アプリを `uvicorn src.main:app
            --host 0.0.0.0 --port 8001 --reload` で起動し、別ターミナルで
            `npm install` と `npm run dev` を実行してください。
          </p>
        </section>
      </main>
    </>
  );
}
