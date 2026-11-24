
import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Code2,
  Send,
  Terminal,
  RotateCcw,
  Loader2,
  CheckCircle,
  XCircle,
  Plus,
  Trash2,
} from 'lucide-react';

import { runCode } from '../services/api';

const problems = [
  {
    id: 1,
    title: 'Two Sum',
    difficulty: 'Easy',
    description:
      'Given an array of integers and a target, return the indices of two numbers that add up to the target.',
    input: 'nums = [2, 7, 11, 15], target = 9',
    output: '[0, 1]',
  },
  {
    id: 2,
    title: 'Reverse a String',
    difficulty: 'Easy',
    description:
      'Given a string, reverse it and return the reversed string.',
    input: 'hello',
    output: 'olleh',
  },
  {
    id: 3,
    title: 'Find Maximum',
    difficulty: 'Easy',
    description:
      'Given an integer array, find and return the largest element.',
    input: '[10, 25, 8, 42, 15]',
    output: '42',
  },
];

const starterCode = {
  Java: `public class Main {
    public static void main(String[] args) {
        // Write your code here

    }
}`,
  Python: `def solution():
    # Write your code here
    pass

solution()`,
  'C++': `#include <iostream>
using namespace std;

int main() {
    // Write your code here

    return 0;
}`,
};

const languageMap = {
  Java: 'java',
  Python: 'python',
  'C++': 'cpp',
};

