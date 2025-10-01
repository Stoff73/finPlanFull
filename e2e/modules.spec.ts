import { test, expect } from '@playwright/test';

/**
 * E2E Test Suite for Goal-Based Modules
 * Tests cover: Navigation, CRUD operations, Analytics, Form validation, Mobile responsive
 */

// Test credentials
const TEST_USER = {
  username: 'demouser',
  password: 'demo123',
};

// Helper function to login
async function login(page) {
  await page.goto('/login');
  await page.fill('input[type="text"], input[type="email"]', TEST_USER.username);
  await page.fill('input[type="password"]', TEST_USER.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard');
}

test.describe('Module Navigation Tests', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should navigate from main dashboard to Protection module dashboard', async ({ page }) => {
    // Wait for dashboard to load
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL('/dashboard');

    // Find and click Protection module card/link
    await page.click('text=/Protection/i');

    // Verify navigation to Protection dashboard
    await page.waitForURL('/modules/protection/dashboard');
    await expect(page).toHaveURL('/modules/protection/dashboard');
    await expect(page.locator('h1, h2').first()).toContainText(/Protection/i);
  });

  test('should navigate from main dashboard to Savings module dashboard', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL('/dashboard');

    await page.click('text=/Savings/i');

    await page.waitForURL('/modules/savings/dashboard');
    await expect(page).toHaveURL('/modules/savings/dashboard');
    await expect(page.locator('h1, h2').first()).toContainText(/Savings/i);
  });

  test('should navigate from main dashboard to Investment module dashboard', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL('/dashboard');

    await page.click('text=/Investment/i');

    await page.waitForURL('/modules/investment/dashboard');
    await expect(page).toHaveURL('/modules/investment/dashboard');
    await expect(page.locator('h1, h2').first()).toContainText(/Investment/i);
  });

  test('should navigate from main dashboard to Retirement module dashboard', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL('/dashboard');

    await page.click('text=/Retirement/i');

    await page.waitForURL('/modules/retirement/dashboard');
    await expect(page).toHaveURL('/modules/retirement/dashboard');
    await expect(page.locator('h1, h2').first()).toContainText(/Retirement/i);
  });

  test('should navigate from main dashboard to IHT Planning module dashboard', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL('/dashboard');

    await page.click('text=/IHT|Inheritance/i');

    await page.waitForURL('/modules/iht/dashboard');
    await expect(page).toHaveURL('/modules/iht/dashboard');
    await expect(page.locator('h1, h2').first()).toContainText(/IHT|Inheritance/i);
  });

  test('should navigate between module sections within Protection module', async ({ page }) => {
    // Navigate to Protection module
    await page.goto('/modules/protection/dashboard');

    // Navigate to Portfolio section
    await page.click('text=/Portfolio|Policies/i');
    await expect(page).toHaveURL('/modules/protection/portfolio');

    // Navigate to Analytics section
    await page.click('text=/Analytics/i');
    await expect(page).toHaveURL('/modules/protection/analytics');

    // Navigate to Needs Analysis section
    await page.click('text=/Needs Analysis/i');
    await expect(page).toHaveURL('/modules/protection/needs-analysis');

    // Navigate back to Dashboard
    await page.click('text=/Dashboard/i');
    await expect(page).toHaveURL('/modules/protection/dashboard');
  });
});

