/** 4px base unit. All spacing values are multiples of 4. */
export const spacing = {
  base: 4,
  scale: [4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96] as const,
} as const;

export const motion = {
  duration: {
    fast: 100,
    normal: 200,
    slow: 350,
    crawl: 500,
  },
  easing: {
    outExpo: 'cubic-bezier(0.16, 1, 0.3, 1)',
    inExpo: 'cubic-bezier(0.7, 0, 0.84, 0)',
  },
} as const;
