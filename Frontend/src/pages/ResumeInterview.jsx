import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { CheckCircle2, FileText, Play, RefreshCw, Sparkles, UploadCloud, X } from 'lucide-react';
import { generateResumeQuestions, uploadResume } from '../services/api.js';
import { scoreAnswerLocally } from '../services/scoring.js';
import { cap } from '../services/insights.js';
import { useAuth } from '../context/AuthContext.jsx';
import { useToast } from '../context/ToastContext.jsx';
import Button from '../components/Button.jsx';
import InterviewRunner from '../components/InterviewRunner.jsx';
import { ProgressBar } from '../components/ScoreCard.jsx';

const MAX_BYTES = 5 * 1024 * 1024; // same limit the backend enforces
const STEPS = ['Upload', 'Questions', 'Interview'];
const STEP_INDEX = { upload: 0, configure: 1, preview: 1, running: 2 };

function readStoredResume() {
  try { return JSON.parse(sessionStorage.getItem('ais_resume') || 'null'); } catch { return null; }
}

function validateFile(file) {
  if (!file) return 'No file selected.';
  if (!file.name.toLowerCase().endsWith('.pdf')) return 'Only PDF files are supported.';
  if (file.size === 0) return 'The selected file is empty.';
  if (file.size > MAX_BYTES) return 'Resume must be smaller than 5 MB.';
  return '';
}