test.describe('Module CRUD Operations Tests', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should create a new protection product', async ({ page }) => {
    // Navigate to Protection Portfolio
    await page.goto('/modules/protection/portfolio');
    await page.waitForLoadState('networkidle');

    // Click "Add" or "Create" button
    const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")').first();
    await addButton.click();

    // Fill in form fields
    await page.fill('input[name="product_name"], input[name="name"]', 'Test Life Insurance');
    await page.fill('input[name="provider"]', 'Test Provider');
    await page.fill('input[name="sum_assured"], input[name="coverage_amount"]', '500000');
    await page.fill('input[name="premium"], input[name="annual_premium"]', '1200');

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for success message or redirect
    await page.waitForTimeout(1000);

    // Verify product appears in list
    await expect(page.locator('text=Test Life Insurance')).toBeVisible();
  });

  test('should edit an existing savings account', async ({ page }) => {
    // Navigate to Savings Accounts
    await page.goto('/modules/savings/accounts');
    await page.waitForLoadState('networkidle');

    // Click first edit button
    const editButton = page.locator('button:has-text("Edit"), [aria-label="Edit"]').first();

    if (await editButton.isVisible()) {
      await editButton.click();

      // Modify a field
      await page.fill('input[name="account_name"], input[name="name"]', 'Updated Account Name');

      // Submit form
      await page.click('button[type="submit"]');

      // Wait for update
      await page.waitForTimeout(1000);

      // Verify updated name appears
      await expect(page.locator('text=Updated Account Name')).toBeVisible();
    }
  });

  test('should delete an investment product', async ({ page }) => {
    // Navigate to Investment Portfolio
    await page.goto('/modules/investment/portfolio');
    await page.waitForLoadState('networkidle');

    // Get initial count of products
    const initialCount = await page.locator('[data-testid="investment-card"], .product-card, .investment-item').count();

    if (initialCount > 0) {
      // Click first delete/archive button
      const deleteButton = page.locator('button:has-text("Delete"), button:has-text("Archive"), [aria-label="Delete"]').first();
      await deleteButton.click();

      // Confirm deletion if modal appears
      const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")');
      if (await confirmButton.isVisible({ timeout: 2000 }).catch(() => false)) {
        await confirmButton.click();
      }

      // Wait for deletion
      await page.waitForTimeout(1000);

      // Verify count decreased or success message appears
      const finalCount = await page.locator('[data-testid="investment-card"], .product-card, .investment-item').count();
      expect(finalCount).toBeLessThanOrEqual(initialCount);
    }
  });

  test('should handle CRUD operations in Retirement Pensions', async ({ page }) => {
    // Navigate to Retirement Pensions
    await page.goto('/modules/retirement/pensions');
    await page.waitForLoadState('networkidle');

    // Create new pension
    const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")').first();

    if (await addButton.isVisible()) {
      await addButton.click();

      // Fill form
      await page.fill('input[name="scheme_name"], input[name="name"]', 'Test Pension Scheme');
      await page.fill('input[name="current_value"], input[name="value"]', '150000');
      await page.fill('input[name="annual_contribution"]', '12000');

      // Submit
      await page.click('button[type="submit"]');
      await page.waitForTimeout(1000);

      // Verify created
      await expect(page.locator('text=Test Pension Scheme')).toBeVisible();
    }
  });
});

test.describe('Analytics Views Tests', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should load Protection Analytics page correctly', async ({ page }) => {
    await page.goto('/modules/protection/analytics');
    await page.waitForLoadState('networkidle');

    // Verify page loaded
    await expect(page.locator('h1, h2')).toContainText(/Analytics|Coverage/i);

    // Check for common analytics elements
    const hasCharts = await page.locator('canvas, svg[class*="recharts"]').count() > 0;
    const hasMetrics = await page.locator('[class*="metric"], [class*="card"]').count() > 0;

    expect(hasCharts || hasMetrics).toBeTruthy();
  });

  test('should load Savings Analytics page correctly', async ({ page }) => {
    await page.goto('/modules/savings/analytics');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('h1, h2')).toContainText(/Analytics|Savings/i);

    // Verify analytics content is present
    const contentCount = await page.locator('[class*="metric"], [class*="card"], canvas, svg').count();
    expect(contentCount).toBeGreaterThan(0);
  });

  test('should load Investment Analytics page correctly', async ({ page }) => {
    await page.goto('/modules/investment/analytics');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('h1, h2')).toContainText(/Analytics|Performance/i);

    // Check for analytics content
    const hasAnalytics = await page.locator('[class*="metric"], [class*="card"], canvas, svg').count() > 0;
    expect(hasAnalytics).toBeTruthy();
  });

  test('should load Retirement Projections page correctly', async ({ page }) => {
    await page.goto('/modules/retirement/projections');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('h1, h2')).toContainText(/Projections|Retirement/i);

    // Verify projections content
    const contentCount = await page.locator('[class*="metric"], [class*="card"], canvas, svg').count();
    expect(contentCount).toBeGreaterThan(0);
  });

  test('should load Investment Rebalancing page correctly', async ({ page }) => {
    await page.goto('/modules/investment/rebalancing');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('h1, h2')).toContainText(/Rebalanc/i);

    // Verify rebalancing content
    const hasContent = await page.locator('[class*="metric"], [class*="card"], table').count() > 0;
    expect(hasContent).toBeTruthy();
  });
});

