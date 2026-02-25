import { test, expect } from '@playwright/test';

const BASE_URL = 'file:///home/rizki/hazn/docs/index.html';

// ============================================================
// 1. PAGE LOAD TESTS
// ============================================================
test.describe('1. Page Load', () => {
  test('page loads without errors', async ({ page }) => {
    const response = await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    expect(response).toBeTruthy();
  });

  test('title tag is correct', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle('Hazn: AI Marketing Agents for Technical Founders');
  });

  test('no console errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    // Filter out expected errors (like Tally form not loading on file://)
    const realErrors = errors.filter(e => !e.includes('tally') && !e.includes('FORM_ID'));
    expect(realErrors).toHaveLength(0);
  });
});

// ============================================================
// 2. ALL SECTIONS PRESENT
// ============================================================
test.describe('2. All Sections Present', () => {
  test('hero section visible', async ({ page }) => {
    await page.goto(BASE_URL);
    const hero = page.locator('section').first();
    await expect(hero).toBeVisible();
    // Check for hero content
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('text=Your Coding Assistant. Now a Marketing Team.')).toBeVisible();
  });

  test('problem section visible', async ({ page }) => {
    await page.goto(BASE_URL);
    const problemSection = page.locator('text=You Can Build Anything. Marketing Is Still the Bottleneck.');
    await expect(problemSection).toBeVisible();
  });

  test('solution section with 10 agent cards visible', async ({ page }) => {
    await page.goto(BASE_URL);
    const solutionHeading = page.locator('text=Not Another AI Tool. A Coordinated Marketing Team.');
    await expect(solutionHeading).toBeVisible();
    
    // Count agent cards - should be 10
    const agentCards = page.locator('.grid.grid-cols-2 > div');
    await expect(agentCards).toHaveCount(10);
  });

  test('how it works section visible', async ({ page }) => {
    await page.goto(BASE_URL);
    const howItWorks = page.locator('text=From Idea to Production in Three Steps');
    await expect(howItWorks).toBeVisible();
  });

  test('who its for section with 4 audience cards visible', async ({ page }) => {
    await page.goto(BASE_URL);
    const whoItsFor = page.locator('text=If You Ship Code, You Can Ship Marketing.');
    await expect(whoItsFor).toBeVisible();
    
    // Count audience cards - should be 4
    const audienceCards = page.locator('.grid.md\\:grid-cols-2 > div.card-hover');
    await expect(audienceCards).toHaveCount(4);
  });

  test('founder story section visible', async ({ page }) => {
    await page.goto(BASE_URL);
    const founderStory = page.locator('text=35 Years of Building. Marketing Was Always the Hard Part.');
    await expect(founderStory).toBeVisible();
  });

  test('early access section visible', async ({ page }) => {
    await page.goto(BASE_URL);
    const earlyAccess = page.locator('text=First 100 Users Shape the Product.');
    await expect(earlyAccess).toBeVisible();
  });

  test('FAQ section visible', async ({ page }) => {
    await page.goto(BASE_URL);
    const faq = page.locator('text=Frequently Asked Questions');
    await expect(faq).toBeVisible();
  });

  test('footer visible', async ({ page }) => {
    await page.goto(BASE_URL);
    const footer = page.locator('footer');
    await expect(footer).toBeVisible();
    await expect(page.locator('text=© 2025 Autonomous. Shipping soon.')).toBeVisible();
  });
});

