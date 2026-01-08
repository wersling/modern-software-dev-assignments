/**
 * Unit tests for tag color generation
 *
 * Run with: npm test
 */

import { describe, it, expect } from 'vitest';

/**
 * Generate a consistent color based on tag name using simple hash
 */
function getTagColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }

  const hue = Math.abs(hash % 360);
  const saturation = 60 + (Math.abs(hash >> 8) % 20);
  const lightness = 85 + (Math.abs(hash >> 16) % 10);

  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

describe('getTagColor', () => {
  it('should generate valid HSL color strings', () => {
    const color = getTagColor('test');
    expect(color).toMatch(/^hsl\(\d+,\s*\d+%,\s*\d+%\)$/);
  });

  it('should return the same color for the same tag name', () => {
    const color1 = getTagColor('work');
    const color2 = getTagColor('work');
    expect(color1).toBe(color2);
  });

  it('should return different colors for different tag names', () => {
    const color1 = getTagColor('work');
    const color2 = getTagColor('personal');
    const color3 = getTagColor('urgent');
    // At least two should be different
    const uniqueColors = new Set([color1, color2, color3]);
    expect(uniqueColors.size).toBeGreaterThan(1);
  });

  it('should generate colors with valid hue (0-360)', () => {
    const color = getTagColor('test');
    const match = color.match(/hsl\((\d+),/);
    expect(match).toBeTruthy();
    const hue = parseInt(match![1]);
    expect(hue).toBeGreaterThanOrEqual(0);
    expect(hue).toBeLessThan(360);
  });

  it('should generate colors with saturation 60-80%', () => {
    const color = getTagColor('test');
    const match = color.match(/hsl\(\d+,\s*(\d+)%,/);
    expect(match).toBeTruthy();
    const saturation = parseInt(match![1]);
    expect(saturation).toBeGreaterThanOrEqual(60);
    expect(saturation).toBeLessThanOrEqual(80);
  });

  it('should generate colors with lightness 85-95%', () => {
    const color = getTagColor('test');
    const match = color.match(/hsl\(\d+,\s*\d+%,\s*(\d+)%\)/);
    expect(match).toBeTruthy();
    const lightness = parseInt(match![1]);
    expect(lightness).toBeGreaterThanOrEqual(85);
    expect(lightness).toBeLessThanOrEqual(95);
  });

  it('should handle empty string', () => {
    const color = getTagColor('');
    expect(color).toMatch(/^hsl\(\d+,\s*\d+%,\s*\d+%\)$/);
  });

  it('should handle special characters', () => {
    const color = getTagColor('tag-with-special-_chars_123');
    expect(color).toMatch(/^hsl\(\d+,\s*\d+%,\s*\d+%\)$/);
  });

  it('should be case-sensitive', () => {
    const color1 = getTagColor('Work');
    const color2 = getTagColor('work');
    expect(color1).not.toBe(color2);
  });

  it('should generate consistent colors across multiple calls', () => {
    const tagName = 'consistency-test';
    const colors = Array.from({ length: 100 }, () => getTagColor(tagName));
    expect(colors.every((c) => c === colors[0])).toBe(true);
  });
});

describe('Tag Color Distribution', () => {
  it('should generate well-distributed colors for common tags', () => {
    const commonTags = [
      'work',
      'personal',
      'urgent',
      'important',
      'todo',
      'done',
      'meeting',
      'idea',
      'reference',
      'archive'
    ];

    const colors = commonTags.map((tag) => getTagColor(tag));
    const uniqueColors = new Set(colors);

    // At least 80% should be unique
    expect(uniqueColors.size / commonTags.length).toBeGreaterThan(0.8);
  });
});
