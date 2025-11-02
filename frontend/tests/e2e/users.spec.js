const { test, expect } = require("@playwright/test");

test.describe("ユーザー管理UI: 一連のCRUDフロー", () => {
  test("正常系: 作成→更新→論理削除の完走を担保する", async ({ page }) => {
    const unique = Date.now().toString();
    const name = `E2E-${unique}`;
    const email = `e2e-${unique}@example.com`;
    const updatedName = `${name}-更新`;

    await page.goto("/");

    await page.getByLabel("名前").fill(name);
    await page.getByLabel("メールアドレス").fill(email);
    await page.getByLabel("年齢 (任意)").fill("33");
    await page.getByRole("button", { name: "ユーザーを登録" }).click();

    const createdRow = page.locator("tbody tr").filter({ hasText: name });
    await expect(createdRow).toHaveCount(1);
    await expect(page.getByText(/作成しました。/)).toBeVisible();
    await page.waitForTimeout(2000);

    await createdRow.getByRole("button", { name: "編集" }).click();

    await expect(page.getByLabel("名前")).toHaveValue(name);
    await page.getByLabel("名前").fill(updatedName);
    await page.getByLabel("年齢 (任意)").fill("34");
    await page.getByRole("button", { name: "ユーザーを更新" }).click();

    const updatedRow = page
      .locator("tbody tr")
      .filter({ hasText: updatedName });
    await expect(updatedRow).toHaveCount(1);
    await expect(page.getByText(/更新しました。/)).toBeVisible();
    await page.waitForTimeout(2000);

    page.once("dialog", (dialog) => dialog.accept());
    await updatedRow.getByRole("button", { name: "削除" }).click();

    await expect(page.getByText(/削除しました。/)).toBeVisible();
    await page.waitForTimeout(2000);
    await expect(
      page.locator("tbody tr").filter({ hasText: updatedName })
    ).toHaveCount(0);
  });

  test("正常系: 複数ユーザーを登録・削除して順序を維持する", async ({ page }) => {
    const unique = Date.now().toString();
    const users = Array.from({ length: 3 }, (_, index) => {
      const suffix = `${unique}-${index + 1}`;
      return {
        name: `E2E-ORDER-${suffix}`,
        email: `e2e-order-${suffix}@example.com`,
      };
    });

    await page.goto("/");

    for (const { name, email } of users) {
      await page.getByLabel("名前").fill(name);
      await page.getByLabel("メールアドレス").fill(email);
      await page.getByLabel("年齢 (任意)").fill("");
      await page.getByRole("button", { name: "ユーザーを登録" }).click();

      const createdRow = page.locator("tbody tr").filter({ hasText: name });
      await expect(createdRow).toHaveCount(1);
      await expect(page.getByText(/作成しました。/)).toBeVisible();
      await page.waitForTimeout(2000);
    }

    const nameCells = page.locator("tbody tr td:nth-child(2)");
    const initialOrder = await nameCells.allTextContents();
    await expect(initialOrder).toEqual(users.map((user) => user.name));

    const deletedUser = users[1];
    page.once("dialog", (dialog) => dialog.accept());
    await page
      .locator("tbody tr")
      .filter({ hasText: deletedUser.name })
      .getByRole("button", { name: "削除" })
      .click();

    await expect(page.getByText(/削除しました。/)).toBeVisible();
    await page.waitForTimeout(2000);

    const remainingOrder = await nameCells.allTextContents();
    await expect(remainingOrder).toEqual([
      users[0].name,
      users[2].name,
    ]);
  });
});
