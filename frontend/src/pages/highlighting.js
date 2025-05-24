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

      case '✏️':
        regex = new RegExp(`(?<!\\w)${queryArg}`, 'gi');
        break;

      case '📚': // Sentence starts with – use server pattern (includes ^)
        regex = new RegExp(pattern, 'gi');
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
        // raw-custom word regex: strip ^/$, turn .* → \S*, then force word-bounds
        let raw = queryArg.replace(/^\^/, '').replace(/\$$/, '');
        raw = raw.replace(/\.\*/g, '\\S*');
        // now only match contiguous non-spaces between word-bounds
        regex = new RegExp(`\\b(?:${raw})\\b`, 'gi');
        break
      case '🛠️':
        let clean = pattern.replace(/^\^/, '').replace(/\$$/, '')
        // build a global, case‐insensitive search inside the snippet
        regex = new RegExp(`(${clean})`, 'gi')
        break;

      case '📝':
        regex = new RegExp(queryArg.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&'), 'gi');
        break;

      case '📌': // Sentence ends with (use server-sent pattern)
        regex = new RegExp(pattern, 'gi');
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