import React from "react";

/**
 * Highlights matches of the given pattern (based on emoji/search type) in the text.
 * @param {string} text - The text to highlight within.
 * @param {string} pattern - The regex/string pattern from backend (or frontend constructed).
 * @param {string} emoji - The search mode emoji.
 * @param {string} queryArg - The query argument (pattern after the emoji).
 * @returns {React.ReactNode}
 */
export const highlightMatch = (text, pattern, emoji, queryArg = '') => {
  // Debug output to see what's being passed in
  // Uncomment this to see values every time highlightMatch is called!
  // console.log({ text, pattern, emoji, queryArg });

  let regex = null;

  // Try to make the most reasonable regex from what we've got
  try {
    if (emoji) {
      switch (emoji) {
        case '📄': // Ends with suffix
        case '🖌️': // multi-suffix (e.g. "ing|ed")
          regex = new RegExp(`(${queryArg})\\b`, 'gi');
          break;
        case '✏️': // Starts with prefix
          regex = new RegExp(`(?<!\\w)${escapeRegExp(queryArg)}`, 'gi');
          break;
        case '📚': // Sentence starts with
        case '📌': // Sentence ends with
          regex = new RegExp(pattern, 'gi');
          break;
        case '📂':
          regex = new RegExp(`\\b\\w{${queryArg},}\\b`, 'gi');
          break;
          case '📕':
            regex = new RegExp(`\\b[a-zA-Z]{1,${queryArg}}\\b`, 'gi');
            break;          
        case '📏':
          regex = new RegExp(`\\b\\w{${queryArg}}\\b`, 'gi');
          break;
        case '📎':
          regex = new RegExp(`\\b\\w*?(.)\\1{${parseInt(queryArg) - 1},}\\w*?\\b`, 'gi');
          break;
        case '📖':
        case '🔍':
          regex = new RegExp(`\\b${escapeRegExp(queryArg)}\\b`, 'gi');
          break;
        case '🔧':
          regex = new RegExp(queryArg, 'gi');
          break;
        case '🛠️':
          regex = new RegExp(pattern, 'gi');
          break;
        case '📝':
          regex = new RegExp(escapeRegExp(queryArg), 'gi');
          break;
        case '🖋️':
          regex = new RegExp(queryArg.split(',').map(w => `\\b${escapeRegExp(w.trim())}\\b`).join('|'), 'gi');
          break;
        case '🖍️':
          regex = new RegExp(queryArg, 'gi');
          break;
        default:
          if (pattern) {
            regex = new RegExp(pattern, 'gi');
          }
      }
    } else if (pattern) {
      regex = new RegExp(pattern, 'gi');
    } else if (queryArg) {
      regex = new RegExp(escapeRegExp(queryArg), 'gi');
    } else {
      return text;
    }
  } catch (e) {
    // If regex construction fails, fallback to simple highlighting
    console.error('Regex error:', e);
    if (queryArg) {
      regex = new RegExp(escapeRegExp(queryArg), 'gi');
    } else {
      return text;
    }
  }

  if (!regex) return text;
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
  return <>{parts}</>;
};

// Helper to escape regex special chars
function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