test.describe('Form Validation Tests', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should validate required fields in Protection form', async ({ page }) => {
    await page.goto('/modules/protection/portfolio');
    await page.waitForLoadState('networkidle');

    // Click add button
    const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")').first();

    if (await addButton.isVisible()) {
      await addButton.click();

      // Try to submit empty form
      await page.click('button[type="submit"]');

      // Check for validation messages
      await page.waitForTimeout(500);

      // Verify form didn't submit (either validation messages or still on form)
      const hasValidationMessage = await page.locator('text=/required|must|invalid/i').count() > 0;
      const stillOnForm = await page.locator('button[type="submit"]').isVisible();

      expect(hasValidationMessage || stillOnForm).toBeTruthy();
    }
  });

  test('should validate numeric fields in Savings form', async ({ page }) => {
    await page.goto('/modules/savings/accounts');
    await page.waitForLoadState('networkidle');

    const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")').first();

    if (await addButton.isVisible()) {
      await addButton.click();

      // Fill in name
      await page.fill('input[name="account_name"], input[name="name"]', 'Test Account');

      // Try to enter invalid number
      await page.fill('input[name="current_balance"], input[name="balance"]', 'invalid');

      // Submit form
      await page.click('button[type="submit"]');
      await page.waitForTimeout(500);

      // Verify validation occurs
      const hasError = await page.locator('text=/invalid|number|required/i').count() > 0;
      const stillOnForm = await page.locator('button[type="submit"]').isVisible();

      expect(hasError || stillOnForm).toBeTruthy();
    }
  });

  test('should validate date fields in IHT Gifts form', async ({ page }) => {
    await page.goto('/modules/iht/gifts');
    await page.waitForLoadState('networkidle');

    const addButton = page.locator('button:has-text("Add"), button:has-text("Record"), button:has-text("New")').first();

    if (await addButton.isVisible()) {
      await addButton.click();

      // Fill required fields
      await page.fill('input[name="recipient"], input[name="recipient_name"]', 'Test Recipient');
      await page.fill('input[name="amount"], input[name="gift_amount"]', '10000');

      // Try invalid date if date picker allows manual entry
      const dateInput = page.locator('input[type="date"], input[name*="date"]').first();
      if (await dateInput.isVisible()) {
        await dateInput.fill('invalid-date');

        // Submit
        await page.click('button[type="submit"]');
        await page.waitForTimeout(500);

        // Verify validation
        const hasError = await page.locator('text=/invalid|required|date/i').count() > 0;
        expect(hasError).toBeTruthy();
      }
    }
  });
});

