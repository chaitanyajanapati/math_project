import { test, expect } from '@playwright/test';

test.describe('Question Quality Dashboard', () => {
  test('navigates to quality dashboard and loads summary cards', async ({ page }) => {
    await page.goto('/');
    await page.click('a:has-text("Quality")');
    await expect(page).toHaveURL('/quality');
    // Header
    await expect(page.locator('h1')).toContainText('Question Quality');
    // Cards or skeleton present
    const card = page.locator('text=Overall Quality');
    await expect(card).toBeVisible();
  });
});
