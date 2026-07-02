const { test, expect } = require('@playwright/test');

test('public routes for homepage and auth screens load in Vietnamese', async ({ page }) => {
  const homeResponse = await page.goto('/');

  expect(homeResponse).not.toBeNull();
  expect(homeResponse.ok()).toBeTruthy();
  await expect(page.getByRole('heading', { name: /nơi nhà báo tìm đúng chuyên gia/i })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Tạo tài khoản' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Đăng nhập bằng email' })).toBeVisible();

  const loginResponse = await page.goto('/login');
  expect(loginResponse).not.toBeNull();
  expect(loginResponse.ok()).toBeTruthy();
  await expect(page.getByRole('heading', { name: 'Đăng nhập vào NguonTin' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Nhận mã đăng nhập' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Tiếp tục với Google' })).toBeVisible();

  const registerResponse = await page.goto('/register');
  expect(registerResponse).not.toBeNull();
  expect(registerResponse.ok()).toBeTruthy();
  await expect(page.getByRole('heading', { name: 'Tạo tài khoản NguonTin' })).toBeVisible();
  await expect(page.getByLabel('Vai trò')).toBeVisible();
  await expect(page.getByLabel('Họ và tên')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Nhận mã để tạo tài khoản' })).toBeVisible();
});