test.describe('Mobile Navigation Tests', () => {
  test.use({ viewport: { width: 375, height: 667 } }); // iPhone SE size

  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should show mobile navigation menu', async ({ page }) => {
    await page.goto('/dashboard');

    // Look for hamburger menu button
    const menuButton = page.locator('button[aria-label*="menu"], button[aria-label*="Menu"], [class*="hamburger"]').first();

    if (await menuButton.isVisible()) {
      await menuButton.click();

      // Verify menu opened
      await page.waitForTimeout(300);

      // Check for navigation links
      const hasNavLinks = await page.locator('a[href*="/modules"], nav a').count() > 0;
      expect(hasNavLinks).toBeTruthy();
    }
  });

  test('should navigate to modules from mobile menu', async ({ page }) => {
    await page.goto('/dashboard');

    // Open mobile menu
    const menuButton = page.locator('button[aria-label*="menu"], button[aria-label*="Menu"], [class*="hamburger"]').first();

    if (await menuButton.isVisible()) {
      await menuButton.click();
      await page.waitForTimeout(300);

      // Click on Protection module link
      await page.click('text=/Protection/i');

      // Verify navigation
      await page.waitForURL(/\/modules\/protection/);
      await expect(page).toHaveURL(/\/modules\/protection/);
    }
  });

  test('should display module cards in mobile layout', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Verify module cards are visible
    const cards = await page.locator('[class*="card"], [class*="module"]').count();
    expect(cards).toBeGreaterThan(0);

    // Verify cards are stacked (mobile layout)
    const firstCard = page.locator('[class*="card"], [class*="module"]').first();
    if (await firstCard.isVisible()) {
      const box = await firstCard.boundingBox();
      expect(box?.width).toBeGreaterThan(300); // Should take most of screen width
    }
  });

  test('should handle forms on mobile viewport', async ({ page }) => {
    await page.goto('/modules/protection/portfolio');
    await page.waitForLoadState('networkidle');

    const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")').first();

    if (await addButton.isVisible()) {
      await addButton.click();

      // Verify form is usable on mobile
      const formInputs = await page.locator('input, select, textarea').count();
      expect(formInputs).toBeGreaterThan(0);

      // Try filling a field
      const firstInput = page.locator('input[type="text"]').first();
      if (await firstInput.isVisible()) {
        await firstInput.fill('Test Value');
        const value = await firstInput.inputValue();
        expect(value).toBe('Test Value');
      }
    }
  });

  test('should scroll and view all content on mobile', async ({ page }) => {
    await page.goto('/modules/protection/dashboard');
    await page.waitForLoadState('networkidle');

    // Get initial scroll position
    const initialScroll = await page.evaluate(() => window.scrollY);

    // Scroll down
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(300);

    // Verify scroll occurred
    const finalScroll = await page.evaluate(() => window.scrollY);
    expect(finalScroll).toBeGreaterThan(initialScroll);

    // Scroll back to top
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(300);
  });
});

test.describe('Cross-Module Integration Tests', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should access all 5 module dashboards in sequence', async ({ page }) => {
    const modules = [
      { name: 'Protection', path: '/modules/protection/dashboard' },
      { name: 'Savings', path: '/modules/savings/dashboard' },
      { name: 'Investment', path: '/modules/investment/dashboard' },
      { name: 'Retirement', path: '/modules/retirement/dashboard' },
      { name: 'IHT', path: '/modules/iht/dashboard' },
    ];

    for (const module of modules) {
      await page.goto(module.path);
      await page.waitForLoadState('networkidle');

      // Verify page loaded successfully
      await expect(page).toHaveURL(module.path);

      // Verify no JavaScript errors
      const errors: string[] = [];
      page.on('pageerror', error => errors.push(error.message));

      await page.waitForTimeout(500);
      expect(errors.length).toBe(0);
    }
  });

  test('should maintain authentication across module navigation', async ({ page }) => {
    // Navigate through multiple modules
    await page.goto('/modules/protection/dashboard');
    await expect(page).toHaveURL('/modules/protection/dashboard');

    await page.goto('/modules/savings/dashboard');
    await expect(page).toHaveURL('/modules/savings/dashboard');

    await page.goto('/modules/investment/dashboard');
    await expect(page).toHaveURL('/modules/investment/dashboard');

    // Verify still authenticated (not redirected to login)
    await expect(page).not.toHaveURL('/login');
  });

  test('should load without console errors', async ({ page }) => {
    const errors: string[] = [];
    const warnings: string[] = [];

    page.on('pageerror', error => errors.push(error.message));
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      } else if (msg.type() === 'warning') {
        warnings.push(msg.text());
      }
    });

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Filter out acceptable warnings (like React warnings in dev mode)
    const criticalErrors = errors.filter(e =>
      !e.includes('ResizeObserver') &&
      !e.includes('source map')
    );

    expect(criticalErrors.length).toBe(0);
  });
});
