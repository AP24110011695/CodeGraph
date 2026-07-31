export const typography = {
  fontFamily: {
    sans: '"Geist", ui-sans-serif, system-ui, sans-serif',
    mono: '"Geist Mono", ui-monospace, SFMono-Regular, monospace',
  },
  scale: {
    xs: { fontSize: '11px', lineHeight: '16px' },
    sm: { fontSize: '12px', lineHeight: '18px' },
    base: { fontSize: '14px', lineHeight: '22px' },
    lg: { fontSize: '16px', lineHeight: '24px' },
    xl: { fontSize: '20px', lineHeight: '28px' },
    '2xl': { fontSize: '24px', lineHeight: '32px' },
    '3xl': { fontSize: '30px', lineHeight: '36px' },
  },
} as const;
