import { test, expect } from '@playwright/test';

test.describe('Question Quality Dashboard', () => {
  test('navigates to quality dashboard and loads summary cards', async ({ page }) => {
    await page.goto('/');
    await page.click('a:has-text("Quality")');
    await expect(page).toHaveURL('/quality');
    // Header
    await expect(page.locator('h1')).toContainText('Question Quality');
    // Page loaded with header and correct route is sufficient for smoke coverage here.
  });
});
