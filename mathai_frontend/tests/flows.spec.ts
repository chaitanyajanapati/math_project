import { test, expect } from '@playwright/test';

// Additional flows covering MCQ mode, solution steps, and timed mode

test.describe('Math AI App - Extended Flows', () => {
  test('MCQ mode shows choices or fallback', async ({ page }) => {
    await page.goto('/');

    // Set grade and switch to MCQ and Algebra topic
    await page.fill('[data-testid="grade-input"]', '8');
    await page.selectOption('[data-testid="question-type-select"]', 'mcq');
    await page.selectOption('[data-testid="topic-select"]', 'algebra');

    // Generate question and wait for backend response
    await Promise.all([
      page.waitForResponse(r => r.url().includes('/api/generate-question') && r.status() === 200),
      page.click('[data-testid="generate-btn"]')
    ]);

    // Ensure the question panel populated
    await expect(page.locator('[data-testid="question-panel"]')).not.toContainText('No question yet', { timeout: 10000 });

    // Either choices are available or fallback warning is shown
    const choiceCount = await page.locator('[data-testid="mcq-choices"] label').count();
    if (choiceCount > 0) {
      expect(choiceCount).toBeGreaterThan(0);
    } else {
      await expect(page.locator('text=Multiple choice options not loaded.')).toBeVisible();
    }
  });

  test('Solution steps placeholder disappears after requesting solution', async ({ page }) => {
    await page.goto('/');

    // Generate open question quickly
    await Promise.all([
      page.waitForResponse(r => r.url().includes('/api/generate-question') && r.status() === 200),
      page.click('[data-testid="generate-btn"]')
    ]);
    await expect(page.locator('[data-testid="question-panel"]')).not.toContainText('No question yet', { timeout: 10000 });

    // Request solution and verify placeholder is replaced
    await page.click('[data-testid="solution-btn"]');
    await expect(page.locator('[data-testid="solution-steps-placeholder"]')).toBeHidden({ timeout: 10000 });
    await expect(page.locator('[data-testid="solution-steps"]')).toBeVisible();
  });

  test('Timed mode shows timer when enabled and question generated', async ({ page }) => {
    await page.goto('/');

    // Enable timed mode by clicking its checkbox label
    await page.click('label:has-text("Timed Mode") input');

    // Generate a question
    await Promise.all([
      page.waitForResponse(r => r.url().includes('/api/generate-question') && r.status() === 200),
      page.click('[data-testid="generate-btn"]')
    ]);

    // Timer should be visible
    await expect(page.locator('[data-testid="timer"]')).toBeVisible();
  });
});
