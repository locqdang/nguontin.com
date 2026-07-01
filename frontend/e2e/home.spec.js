const { test, expect } = require('@playwright/test');

test('home page loads', async ({ page }) => {
  const response = await page.goto('/');

  expect(response).not.toBeNull();
  expect(response.ok()).toBeTruthy();
  await expect(page.locator('body')).toBeVisible();
  await expect(page.getByRole('heading', { name: /nơi nhà báo tìm đúng chuyên gia/i })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Nhận thông tin sớm' })).toBeVisible();
});