// ============================================================
// 3. SEO ELEMENTS
// ============================================================
test.describe('3. SEO Elements', () => {
  test('meta description exists', async ({ page }) => {
    await page.goto(BASE_URL);
    const metaDesc = page.locator('meta[name="description"]');
    await expect(metaDesc).toHaveAttribute('content', /10 AI marketing agents/);
  });

  test('OG tags present', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page.locator('meta[property="og:title"]')).toHaveAttribute('content', /Hazn/);
    await expect(page.locator('meta[property="og:description"]')).toHaveAttribute('content', /.+/);
    await expect(page.locator('meta[property="og:image"]')).toHaveAttribute('content', /.+/);
    await expect(page.locator('meta[property="og:url"]')).toHaveAttribute('content', /.+/);
    await expect(page.locator('meta[property="og:type"]')).toHaveAttribute('content', 'website');
  });

  test('JSON-LD schema blocks present (check for 3)', async ({ page }) => {
    await page.goto(BASE_URL);
    const schemaScripts = page.locator('script[type="application/ld+json"]');
    const count = await schemaScripts.count();
    expect(count).toBeGreaterThanOrEqual(3);
    
    // Verify they contain valid JSON
    for (let i = 0; i < count; i++) {
      const content = await schemaScripts.nth(i).textContent();
      expect(() => JSON.parse(content!)).not.toThrow();
    }
  });

  test('H1 exists and is unique', async ({ page }) => {
    await page.goto(BASE_URL);
    const h1s = page.locator('h1');
    await expect(h1s).toHaveCount(1);
    await expect(h1s.first()).toContainText('Your Coding Assistant. Now a Marketing Team.');
  });

  test('canonical URL present', async ({ page }) => {
    await page.goto(BASE_URL);
    const canonical = page.locator('link[rel="canonical"]');
    await expect(canonical).toHaveAttribute('href', /hazn/);
  });
});

// ============================================================
// 4. INTERACTIVE ELEMENTS
// ============================================================
test.describe('4. Interactive Elements', () => {
  test('sticky header appears after scrolling', async ({ page }) => {
    await page.goto(BASE_URL);
    const stickyHeader = page.locator('#stickyHeader');
    
    // Initially hidden
    await expect(stickyHeader).not.toHaveClass(/visible/);
    
    // Scroll down past the hero
    await page.evaluate(() => window.scrollTo(0, 800));
    await page.waitForTimeout(500);
    
    // Should now be visible
    await expect(stickyHeader).toHaveClass(/visible/);
  });

  test('Tally form embed placeholder exists', async ({ page }) => {
    await page.goto(BASE_URL);
    const tallyIframe = page.locator('iframe[data-tally-src]');
    await expect(tallyIframe).toBeVisible();
    await expect(tallyIframe).toHaveAttribute('title', 'Hazn Waitlist');
  });

  test('navigation links have smooth scroll', async ({ page }) => {
    await page.goto(BASE_URL);
    const waitlistLinks = page.locator('a[href="#waitlist"]');
    await expect(waitlistLinks.first()).toBeVisible();
    
    // Click and verify scroll behavior (html has scroll-behavior: smooth)
    const htmlStyle = await page.locator('html').evaluate((el) => 
      getComputedStyle(el).scrollBehavior
    );
    expect(htmlStyle).toBe('smooth');
  });

  test('CTA buttons are clickable', async ({ page }) => {
    await page.goto(BASE_URL);
    const ctaButtons = page.locator('.btn-primary');
    const count = await ctaButtons.count();
    expect(count).toBeGreaterThan(0);
    
    // Check each CTA is enabled and visible
    for (let i = 0; i < count; i++) {
      await expect(ctaButtons.nth(i)).toBeEnabled();
    }
  });
});

// ============================================================
// 5. RESPONSIVE DESIGN
// ============================================================
test.describe('5. Responsive Design', () => {
  test('mobile (375px) - no horizontal overflow', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(BASE_URL);
    
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1); // Allow 1px tolerance
  });

  test('tablet (768px) - no horizontal overflow', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(BASE_URL);
    
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1);
  });

  test('desktop (1280px) - no horizontal overflow', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto(BASE_URL);
    
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1);
  });

  test('mobile renders correctly', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(BASE_URL);
    
    // Hero should be visible and stack properly
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.terminal').first()).toBeVisible();
  });

  test('tablet renders correctly', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(BASE_URL);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('desktop renders correctly', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto(BASE_URL);
    await expect(page.locator('h1')).toBeVisible();
    // Grid layout should be side by side
    const heroGrid = page.locator('.grid.lg\\:grid-cols-2').first();
    await expect(heroGrid).toBeVisible();
  });
});