export default function CodingArena() {
  const [language, setLanguage] = useState('Java');
  const [problemIndex, setProblemIndex] = useState(0);
  const [code, setCode] = useState(starterCode.Java);

  const [testCases, setTestCases] = useState([
    { input: '', expected_output: '' },
    { input: '', expected_output: '' },
  ]);

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const problem = problems[problemIndex];

  const changeLanguage = (value) => {
    setLanguage(value);
    setCode(starterCode[value]);
    setResult(null);
  };

  const changeProblem = (index) => {
    setProblemIndex(index);
    setTestCases([
      { input: '', expected_output: '' },
      { input: '', expected_output: '' },
    ]);
    setResult(null);
  };

  const resetCode = () => {
    setCode(starterCode[language]);
    setTestCases([
      { input: '', expected_output: '' },
      { input: '', expected_output: '' },
    ]);
    setResult(null);
  };

  const addTestCase = () => {
    if (testCases.length >= 10) {
      alert('Maximum 10 test cases allowed.');
      return;
    }

    setTestCases([
      ...testCases,
      { input: '', expected_output: '' },
    ]);

    setResult(null);
  };

  const removeTestCase = (index) => {
    if (testCases.length <= 1) {
      alert('At least one test case is required.');
      return;
    }

    setTestCases(testCases.filter((_, i) => i !== index));
    setResult(null);
  };

  const updateTestCase = (index, field, value) => {
    setTestCases((previous) =>
      previous.map((testCase, i) =>
        i === index
          ? { ...testCase, [field]: value }
          : testCase
      )
    );

    setResult(null);
  };

  const submitCode = async () => {
    if (!code.trim()) {
      setResult({
        status: 'error',
        verdict: 'Invalid Submission',
        output: '',
        error: 'Please write some code before submitting.',
      });
      return;
    }

    const validTestCases = testCases.filter(
      (testCase) => testCase.expected_output.trim() !== ''
    );

    if (validTestCases.length === 0) {
      setResult({
        status: 'error',
        verdict: 'Invalid Test Cases',
        output: '',
        error: 'Please enter expected output for at least one test case.',
      });
      return;
    }

    try {
      setLoading(true);
      setResult(null);

      const response = await runCode(
        languageMap[language],
        code,
        '',
        null,
        validTestCases
      );

      setResult(response.data || response);
    } catch (error) {
      setResult({
        status: 'error',
        verdict: 'Execution Error',
        output: '',
        error:
          error.response?.data?.detail ||
          error.message ||
          'Code execution failed.',
      });
    } finally {
      setLoading(false);
    }
  };

  const verdict = result?.verdict || result?.status || 'Unknown';

  const isAccepted = verdict === 'Accepted';
  const isExecuted = verdict === 'Executed';
  const isTimeout = verdict === 'Time Limit Exceeded';

  return (
    <div className="page space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-600">
            <Code2 size={22} />
            <span className="text-sm font-semibold">PRACTICE ZONE</span>
          </div>

          <h1 className="text-3xl font-bold mt-2">Coding Arena</h1>

          <p className="text-slate-500 mt-1">
            Solve coding challenges and improve your problem-solving skills.
          </p>
        </div>

        <div className="card flex items-center gap-3 px-4 py-3">
          <Terminal className="text-indigo-600" />
          <div>
            <p className="text-sm font-semibold">Coding Practice</p>
            <p className="text-xs text-slate-500">Beginner level</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="card space-y-5"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-500">
              Problem {problemIndex + 1} of {problems.length}
            </span>

            <span className="text-xs font-semibold px-3 py-1 rounded-full bg-green-100 text-green-700">
              {problem.difficulty}
            </span>
          </div>

          <div className="flex gap-2">
            {problems.map((item, index) => (
              <button
                key={item.id}
                onClick={() => changeProblem(index)}
                disabled={loading}
                className={`px-3 py-2 rounded-lg text-sm ${
                  index === problemIndex
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-100 text-slate-600'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>

          <div>
            <h2 className="text-xl font-bold">{problem.title}</h2>

            <p className="text-slate-600 mt-3 leading-7">
              {problem.description}
            </p>
          </div>

          <div className="space-y-3">
            <div>
              <p className="font-semibold text-sm mb-2">Example Input</p>
              <pre className="bg-slate-100 rounded-lg p-3 text-sm whitespace-pre-wrap">
                {problem.input}
              </pre>
            </div>

            <div>
              <p className="font-semibold text-sm mb-2">Expected Output</p>
              <pre className="bg-slate-100 rounded-lg p-3 text-sm">
                {problem.output}
              </pre>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="card space-y-4"
        >
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="font-bold text-lg flex items-center gap-2">
              <Code2 size={20} className="text-indigo-600" />
              Code Editor
            </h2>

            <select
              value={language}
              onChange={(e) => changeLanguage(e.target.value)}
              className="border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white"
              disabled={loading}
            >
              <option value="Java">Java</option>
              <option value="Python">Python</option>
              <option value="C++">C++</option>
            </select>
          </div>

          <textarea
            value={code}
            onChange={(e) => {
              setCode(e.target.value);
              setResult(null);
            }}
            spellCheck="false"
            disabled={loading}
            className="w-full min-h-[350px] bg-slate-950 text-green-300 rounded-xl p-4 font-mono text-sm outline-none resize-y"
            placeholder="Write your code here..."
          />

          {/* Multiple Test Cases */}
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="font-bold text-lg">
                Test Cases ({testCases.length}/10)
              </h3>

              <button
                onClick={addTestCase}
                disabled={loading || testCases.length >= 10}
                className="px-3 py-2 rounded-lg bg-indigo-600 text-white flex items-center gap-2 text-sm disabled:opacity-50"
              >
                <Plus size={16} />
                Add Test Case
              </button>
            </div>

            {testCases.map((testCase, index) => (
              <div
                key={index}
                className="border border-slate-200 rounded-xl p-4 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <p className="font-semibold text-sm">
                    Test Case {index + 1}
                  </p>

                  <button
                    onClick={() => removeTestCase(index)}
                    disabled={loading || testCases.length <= 1}
                    className="text-red-500 hover:text-red-700 disabled:opacity-40"
                    title="Remove test case"
                  >
                    <Trash2 size={17} />
                  </button>
                </div>

                <div>
                  <label className="font-semibold text-sm mb-2 block">
                    Custom Input (stdin)
                  </label>

                  <textarea
                    value={testCase.input}
                    onChange={(e) =>
                      updateTestCase(index, 'input', e.target.value)
                    }
                    disabled={loading}
                    rows={2}
                    className="w-full bg-slate-100 rounded-lg p-3 text-sm font-mono outline-none resize-y"
                    placeholder="Enter input..."
                  />
                </div>

                <div>
                  <label className="font-semibold text-sm mb-2 block">
                    Expected Output
                  </label>

                  <textarea
                    value={testCase.expected_output}
                    onChange={(e) =>
                      updateTestCase(
                        index,
                        'expected_output',
                        e.target.value
                      )
                    }
                    disabled={loading}
                    rows={2}
                    className="w-full bg-slate-100 rounded-lg p-3 text-sm font-mono outline-none resize-y"
                    placeholder="Enter expected output..."
                  />
                </div>
              </div>
            ))}
          </div>

          <p className="text-xs text-slate-500">
            Add multiple test cases. All expected outputs must be entered
            before submission.
          </p>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={resetCode}
              disabled={loading}
              className="px-4 py-2 rounded-lg border border-slate-300 flex items-center gap-2 text-sm disabled:opacity-50"
            >
              <RotateCcw size={16} />
              Reset
            </button>

            <button
              onClick={submitCode}
              disabled={loading}
              className="px-5 py-2 rounded-lg bg-indigo-600 text-white flex items-center gap-2 text-sm disabled:opacity-60"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Send size={16} />
                  Submit Code
                </>
              )}
            </button>
          </div>

          {/* Overall Result */}
          {result && (
            <div
              className={`rounded-lg border p-4 space-y-3 ${
                isAccepted
                  ? 'bg-green-50 border-green-200'
                  : isExecuted
                  ? 'bg-blue-50 border-blue-200'
                  : isTimeout
                  ? 'bg-amber-50 border-amber-200'
                  : 'bg-red-50 border-red-200'
              }`}
            >
              <div
                className={`flex items-center gap-2 font-semibold ${
                  isAccepted
                    ? 'text-green-700'
                    : isExecuted
                    ? 'text-blue-700'
                    : isTimeout
                    ? 'text-amber-700'
                    : 'text-red-700'
                }`}
              >
                {isAccepted || isExecuted ? (
                  <CheckCircle size={18} />
                ) : (
                  <XCircle size={18} />
                )}

                Verdict: {verdict}
              </div>

              {result.passed_count !== undefined && (
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="bg-white rounded-lg p-3">
                    <p className="text-xl font-bold text-slate-800">
                      {result.total_test_cases}
                    </p>
                    <p className="text-xs text-slate-500">Total</p>
                  </div>

                  <div className="bg-white rounded-lg p-3">
                    <p className="text-xl font-bold text-green-600">
                      {result.passed_count}
                    </p>
                    <p className="text-xs text-slate-500">Passed</p>
                  </div>

                  <div className="bg-white rounded-lg p-3">
                    <p className="text-xl font-bold text-red-600">
                      {result.failed_count}
                    </p>
                    <p className="text-xs text-slate-500">Failed</p>
                  </div>
                </div>
              )}

              {/* Individual Test Results */}
              {result.test_results?.map((test, index) => (
                <div
                  key={index}
                  className="bg-white border border-slate-200 rounded-lg p-3 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <p className="font-semibold text-sm">
                      Test Case {test.test_case}
                    </p>

                    <span
                      className={`text-xs font-semibold ${
                        test.verdict === 'Accepted'
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}
                    >
                      {test.verdict}
                    </span>
                  </div>

                  <div>
                    <p className="text-xs font-semibold text-slate-500 mb-1">
                      Expected Output
                    </p>
                    <pre className="bg-slate-100 rounded p-2 text-sm whitespace-pre-wrap">
                      {test.expected_output}
                    </pre>
                  </div>

                  <div>
                    <p className="text-xs font-semibold text-slate-500 mb-1">
                      Your Output
                    </p>
                    <pre className="bg-slate-950 text-green-300 rounded p-2 text-sm whitespace-pre-wrap overflow-x-auto">
                      {test.output || '(No output)'}
                    </pre>
                  </div>

                  {test.error && (
                    <pre className="bg-red-50 text-red-700 rounded p-2 text-xs whitespace-pre-wrap">
                      {test.error}
                    </pre>
                  )}
                </div>
              ))}

              {result.error && !result.test_results?.length && (
                <div>
                  <p className="text-sm font-semibold mb-1">Error Details</p>
                  <pre className="bg-slate-950 text-red-300 rounded-lg p-3 text-sm whitespace-pre-wrap overflow-x-auto">
                    {result.error}
                  </pre>
                </div>
              )}

              {isExecuted && (
                <p className="text-sm text-blue-700">
                  Code executed successfully. Answer validation was skipped.
                </p>
              )}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
