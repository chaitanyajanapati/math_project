import { test, expect } from '@playwright/test';

test.describe('Math AI App - Basic Flow', () => {
  test('should load homepage', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('Question Generator');
  });

  test('should generate a question', async ({ page }) => {
    await page.goto('/');
    
    // Select grade and topic
    await page.selectOption('select:has-text("Grade")', '8');
    await page.selectOption('select:has-text("Topic")', 'algebra');
    
    // Click generate
    await page.click('button:has-text("Generate Question")');
    
    // Wait for question to appear
    await expect(page.locator('.bg-yellow-50')).toContainText(/Solve|Find|Calculate/, {
      timeout: 10000
    });
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
    await page.waitForTimeout(2000);
    
    // Request hint
    await page.click('button:has-text("Get Hint")');
    
    // Check hint appears
    await expect(page.locator('text=💡')).toBeVisible({ timeout: 5000 });
  });
});
