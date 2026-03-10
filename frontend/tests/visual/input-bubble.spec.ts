import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const SCREENSHOT_DIR = join(__dirname, 'screenshots');
const BASELINE_DIR = join(SCREENSHOT_DIR, 'baseline');
const ACTUAL_DIR = join(SCREENSHOT_DIR, 'actual');
const DIFF_DIR = join(SCREENSHOT_DIR, 'diff');
const PIXELMATCH_THRESHOLD = 0.1;

test.describe('InputBubble Visual Regression Tests', () => {
  
  test.beforeAll(() => {
    [BASELINE_DIR, ACTUAL_DIR, DIFF_DIR].forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  });

  test.beforeEach(async ({ page }) => {
    await page.goto('/chat');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('.input-bubble', { timeout: 5000 });
  });

  const captureAndCompare = async (
    page: Page,
    name: string,
    selector: string = '.input-bubble'
  ) => {
    const baselinePath = join(BASELINE_DIR, `${name}.png`);
    const actualPath = join(ACTUAL_DIR, `${name}.png`);
    const diffPath = join(DIFF_DIR, `${name}-diff.png`);

    const element = await page.$(selector);
    expect(element).toBeTruthy();

    const screenshot = await element?.screenshot({ type: 'png' });
    fs.writeFileSync(actualPath, screenshot!);

    if (!fs.existsSync(baselinePath)) {
      fs.writeFileSync(baselinePath, screenshot!);
      console.log(`Created baseline: ${name}`);
      return { diffPixels: 0, diffPercentage: 0, passed: true };
    }

    const baselineImg = PNG.sync.read(fs.readFileSync(baselinePath));
    const actualImg = PNG.sync.read(fs.readFileSync(actualPath));
    const { width, height } = baselineImg;
    const diff = new PNG({ width, height });

    const diffPixels = pixelmatch(
      baselineImg.data,
      actualImg.data,
      diff.data,
      width,
      height,
      { threshold: PIXELMATCH_THRESHOLD }
    );

    const diffPercentage = (diffPixels / (width * height)) * 100;
    const passed = diffPercentage <= PIXELMATCH_THRESHOLD;

    if (!passed) {
      fs.writeFileSync(diffPath, PNG.sync.write(diff));
      console.log(`Diff saved: ${name}-diff.png`);
    }

    return { diffPixels, diffPercentage, passed };
  };

  test('Light theme - Default state', async ({ page }) => {
    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
    });
    await page.waitForTimeout(500);

    const result = await captureAndCompare(page, 'light-default');
    expect(result.passed, 
      `Difference: ${result.diffPercentage.toFixed(2)}% (${result.diffPixels} pixels)`).toBeTruthy();
  });

  test('Light theme - Focus state', async ({ page }) => {
    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
    });
    await page.waitForTimeout(500);

    const textarea = await page.$('textarea');
    await textarea?.focus();
    await page.waitForTimeout(300);

    const result = await captureAndCompare(page, 'light-focus');
    expect(result.passed,
      `Difference: ${result.diffPercentage.toFixed(2)}% (${result.diffPixels} pixels)`).toBeTruthy();
  });

  test('Light theme - Typing state', async ({ page }) => {
    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
    });
    await page.waitForTimeout(500);

    const textarea = await page.$('textarea');
    await textarea?.fill('typing test');
    await page.waitForTimeout(200);

    const result = await captureAndCompare(page, 'light-typing');
    expect(result.passed,
      `Difference: ${result.diffPercentage.toFixed(2)}% (${result.diffPixels} pixels)`).toBeTruthy();
  });

  test('Dark theme - Default state', async ({ page }) => {
    await page.evaluate(() => {
      document.documentElement.classList.add('dark');
    });
    await page.waitForTimeout(500);

    const result = await captureAndCompare(page, 'dark-default');
    expect(result.passed,
      `Difference: ${result.diffPercentage.toFixed(2)}% (${result.diffPixels} pixels)`).toBeTruthy();
  });

  test('Dark theme - Focus state', async ({ page }) => {
    await page.evaluate(() => {
      document.documentElement.classList.add('dark');
    });
    await page.waitForTimeout(500);

    const textarea = await page.$('textarea');
    await textarea?.focus();
    await page.waitForTimeout(300);

    const result = await captureAndCompare(page, 'dark-focus');
    expect(result.passed,
      `Difference: ${result.diffPercentage.toFixed(2)}% (${result.diffPixels} pixels)`).toBeTruthy();
  });

  test('Dark theme - Typing state', async ({ page }) => {
    await page.evaluate(() => {
      document.documentElement.classList.add('dark');
    });
    await page.waitForTimeout(500);

    const textarea = await page.$('textarea');
    await textarea?.fill('typing test');
    await page.waitForTimeout(200);

    const result = await captureAndCompare(page, 'dark-typing');
    expect(result.passed,
      `Difference: ${result.diffPercentage.toFixed(2)}% (${result.diffPixels} pixels)`).toBeTruthy();
  });

  test('Hover state - Light theme', async ({ page }) => {
    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
    });
    await page.waitForTimeout(500);

    const bubble = await page.$('.input-bubble');
    await bubble?.hover();
    await page.waitForTimeout(200);

    const result = await captureAndCompare(page, 'light-hover');
    expect(result.passed,
      `Difference: ${result.diffPercentage.toFixed(2)}% (${result.diffPixels} pixels)`).toBeTruthy();
  });

  test('Hover state - Dark theme', async ({ page }) => {
    await page.evaluate(() => {
      document.documentElement.classList.add('dark');
    });
    await page.waitForTimeout(500);

    const bubble = await page.$('.input-bubble');
    await bubble?.hover();
    await page.waitForTimeout(200);

    const result = await captureAndCompare(page, 'dark-hover');
    expect(result.passed,
      `Difference: ${result.diffPercentage.toFixed(2)}% (${result.diffPixels} pixels)`).toBeTruthy();
  });

  test('Responsive - Mobile viewport (375px)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
    });
    await page.waitForTimeout(500);

    const result = await captureAndCompare(page, 'mobile-light-default');
    expect(result.passed,
      `Difference: ${result.diffPercentage.toFixed(2)}% (${result.diffPixels} pixels)`).toBeTruthy();
  });

  test('Responsive - Tablet viewport (768px)', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
    });
    await page.waitForTimeout(500);

    const result = await captureAndCompare(page, 'tablet-light-default');
    expect(result.passed,
      `Difference: ${result.diffPercentage.toFixed(2)}% (${result.diffPixels} pixels)`).toBeTruthy();
  });

  test('Responsive - Desktop viewport (1920px)', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
    });
    await page.waitForTimeout(500);

    const result = await captureAndCompare(page, 'desktop-light-default');
    expect(result.passed,
      `Difference: ${result.diffPercentage.toFixed(2)}% (${result.diffPixels} pixels)`).toBeTruthy();
  });

  test('Performance - 60fps animation check', async ({ page }) => {
    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
    });
    await page.waitForTimeout(500);

    const textarea = await page.$('textarea');
    await textarea?.focus();
    await page.waitForTimeout(300);

    const fps = await page.evaluate(() => {
      return new Promise((resolve) => {
        let frames = 0;
        let startTime = performance.now();
        
        const measureFPS = () => {
          frames++;
          const elapsed = performance.now() - startTime;
          if (elapsed < 1000) {
            requestAnimationFrame(measureFPS);
          } else {
            resolve(Math.round((frames / elapsed) * 1000));
          }
        };
        
        measureFPS();
      });
    });

    expect(fps).toBeGreaterThanOrEqual(55);
    console.log(`Animation FPS: ${fps}`);
  });
});

test.afterAll(() => {
  console.log('\n=== Visual Regression Test Summary ===');
  console.log(`Screenshots saved to: ${SCREENSHOT_DIR}`);
  console.log(`Baseline: ${BASELINE_DIR}`);
  console.log(`Actual: ${ACTUAL_DIR}`);
  console.log(`Diffs: ${DIFF_DIR}`);
});
