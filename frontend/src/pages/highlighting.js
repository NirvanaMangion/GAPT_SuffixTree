// src/pages/highlighting.js
export const highlightMatch = (text, pattern, emoji, queryArg = '') => {
  if (!pattern || !emoji) return text;

  let regex;
  try {
    switch (emoji) {
      case '📄': // Ends with suffix
      case '🖌️':
        regex = new RegExp(`${queryArg}(?!\\w)`, 'gi');
        break;
      case '✏️': // Starts with prefix
      case '🖌️S':
        regex = new RegExp(`(?<!\\w)${queryArg}`, 'gi');
        break;
      case '📂':
        regex = new RegExp(`\\b\\w{${queryArg},}\\b`, 'gi');
        break;
      case '📕':
        regex = new RegExp(`\\b\\w{1,${queryArg}}\\b`, 'gi');
        break;
      case '📏':
        regex = new RegExp(`\\b\\w{${queryArg}}\\b`, 'gi');
        break;
      case '📎':
        regex = new RegExp(`\\b\\w*?(.)\\1{${parseInt(queryArg) - 1},}\\w*?\\b`, 'gi');
        break;
      case '📖':
      case '🔍':
        regex = new RegExp(`\\b${queryArg}\\b`, 'gi');
        break;
      case '🔧':
      case '🔧S':
        regex = new RegExp(queryArg, 'gi');
        break;
      case '📝':
        regex = new RegExp(queryArg.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&'), 'gi');
        break;
      case '📌':
        regex = new RegExp(`${queryArg}(?=\\W*$)`, 'gi');
        break;
      case '🖋️':
        regex = new RegExp(queryArg.split(',').map(w => `\\b${w.trim()}\\b`).join('|'), 'gi');
        break;
      case '🖍️':
        regex = new RegExp(queryArg, 'gi');
        break;
      default:
        regex = new RegExp(pattern, 'gi');
    }
  } catch (e) {
    console.error('Regex error:', e);
    return text;
  }

  const parts = [];
  let lastIndex = 0;

  for (const match of text.matchAll(regex)) {
    const start = match.index;
    const end = start + match[0].length;

    if (start > lastIndex) {
      parts.push(text.slice(lastIndex, start));
    }

    parts.push(
      <span key={start} className="highlight">
        {text.slice(start, end)}
      </span>
    );
    lastIndex = end;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts;
};