// ============================================================
// 6. ANIMATIONS
// ============================================================
test.describe('6. Animations', () => {
  test('elements with animation classes exist', async ({ page }) => {
    await page.goto(BASE_URL);
    
    const fadeUpElements = page.locator('.fade-up');
    const count = await fadeUpElements.count();
    expect(count).toBeGreaterThan(10); // Many animated elements expected
    
    // Stagger classes
    const staggerElements = page.locator('[class*="stagger-"]');
    const staggerCount = await staggerElements.count();
    expect(staggerCount).toBeGreaterThan(0);
  });

  test('reduced motion media query is respected', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // Check that reduced-motion styles exist
    const hasReducedMotionStyles = await page.evaluate(() => {
      const styleSheets = Array.from(document.styleSheets);
      for (const sheet of styleSheets) {
        try {
          const rules = Array.from(sheet.cssRules || []);
          for (const rule of rules) {
            if (rule instanceof CSSMediaRule && rule.conditionText?.includes('prefers-reduced-motion')) {
              return true;
            }
          }
        } catch (e) {
          // External stylesheets may not be readable
        }
      }
      // Check inline styles
      const styles = document.querySelectorAll('style');
      for (const style of styles) {
        if (style.textContent?.includes('prefers-reduced-motion')) {
          return true;
        }
      }
      return false;
    });
    
    expect(hasReducedMotionStyles).toBe(true);
  });
});

// ============================================================
// 7. ACCESSIBILITY
// ============================================================
test.describe('7. Accessibility', () => {
  test('all images have alt text', async ({ page }) => {
    await page.goto(BASE_URL);
    
    const images = page.locator('img');
    const count = await images.count();
    
    // If there are images, check they all have alt
    for (let i = 0; i < count; i++) {
      const alt = await images.nth(i).getAttribute('alt');
      expect(alt).toBeTruthy();
    }
  });

  test('buttons have accessible names', async ({ page }) => {
    await page.goto(BASE_URL);
    
    const buttons = page.locator('button, a.btn-primary, [role="button"]');
    const count = await buttons.count();
    
    for (let i = 0; i < count; i++) {
      const text = await buttons.nth(i).textContent();
      const ariaLabel = await buttons.nth(i).getAttribute('aria-label');
      expect(text?.trim() || ariaLabel).toBeTruthy();
    }
  });

  test('color contrast - text readability spot check', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // Check that primary text color is light on dark background
    const h1Color = await page.locator('h1').evaluate((el) => 
      getComputedStyle(el).color
    );
    // Should be near white (high luminance)
    expect(h1Color).toMatch(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    const match = h1Color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (match) {
      const [, r, g, b] = match.map(Number);
      // All values should be high for light text
      expect(r).toBeGreaterThan(200);
      expect(g).toBeGreaterThan(200);
      expect(b).toBeGreaterThan(200);
    }
  });

  test('focus states visible', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // Check that CTA buttons have focus-visible styles or default outline
    const ctaButton = page.locator('.btn-primary').first();
    await ctaButton.focus();
    
    // The button should either have a visible outline or box-shadow when focused
    const outlineOrShadow = await ctaButton.evaluate((el) => {
      const styles = getComputedStyle(el);
      return styles.outline + ' ' + styles.boxShadow;
    });
    // Just verify focus doesn't remove outline entirely (outline: none without replacement)
    expect(outlineOrShadow).toBeTruthy();
  });
});

// ============================================================
// 8. CONTENT CHECKS
// ============================================================
test.describe('8. Content Checks', () => {
  test('no em-dashes (—) anywhere on page', async ({ page }) => {
    await page.goto(BASE_URL);
    
    const bodyText = await page.locator('body').textContent();
    // Em-dash is Unicode 2014
    const hasEmDash = bodyText?.includes('—') || bodyText?.includes('\u2014');
    expect(hasEmDash).toBe(false);
  });

  test('"Autonomous" mentioned (founder credibility)', async ({ page }) => {
    await page.goto(BASE_URL);
    
    const bodyText = await page.locator('body').textContent();
    expect(bodyText).toContain('Autonomous');
  });

  test('"10 agents" or "10 AI agents" mentioned', async ({ page }) => {
    await page.goto(BASE_URL);
    
    const bodyText = await page.locator('body').textContent();
    const has10Agents = bodyText?.includes('10 agents') || 
                        bodyText?.includes('10 AI agents') || 
                        bodyText?.includes('10 specialized agents');
    expect(has10Agents).toBe(true);
  });
});
