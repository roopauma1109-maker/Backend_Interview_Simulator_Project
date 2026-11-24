/**
 * Resume interviews have no backend evaluation endpoint (POST /interview/answer/{id}
 * only works on server-side sessions created by GET /interview/start).
 * This is a direct port of score_answer() in Backend/main.py so the scoring
 * rule is identical for both interview types.
 */
export function scoreAnswerLocally(userAnswer, question) {
  const keywords = question.keywords || [];
  const lower = userAnswer.toLowerCase();
  const matched = keywords.filter((k) => lower.includes(String(k).toLowerCase()));
  const missed = keywords.filter((k) => !lower.includes(String(k).toLowerCase()));

  const score = keywords.length ? Math.floor((matched.length / keywords.length) * 100) : 50;

  let grade = 'Needs Improvement';
  if (score >= 80) grade = 'Excellent';
  else if (score >= 60) grade = 'Good';
  else if (score >= 40) grade = 'Fair';

  return {
    score,
    grade,
    matched_keywords: matched,
    missed_keywords: missed,
    model_answer: question.answer || '',
  };
}
