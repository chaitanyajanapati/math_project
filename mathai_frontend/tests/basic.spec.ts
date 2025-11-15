import { test, expect } from '@playwright/test';

test.describe('Math AI App - Basic Flow', () => {
  test('should load homepage', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('Question Generator');
  });

  test('should generate a question', async ({ page }) => {
    await page.goto('/');
    
  // Select grade and topic
  await page.fill('input[type="number"]', '8');
  // Specifically target the Topic dropdown (label followed by select)
  await page.selectOption('label:has-text("Topic") + select', 'algebra');
    
    // Click generate and wait for question to render
    await page.click('button:has-text("Generate Question")');
    await expect(page.locator('[data-testid="question-panel"]')).not.toContainText('No question yet', { timeout: 15000 });
    await expect(page.locator('[data-testid="question-panel"]')).toContainText(/[A-Za-z]/, { timeout: 15000 });
  });

  test('should navigate to dashboard', async ({ page }) => {
    await page.goto('/');
    await page.click('a:has-text("Dashboard")');
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Your Dashboard');
  });

  test('should request a hint', async ({ page }) => {
    await page.goto('/');
    
    // Generate question first
    await page.click('button:has-text("Generate Question")');
    await expect(page.locator('[data-testid="question-panel"]')).not.toContainText('No question yet', { timeout: 15000 });
    
    // Request hint
    const hintBtn = page.getByRole('button', { name: /Get Hint|Next Hint/ });
    await expect(hintBtn).toBeEnabled();
    await hintBtn.click();
    
    // Check hint appears (hints section shows up) or button label changes to Next Hint
    const hintsVisible = await page.locator('[data-testid="hints-section"]').isVisible().catch(() => false);
    if (!hintsVisible) {
      await expect(page.getByRole('button', { name: /Next Hint/ })).toBeVisible({ timeout: 10000 });
    }
  });
});
