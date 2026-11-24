export const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : s);

/** Same bands the backend uses for grades: >=60 good, >=40 fair. */
export const scoreTone = (score) => (score >= 60 ? 'success' : score >= 40 ? 'warning' : 'error');

const topKeywords = (list, n = 6) => {
  const counts = new Map();
  list.forEach((k) => counts.set(k, (counts.get(k) || 0) + 1));
  return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, n).map(([k]) => k);
};

/**
 * Strengths / improvements / next steps are derived ONLY from the per-answer
 * data the backend returns (score, matched_keywords, missed_keywords).
 */
export function buildInsights(answers, average, topic, difficulty) {
  const strong = answers.filter((a) => a.score >= 80).length;
  const weak = answers.filter((a) => a.score < 60).length;
  const matched = topKeywords(answers.flatMap((a) => a.matched_keywords || []));
  const missed = topKeywords(answers.flatMap((a) => a.missed_keywords || []));

  const strengths = [];
  if (strong) strengths.push(`${strong} of ${answers.length} answers scored 80% or higher.`);
  if (matched.length) strengths.push(`Concepts you covered well: ${matched.join(', ')}.`);

  const improvements = [];
  if (weak) improvements.push(`${weak} of ${answers.length} answers scored below 60%.`);
  if (missed.length) improvements.push(`Concepts that were missing: ${missed.join(', ')}.`);

  const next = [];
  if (weak) next.push('Re-read the model answers for your lowest-scoring questions.');
  if (missed.length) next.push(`Practise explaining ${missed.slice(0, 3).join(', ')} in your own words.`);
  if (average >= 80 && difficulty === 'easy') next.push('You are ready to try Medium difficulty.');
  else if (average >= 80 && difficulty === 'medium') next.push('You are ready to try Hard difficulty.');
  else if (average < 60) next.push(`Retry ${topic} after reviewing the gaps above.`);
  else next.push('Run another session to keep improving.');

  return { strengths, improvements, next };
}
