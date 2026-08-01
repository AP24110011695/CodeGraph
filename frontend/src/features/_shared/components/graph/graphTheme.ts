/** Language / type → minimap + indicator colors (Carbon + Amber palette). */
export function languagePaletteColor(languageOrType: string): string {
  const key = languageOrType.toLowerCase();
  if (key.includes('python')) return '#E8A045';
  if (key.includes('typescript') || key.includes('javascript') || key.includes('tsx') || key.includes('jsx')) {
    return '#4F9DFF';
  }
  if (key.includes('css') || key.includes('scss') || key.includes('sass')) return '#4F9DFF';
  if (key.includes('rust')) return '#F28C28';
  if (key.includes('go')) return '#27C6B7';
  if (key.includes('java') && !key.includes('javascript')) return '#FF5C5C';
  if (key.includes('c++') || key.includes('cpp') || key === 'c') return '#8E98A8';
  if (key.includes('security') || key.includes('vulnerab')) return '#FF5C5C';
  if (key.includes('module') || key.includes('package') || key.includes('layer')) return '#E8A045';
  if (key.includes('class') || key.includes('function') || key.includes('method')) return '#4F9DFF';
  if (key.includes('database') || key.includes('schema')) return '#27C6B7';
  return '#B7AB9C';
}

export const MINIMAP_MASK = 'rgba(15, 14, 13, 0.82)';
export const MINIMAP_CLASS =
  '!h-[128px] !w-[200px] !overflow-hidden !rounded-2xl !border !border-border-base/80 ' +
  '!bg-bg-elevated/90 !shadow-xl !backdrop-blur-md transition-transform duration-200 hover:!scale-[1.04]';