export default function ResumeInterview() {
  const { user, logout } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const inputRef = useRef(null);

  const [resume, setResume] = useState(readStoredResume); // { resume_id, filename, characters }
  const [step, setStep] = useState(() => (readStoredResume() ? 'configure' : 'upload'));
  const [file, setFile] = useState(null);
  const [fileError, setFileError] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [pct, setPct] = useState(0);
  const [count, setCount] = useState(5);
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated] = useState(null); // { questions, skills }
  const [run, setRun] = useState({ index: 0, answers: [] });

  const pickFile = (f) => {
    const problem = validateFile(f);
    if (problem) {
      setFile(null);
      setFileError(problem);
      toast.error(problem);
      return;
    }
    setFileError('');
    setFile(f);
  };

  /** The backend answers 404 "User not found. Please log in again." for unknown users. */
  const handleAuthError = (err) => {
    if (err.status === 404 && /log in/i.test(err.message)) {
      toast.error(err.message);
      logout();
      navigate('/login', { replace: true });
      return true;
    }
    return false;
  };

  const upload = async () => {
    if (!file || uploading) return;
    setUploading(true);
    setPct(0);
    try {
      const res = await uploadResume(user.user_id, file, setPct);
      const info = { resume_id: res.resume_id, filename: res.filename, characters: res.characters_extracted };
      sessionStorage.setItem('ais_resume', JSON.stringify(info));
      setResume(info);
      setFile(null);
      setStep('configure');
      toast.success('Resume uploaded and text extracted.');
    } catch (err) {
      if (!handleAuthError(err)) {
        setFileError(err.message);
        toast.error(err.message);
      }
    } finally {
      setUploading(false);
    }
  };

  const generate = async () => {
    if (generating || !resume) return;
    setGenerating(true);
    try {
      const res = await generateResumeQuestions({ userId: user.user_id, resumeId: resume.resume_id, numQuestions: count });
      setGenerated({ questions: res.questions, skills: res.detected_skills || [] });
      setStep('preview');
    } catch (err) {
      if (err.status === 404 && /resume not found/i.test(err.message)) {
        sessionStorage.removeItem('ais_resume');
        setResume(null);
        setStep('upload');
        toast.error('That resume is no longer available. Please upload it again.');
      } else if (!handleAuthError(err)) {
        toast.error(err.message);
      }
    } finally {
      setGenerating(false);
    }
  };

  const changeResume = () => {
    sessionStorage.removeItem('ais_resume');
    setResume(null);
    setGenerated(null);
    setStep('upload');
  };

  // ---------- interview (scored in the browser, see services/scoring.js) ----------
  if (step === 'running' && generated) {
    const { questions } = generated;
    const q = questions[run.index];

    const handleSubmit = async (answer) => {
      const result = scoreAnswerLocally(answer, q);
      setRun((r) => ({ ...r, answers: [...r.answers, { question: q.question, user_answer: answer, ...result }] }));
      return result;
    };
    const handleNext = async () => setRun((r) => ({ ...r, index: r.index + 1 }));
    const handleFinish = async () => {
      const answers = run.answers;
      const total = answers.reduce((sum, a) => sum + a.score, 0);
      const result = {
        topic: 'Resume',
        difficulty: 'mixed',
        total_score: total,
        average_score: Math.floor(total / Math.max(answers.length, 1)),
        answers,
        total_questions: questions.length,
        source: 'local',
        filename: resume?.filename,
      };
      sessionStorage.setItem('ais_resume_result', JSON.stringify(result));
      navigate('/results/resume');
    };

    return (
      <div className="stack">
        <p className="muted small">
          Resume interviews are scored in your browser with the same keyword rule the backend uses for topic interviews.
        </p>
        <InterviewRunner
          key={run.index + 1}
          number={run.index + 1}
          total={questions.length}
          question={q}
          isLast={run.index + 1 >= questions.length}
          answeredCount={run.answers.length}
          onSubmit={handleSubmit}
          onNext={handleNext}
          onFinish={handleFinish}
        />
      </div>
    );
  }

  return (
    <div className="stack-lg">
      <header>
        <h1 className="page-title">Resume-Based Interview</h1>
        <p className="muted">Upload your resume and practise questions generated from its content.</p>
      </header>

      <ol className="stepper" aria-label="Progress">
        {STEPS.map((label, i) => (
          <li key={label} className={`step${i === STEP_INDEX[step] ? ' current' : ''}${i < STEP_INDEX[step] ? ' done' : ''}`}>
            <span className="step-dot">{i < STEP_INDEX[step] ? <CheckCircle2 size={16} /> : i + 1}</span>
            {label}
          </li>
        ))}
      </ol>

      <AnimatePresence mode="wait">
        {step === 'upload' && (
          <motion.div key="upload" className="card stack" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <div
              className={`dropzone${dragOver ? ' over' : ''}${fileError ? ' invalid' : ''}`}
              role="button"
              tabIndex={0}
              aria-label="Upload a PDF resume"
              onClick={() => inputRef.current?.click()}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  inputRef.current?.click();
                }
              }}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); pickFile(e.dataTransfer.files?.[0]); }}
            >
              <UploadCloud size={34} />
              <p><strong>Drag &amp; drop your resume</strong> or click to browse</p>
              <p className="muted small">PDF only · max 5 MB · must contain selectable text (not a scan)</p>
              <input
                ref={inputRef}
                type="file"
                accept="application/pdf,.pdf"
                hidden
                onChange={(e) => { pickFile(e.target.files?.[0]); e.target.value = ''; }}
              />
            </div>

            {fileError && <p className="field-error" role="alert">{fileError}</p>}

            {file && (
              <div className="file-chip">
                <FileText size={18} />
                <span className="file-name">{file.name}</span>
                <span className="muted small">{(file.size / 1024).toFixed(0)} KB</span>
                {!uploading && (
                  <button type="button" className="icon-btn" onClick={() => setFile(null)} aria-label="Remove selected file">
                    <X size={16} />
                  </button>
                )}
              </div>
            )}

            {uploading && (
              <div className="stack-sm">
                <ProgressBar value={pct} label="Upload progress" />
                <p className="muted small">{pct < 100 ? `Uploading… ${pct}%` : 'Extracting text from your resume…'}</p>
              </div>
            )}

            <div className="row-end">
              <Button icon={UploadCloud} loading={uploading} disabled={!file} onClick={upload}>
                {uploading ? 'Uploading…' : 'Upload resume'}
              </Button>
            </div>
          </motion.div>
        )}

        {step === 'configure' && resume && (
          <motion.div key="configure" className="card stack" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <div className="file-chip success">
              <CheckCircle2 size={18} />
              <span className="file-name">{resume.filename}</span>
              {resume.characters != null && <span className="muted small">{resume.characters.toLocaleString()} characters extracted</span>}
            </div>

            <div className="stack-sm">
              <h2 className="section-title">Number of questions: <span className="accent">{count}</span></h2>
              <input type="range" min={1} max={10} value={count} onChange={(e) => setCount(Number(e.target.value))} className="range" aria-label="Number of questions" />
              <div className="row-between muted small"><span>1</span><span>10</span></div>
              <p className="muted small">The number actually generated depends on how many skills and topics the resume contains.</p>
            </div>

            <div className="row-between">
              <Button variant="ghost" icon={RefreshCw} onClick={changeResume} disabled={generating}>Use a different resume</Button>
              <Button icon={Sparkles} loading={generating} onClick={generate}>
                {generating ? 'Generating…' : 'Generate questions'}
              </Button>
            </div>
          </motion.div>
        )}

        {step === 'preview' && generated && (
          <motion.div key="preview" className="card stack" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            {generated.skills.length > 0 && (
              <div className="stack-sm">
                <h2 className="section-title">Skills detected in your resume</h2>
                <div className="chips">{generated.skills.map((s) => <span key={s} className="chip">{s}</span>)}</div>
              </div>
            )}

            <div className="stack-sm">
              <h2 className="section-title">{generated.questions.length} generated question{generated.questions.length === 1 ? '' : 's'}</h2>
              <ol className="q-list">
                {generated.questions.map((q, i) => (
                  <motion.li key={q.question} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}>
                    <span>{q.question}</span>
                    <span className="badge badge-soft">{cap(q.difficulty)}</span>
                  </motion.li>
                ))}
              </ol>
            </div>

            <div className="row-between">
              <Button variant="ghost" icon={RefreshCw} onClick={() => setStep('configure')}>Regenerate</Button>
              <Button icon={Play} onClick={() => { setRun({ index: 0, answers: [] }); setStep('running'); }}>
                Start Interview
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
