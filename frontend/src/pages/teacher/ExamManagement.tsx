import React, { useState } from 'react';
import { 
  FileText, 
  Plus, 
  Search, 
  Check, 
  ArrowLeft, 
  HelpCircle, 
  Eye, 
  Bold, 
  Italic, 
  List, 
  ListOrdered,
  Trash2,
  Send,
  X,
  Edit2
} from 'lucide-react';

interface Exam {
  id: string;
  name: string;
  type: 'Objective' | 'Subjective';
  date: string;
  time?: string;
  duration: string;
  status: 'Scheduled' | 'Completed' | 'Draft';
  description?: string;
  totalMarks?: string;
  selectedQuestionIds?: string[];
}

interface Question {
  id: string;
  text: string;
  options?: string[];
  correctAnswer?: string;
  marks?: string;
}

export const ExamManagement: React.FC = () => {
  const [currentView, setCurrentView] = useState<'list' | 'step1' | 'step2' | 'add-question' | 'step3' | 'view-details'>('list');

  // Filter & Search State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');

  // Central Exams List State
  const [exams, setExams] = useState<Exam[]>([
    { id: '1', name: 'maths', type: 'Objective', date: '', time: '', duration: '1 hour', status: 'Draft', description: 'Basic mathematics assessment unit.', totalMarks: '100', selectedQuestionIds: ['q1'] },
    { id: '2', name: 'Physics - Chapter 3', type: 'Objective', date: '2026-11-04', time: '14:00', duration: '45 mins', status: 'Scheduled', description: 'Motion and forces evaluation.', totalMarks: '50', selectedQuestionIds: ['q1', 'q2'] },
    { id: '3', name: 'English - Grammar', type: 'Subjective', date: '2026-11-15', time: '10:00', duration: '30 mins', status: 'Scheduled', description: 'Grammar and sentence structure.', totalMarks: '40', selectedQuestionIds: [] },
  ]);

  // Selected Exam for Viewing or Editing
  const [activeExam, setActiveExam] = useState<Exam | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // Active Exam Form State
  const [examName, setExamName] = useState('');
  const [examDescription, setExamDescription] = useState('');
  const [examSubject, setExamSubject] = useState('Mathematics');
  const [examType, setExamType] = useState<'Objective' | 'Subjective'>('Objective');
  const [examDate, setExamDate] = useState('');
  const [examTime, setExamTime] = useState('');
  const [examDuration, setExamDuration] = useState('1 hour');
  const [examTotalMarks, setExamTotalMarks] = useState('100');

  // Question Bank State
  const [questions, setQuestions] = useState<Question[]>([
    { id: 'q1', text: 'What is the value of 5 x 6?', options: ['25', '30', '35', '20'], correctAnswer: 'B', marks: '1' },
    { id: 'q2', text: 'Which planet is known as the "Red Planet"?', options: ['Venus', 'Mars', 'Jupiter', 'Saturn'], correctAnswer: 'B', marks: '1' },
    { id: 'q3', text: 'Solve for x: 2x + 3 = 11', options: ['3', '4', '5', '6'], correctAnswer: 'B', marks: '2' },
  ]);
  const [selectedQuestionIds, setSelectedQuestionIds] = useState<string[]>([]);

  // Add/Edit Question Form State
  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(null);
  const [newQuestionText, setNewQuestionText] = useState('');
  const [optionA, setOptionA] = useState('');
  const [optionB, setOptionB] = useState('');
  const [optionC, setOptionC] = useState('');
  const [optionD, setOptionD] = useState('');
  const [correctAnswer, setCorrectAnswer] = useState('A');
  const [questionMarks, setQuestionMarks] = useState('1');

  // Preview Modal State
  const [previewQuestion, setPreviewQuestion] = useState<Question | null>(null);

  // Handlers
  const handleSaveDraft = () => {
    if (!examName.trim()) {
      alert('Please enter at least an Exam Name before saving as draft.');
      return;
    }

    if (isEditing && activeExam) {
      setExams(exams.map(ex => ex.id === activeExam.id ? {
        ...ex,
        name: examName,
        type: examType,
        date: examDate,
        time: examTime,
        duration: examDuration,
        status: 'Draft',
        description: examDescription,
        totalMarks: examTotalMarks,
        selectedQuestionIds: selectedQuestionIds
      } : ex));
      alert('Exam draft updated successfully!');
    } else {
      const newExam: Exam = {
        id: `exam_${Date.now()}`,
        name: examName,
        type: examType,
        date: examDate,
        time: examTime,
        duration: examDuration,
        status: 'Draft',
        description: examDescription,
        totalMarks: examTotalMarks,
        selectedQuestionIds: selectedQuestionIds
      };
      setExams([newExam, ...exams]);
      alert('Exam saved as draft successfully!');
    }

    resetForm();
    setCurrentView('list');
  };

  const handlePublishExam = () => {
    if (!examName.trim()) {
      alert('Please fill out the required exam details.');
      return;
    }

    if (isEditing && activeExam) {
      setExams(exams.map(ex => ex.id === activeExam.id ? {
        ...ex,
        name: examName,
        type: examType,
        date: examDate,
        time: examTime,
        duration: examDuration,
        status: 'Scheduled',
        description: examDescription,
        totalMarks: examTotalMarks,
        selectedQuestionIds: selectedQuestionIds
      } : ex));
      alert('Exam updated and published successfully!');
    } else {
      const newExam: Exam = {
        id: `exam_${Date.now()}`,
        name: examName,
        type: examType,
        date: examDate,
        time: examTime,
        duration: examDuration,
        status: 'Scheduled',
        description: examDescription,
        totalMarks: examTotalMarks,
        selectedQuestionIds: selectedQuestionIds
      };
      setExams([newExam, ...exams]);
      alert('Exam published successfully!');
    }

    resetForm();
    setCurrentView('list');
  };

  const handleDeleteExam = (id: string) => {
    if (window.confirm('Are you sure you want to delete this exam?')) {
      setExams(exams.filter((ex) => ex.id !== id));
    }
  };

  const handleViewExam = (exam: Exam) => {
    setActiveExam(exam);
    setCurrentView('view-details');
  };

  const handleEditExam = (exam: Exam) => {
    setActiveExam(exam);
    setIsEditing(true);
    setExamName(exam.name);
    setExamDescription(exam.description || '');
    setExamType(exam.type);
    setExamDate(exam.date || '');
    setExamTime(exam.time || '');
    setExamDuration(exam.duration || '1 hour');
    setExamTotalMarks(exam.totalMarks || '100');
    setSelectedQuestionIds(exam.selectedQuestionIds || []);
    setCurrentView('step1');
  };

  const resetForm = () => {
    setExamName('');
    setExamDescription('');
    setExamSubject('Mathematics');
    setExamType('Objective');
    setExamDate('');
    setExamTime('');
    setExamDuration('1 hour');
    setExamTotalMarks('100');
    setSelectedQuestionIds([]);
    setIsEditing(false);
    setActiveExam(null);
  };

  const handleOpenAddQuestion = () => {
    setEditingQuestionId(null);
    setNewQuestionText('');
    setOptionA('');
    setOptionB('');
    setOptionC('');
    setOptionD('');
    setCorrectAnswer('A');
    setQuestionMarks('1');
    setCurrentView('add-question');
  };

  const handleEditQuestion = (q: Question) => {
    setEditingQuestionId(q.id);
    setNewQuestionText(q.text);
    setOptionA(q.options?.[0] || '');
    setOptionB(q.options?.[1] || '');
    setOptionC(q.options?.[2] || '');
    setOptionD(q.options?.[3] || '');
    setCorrectAnswer(q.correctAnswer || 'A');
    setQuestionMarks(q.marks || '1');
    setCurrentView('add-question');
  };

  const handleDeleteQuestion = (qId: string) => {
    if (window.confirm('Delete this question from question bank?')) {
      setQuestions(questions.filter(q => q.id !== qId));
      setSelectedQuestionIds(selectedQuestionIds.filter(id => id !== qId));
    }
  };

  const handleSaveQuestionForm = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newQuestionText.trim()) return;

    const optionsList = [optionA, optionB, optionC, optionD];

    if (editingQuestionId) {
      setQuestions(questions.map(q => q.id === editingQuestionId ? {
        ...q,
        text: newQuestionText,
        options: optionsList,
        correctAnswer: correctAnswer,
        marks: questionMarks
      } : q));
    } else {
      const created: Question = {
        id: `q_${Date.now()}`,
        text: newQuestionText,
        options: optionsList,
        correctAnswer: correctAnswer,
        marks: questionMarks,
      };
      setQuestions([created, ...questions]);
      setSelectedQuestionIds([...selectedQuestionIds, created.id]);
    }

    setCurrentView('step2');
  };

  const filteredExams = exams.filter((exam) => {
    const matchesSearch = exam.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedType === 'All' || exam.type === selectedType;
    const matchesStatus = selectedStatus === 'All' || exam.status === selectedStatus;
    return matchesSearch && matchesType && matchesStatus;
  });

  return (
    <div className="p-8 bg-[#F0F5FA] min-h-screen">
      {/* VIEW 1: MANAGE EXAMS LIST */}
      {currentView === 'list' && (
        <>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Manage Exams</h1>
              <p className="text-gray-500 text-sm mt-0.5">Create, edit and manage your exams.</p>
            </div>
            <button
              onClick={() => {
                resetForm();
                setCurrentView('step1');
              }}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-medium text-sm transition-all shadow-md shadow-blue-500/20 cursor-pointer self-start md:self-auto"
            >
              <Plus className="w-4 h-4" />
              Create New Exam
            </button>
          </div>

          <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 mb-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="relative w-full md:w-96">
              <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search by exam name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50/50 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            <div className="flex items-center gap-3 w-full md:w-auto">
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full md:w-44 px-4 py-2.5 bg-gray-50/50 rounded-xl border border-gray-200 text-sm text-gray-700 cursor-pointer"
              >
                <option value="All">All Types</option>
                <option value="Objective">Objective</option>
                <option value="Subjective">Subjective</option>
              </select>

              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full md:w-44 px-4 py-2.5 bg-gray-50/50 rounded-xl border border-gray-200 text-sm text-gray-700 cursor-pointer"
              >
                <option value="All">All Statuses</option>
                <option value="Scheduled">Scheduled</option>
                <option value="Draft">Draft</option>
                <option value="Completed">Completed</option>
              </select>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-gray-100 text-gray-400 text-xs font-semibold uppercase tracking-wider">
                    <th className="py-4 px-6">Exam Name</th>
                    <th className="py-4 px-6">Type</th>
                    <th className="py-4 px-6">Date & Time</th>
                    <th className="py-4 px-6">Duration</th>
                    <th className="py-4 px-6">Status</th>
                    <th className="py-4 px-6 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-sm">
                  {filteredExams.map((exam) => (
                    <tr key={exam.id} className="hover:bg-gray-50/50 transition-colors">
                      <td className="py-4 px-6 font-semibold text-gray-900 flex items-center gap-2.5">
                        <FileText className="w-4 h-4 text-blue-600" />
                        {exam.name}
                      </td>
                      <td className="py-4 px-6 text-gray-600">{exam.type}</td>
                      <td className="py-4 px-6 text-gray-600">{exam.date ? `${exam.date} ${exam.time || ''}` : 'TBD'}</td>
                      <td className="py-4 px-6 text-gray-600">{exam.duration}</td>
                      <td className="py-4 px-6">
                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${
                          exam.status === 'Draft' ? 'bg-amber-50 text-amber-600' : 'bg-blue-50 text-blue-600'
                        }`}>
                          {exam.status}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-right space-x-3">
                        <button 
                          onClick={() => handleViewExam(exam)}
                          className="text-xs font-semibold text-blue-600 hover:underline cursor-pointer"
                        >
                          View
                        </button>
                        <button 
                          onClick={() => handleEditExam(exam)}
                          className="text-xs font-semibold text-gray-600 hover:underline cursor-pointer"
                        >
                          Edit
                        </button>
                        <button 
                          onClick={() => handleDeleteExam(exam.id)}
                          className="text-xs font-semibold text-rose-500 hover:text-rose-700 cursor-pointer inline-flex items-center gap-1"
                        >
                          <Trash2 className="w-3.5 h-3.5 inline" /> Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination Footer */}
            <div className="flex items-center justify-between px-6 py-4 border-t border-gray-100 text-xs text-gray-500 bg-white">
              <p>Showing 1 - {filteredExams.length} of {exams.length} exams</p>
              <div className="flex items-center gap-1">
                <button className="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">Prev</button>
                <button className="px-3 py-1.5 rounded-lg bg-blue-600 text-white font-semibold cursor-pointer">1</button>
                <button className="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">Next</button>
              </div>
            </div>
          </div>
        </>
      )}

      {/* VIEW DETAILS MODAL / SCREEN */}
      {currentView === 'view-details' && activeExam && (
        <div className="max-w-3xl mx-auto bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-100">
            <div>
              <span className="text-xs font-semibold text-blue-600 uppercase tracking-widest">{activeExam.type} Exam</span>
              <h2 className="text-2xl font-bold text-gray-900 mt-1">{activeExam.name}</h2>
            </div>
            <button 
              onClick={() => setCurrentView('list')}
              className="p-2 rounded-full hover:bg-gray-100 text-gray-500 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-6 mb-6 text-sm">
            <div>
              <p className="text-gray-400 text-xs font-medium">Date & Time</p>
              <p className="font-semibold text-gray-900 mt-0.5">{activeExam.date ? `${activeExam.date} ${activeExam.time || ''}` : 'TBD'}</p>
            </div>
            <div>
              <p className="text-gray-400 text-xs font-medium">Duration</p>
              <p className="font-semibold text-gray-900 mt-0.5">{activeExam.duration}</p>
            </div>
            <div>
              <p className="text-gray-400 text-xs font-medium">Status</p>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-600 mt-1">
                {activeExam.status}
              </span>
            </div>
            <div>
              <p className="text-gray-400 text-xs font-medium">Total Marks</p>
              <p className="font-semibold text-gray-900 mt-0.5">{activeExam.totalMarks || '100'} Marks</p>
            </div>
          </div>

          <div className="mb-6">
            <p className="text-gray-400 text-xs font-medium mb-1">Description</p>
            <p className="text-gray-700 text-sm bg-gray-50 p-4 rounded-xl border border-gray-100">
              {activeExam.description || 'No description provided.'}
            </p>
          </div>

          <div className="flex justify-end">
            <button
              onClick={() => setCurrentView('list')}
              className="px-6 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 cursor-pointer"
            >
              Close Details
            </button>
          </div>
        </div>
      )}

      {/* PREVIEW QUESTION MODAL */}
      {previewQuestion && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-100">
              <h3 className="font-bold text-gray-900 text-lg">Question Preview</h3>
              <button onClick={() => setPreviewQuestion(null)} className="text-gray-400 hover:text-gray-600 cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="font-semibold text-gray-900 mb-4">{previewQuestion.text}</p>
            {previewQuestion.options && previewQuestion.options.length > 0 && (
              <div className="space-y-2 mb-4">
                {previewQuestion.options.map((opt, idx) => {
                  const optLetter = ['A', 'B', 'C', 'D'][idx];
                  const isCorrect = previewQuestion.correctAnswer === optLetter;
                  return (
                    <div key={idx} className={`p-3 rounded-xl border text-sm flex items-center justify-between ${isCorrect ? 'bg-emerald-50 border-emerald-200 text-emerald-900 font-semibold' : 'bg-gray-50 border-gray-200 text-gray-700'}`}>
                      <span>{optLetter}. {opt}</span>
                      {isCorrect && <span className="text-xs bg-emerald-600 text-white px-2 py-0.5 rounded-full">Correct Answer</span>}
                    </div>
                  );
                })}
              </div>
            )}
            <div className="flex justify-end">
              <button onClick={() => setPreviewQuestion(null)} className="px-5 py-2 bg-blue-600 text-white rounded-xl text-sm font-medium cursor-pointer">Close</button>
            </div>
          </div>
        </div>
      )}

      {/* VIEW 2: STEP 1 - BASIC INFORMATION */}
      {currentView === 'step1' && (
        <div className="max-w-5xl mx-auto">
          <button 
            onClick={() => {
              resetForm();
              setCurrentView('list');
            }}
            className="flex items-center gap-1.5 text-xs font-semibold text-blue-600 mb-4 hover:underline cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Exams
          </button>

          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">{isEditing ? 'Edit Exam' : 'Create New Exam'}</h1>
            <p className="text-gray-500 text-sm mt-0.5">Fill in the details below.</p>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm">1</div>
              <span className="font-bold text-gray-950 text-sm">Basic Information</span>
            </div>
            <div className="h-0.5 flex-1 bg-gray-200 mx-4" />
            <div className="flex items-center gap-3 opacity-40">
              <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-700 flex items-center justify-center font-bold text-sm">2</div>
              <span className="font-medium text-gray-700 text-sm">Add Questions</span>
            </div>
            <div className="h-0.5 flex-1 bg-gray-200 mx-4" />
            <div className="flex items-center gap-3 opacity-40">
              <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-700 flex items-center justify-center font-bold text-sm">3</div>
              <span className="font-medium text-gray-700 text-sm">Exam Settings</span>
            </div>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">Exam Name *</label>
                <input 
                  type="text" 
                  placeholder="Enter exam name" 
                  value={examName}
                  onChange={(e) => setExamName(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20" 
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">Description</label>
                <textarea 
                  rows={4} 
                  placeholder="Add a brief description (optional)" 
                  value={examDescription}
                  onChange={(e) => setExamDescription(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none resize-none" 
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Subject *</label>
                  <select 
                    value={examSubject}
                    onChange={(e) => setExamSubject(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm bg-white cursor-pointer"
                  >
                    <option value="Mathematics">Mathematics</option>
                    <option value="Physics">Physics</option>
                    <option value="Chemistry">Chemistry</option>
                    <option value="English">English</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Exam Type *</label>
                  <select 
                    value={examType}
                    onChange={(e) => setExamType(e.target.value as 'Objective' | 'Subjective')}
                    className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm bg-white cursor-pointer"
                  >
                    <option value="Objective">Objective</option>
                    <option value="Subjective">Subjective</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Date *</label>
                  <input 
                    type="date" 
                    value={examDate}
                    onChange={(e) => setExamDate(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Time *</label>
                  <input 
                    type="time" 
                    value={examTime}
                    onChange={(e) => setExamTime(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm" 
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">Duration *</label>
                <select 
                  value={examDuration}
                  onChange={(e) => setExamDuration(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm bg-white cursor-pointer"
                >
                  <option value="30 mins">30 mins</option>
                  <option value="45 mins">45 mins</option>
                  <option value="1 hour">1 hour</option>
                  <option value="2 hours">2 hours</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">Total Marks *</label>
                <input 
                  type="number" 
                  value={examTotalMarks}
                  onChange={(e) => setExamTotalMarks(e.target.value)}
                  placeholder="Enter total marks" 
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm" 
                />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between gap-3">
            <button 
              onClick={handleSaveDraft}
              className="px-6 py-2.5 rounded-xl text-sm font-medium border border-gray-200 hover:bg-gray-50 cursor-pointer"
            >
              Save Draft
            </button>
            <button 
              onClick={() => setCurrentView('step2')}
              className="px-6 py-2.5 rounded-xl text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-500/20 cursor-pointer"
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {/* VIEW 3: STEP 2 - ADD QUESTIONS */}
      {currentView === 'step2' && (
        <div className="max-w-5xl mx-auto">
          <button 
            onClick={() => setCurrentView('step1')}
            className="flex items-center gap-1.5 text-xs font-semibold text-blue-600 mb-4 hover:underline cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Basic Info
          </button>

          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{isEditing ? 'Edit Exam' : 'Create New Exam'}</h1>
              <p className="text-gray-500 text-sm mt-0.5">Add questions to your exam.</p>
            </div>
            <button
              onClick={handleOpenAddQuestion}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl text-sm font-medium shadow-md shadow-blue-500/20 cursor-pointer"
            >
              <Plus className="w-4 h-4" /> Add Question
            </button>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-6 flex items-center justify-between">
            <div className="flex items-center gap-3 text-emerald-600">
              <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center font-bold text-sm"><Check className="w-4 h-4" /></div>
              <span className="font-bold text-sm">Basic Info</span>
            </div>
            <div className="h-0.5 flex-1 bg-blue-600 mx-4" />
            <div className="flex items-center gap-3 text-blue-600">
              <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm">2</div>
              <span className="font-bold text-sm">Questions</span>
            </div>
            <div className="h-0.5 flex-1 bg-gray-200 mx-4" />
            <div className="flex items-center gap-3 opacity-40">
              <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-700 flex items-center justify-center font-bold text-sm">3</div>
              <span className="font-medium text-gray-700 text-sm">Settings</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
            <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
              <HelpCircle className="w-5 h-5 text-blue-600" /> Question Bank
            </h3>
            
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-100 text-gray-400 text-xs font-semibold uppercase">
                  <th className="py-3 px-4 w-10">Select</th>
                  <th className="py-3 px-4">Question</th>
                  <th className="py-3 px-4 text-right">Preview / Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-sm">
                {questions.map((q) => {
                  const isChecked = selectedQuestionIds.includes(q.id);
                  return (
                    <tr key={q.id} className="hover:bg-gray-50/50">
                      <td className="py-3.5 px-4">
                        <input 
                          type="checkbox" 
                          checked={isChecked}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedQuestionIds([...selectedQuestionIds, q.id]);
                            } else {
                              setSelectedQuestionIds(selectedQuestionIds.filter(id => id !== q.id));
                            }
                          }}
                          className="rounded border-gray-300 text-blue-600 cursor-pointer" 
                        />
                      </td>
                      <td className="py-3.5 px-4 font-semibold text-gray-900">{q.text}</td>
                      <td className="py-3.5 px-4 text-right space-x-3">
                        <button 
                          onClick={() => setPreviewQuestion(q)}
                          className="text-xs font-semibold text-blue-600 hover:underline inline-flex items-center gap-1 cursor-pointer"
                        >
                          <Eye className="w-3.5 h-3.5" /> Preview
                        </button>
                        <button 
                          onClick={() => handleEditQuestion(q)}
                          className="text-xs font-semibold text-gray-600 hover:underline inline-flex items-center gap-1 cursor-pointer"
                        >
                          <Edit2 className="w-3.5 h-3.5" /> Edit
                        </button>
                        <button 
                          onClick={() => handleDeleteQuestion(q.id)}
                          className="text-xs font-semibold text-rose-500 hover:text-rose-700 inline-flex items-center gap-1 cursor-pointer"
                        >
                          <Trash2 className="w-3.5 h-3.5" /> Delete
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between">
            <button 
              onClick={handleSaveDraft}
              className="px-6 py-2.5 rounded-xl text-sm font-medium border border-gray-200 hover:bg-gray-50 cursor-pointer"
            >
              Save Draft
            </button>
            <button 
              onClick={() => setCurrentView('step3')}
              className="px-6 py-2.5 rounded-xl text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-500/20 cursor-pointer"
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {/* VIEW 4: ADD/EDIT QUESTION SCREEN WITH OPTIONS */}
      {currentView === 'add-question' && (
        <div className="max-w-4xl mx-auto">
          <button 
            onClick={() => setCurrentView('step2')}
            className="flex items-center gap-1.5 text-xs font-semibold text-blue-600 mb-4 hover:underline cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Questions
          </button>

          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">{editingQuestionId ? 'Edit Question' : 'Add Question'}</h1>
            <p className="text-gray-500 text-sm mt-0.5">Create or modify a question for your exam.</p>
          </div>

          <form onSubmit={handleSaveQuestionForm} className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 space-y-6">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-2">Question Text</label>
              <div className="border border-gray-200 rounded-xl overflow-hidden">
                <div className="bg-gray-50 border-b border-gray-200 px-4 py-2 flex items-center gap-4 text-gray-600 text-xs">
                  <button type="button" className="hover:text-blue-600"><Bold className="w-4 h-4" /></button>
                  <button type="button" className="hover:text-blue-600"><Italic className="w-4 h-4" /></button>
                  <button type="button" className="hover:text-blue-600"><List className="w-4 h-4" /></button>
                  <button type="button" className="hover:text-blue-600"><ListOrdered className="w-4 h-4" /></button>
                </div>
                <textarea
                  rows={3}
                  placeholder="Enter your question here..."
                  value={newQuestionText}
                  onChange={(e) => setNewQuestionText(e.target.value)}
                  className="w-full p-4 text-sm focus:outline-none resize-none"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <label className="block text-xs font-semibold text-gray-700">Options</label>
                <div>
                  <span className="text-[11px] text-gray-400 font-medium">Option A</span>
                  <input type="text" placeholder="Enter option A" value={optionA} onChange={(e) => setOptionA(e.target.value)} className="w-full px-4 py-2 rounded-xl border border-gray-200 text-sm" />
                </div>
                <div>
                  <span className="text-[11px] text-gray-400 font-medium">Option B</span>
                  <input type="text" placeholder="Enter option B" value={optionB} onChange={(e) => setOptionB(e.target.value)} className="w-full px-4 py-2 rounded-xl border border-gray-200 text-sm" />
                </div>
                <div>
                  <span className="text-[11px] text-gray-400 font-medium">Option C</span>
                  <input type="text" placeholder="Enter option C" value={optionC} onChange={(e) => setOptionC(e.target.value)} className="w-full px-4 py-2 rounded-xl border border-gray-200 text-sm" />
                </div>
                <div>
                  <span className="text-[11px] text-gray-400 font-medium">Option D</span>
                  <input type="text" placeholder="Enter option D" value={optionD} onChange={(e) => setOptionD(e.target.value)} className="w-full px-4 py-2 rounded-xl border border-gray-200 text-sm" />
                </div>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-2">Select Correct Answer</label>
                  <div className="space-y-2">
                    {['A', 'B', 'C', 'D'].map((opt) => (
                      <label key={opt} className="flex items-center gap-2 text-sm font-medium text-gray-700 cursor-pointer">
                        <input 
                          type="radio" 
                          name="correctOpt" 
                          checked={correctAnswer === opt} 
                          onChange={() => setCorrectAnswer(opt)} 
                          className="text-blue-600 focus:ring-blue-500"
                        />
                        Option {opt}
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Marks</label>
                  <input 
                    type="number" 
                    value={questionMarks} 
                    onChange={(e) => setQuestionMarks(e.target.value)} 
                    className="w-full px-4 py-2 rounded-xl border border-gray-200 text-sm" 
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
              <button 
                type="button" 
                onClick={() => setCurrentView('step2')}
                className="px-5 py-2.5 rounded-xl text-sm font-medium border border-gray-200 hover:bg-gray-50 cursor-pointer"
              >
                Cancel
              </button>
              <button 
                type="submit"
                className="px-5 py-2.5 rounded-xl text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-500/20 cursor-pointer"
              >
                Save Question
              </button>
            </div>
          </form>
        </div>
      )}

      {/* VIEW 5: STEP 3 - EXAM SETTINGS */}
      {currentView === 'step3' && (
        <div className="max-w-5xl mx-auto">
          <button 
            onClick={() => setCurrentView('step2')}
            className="flex items-center gap-1.5 text-xs font-semibold text-blue-600 mb-4 hover:underline cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Questions
          </button>

          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">{isEditing ? 'Edit Exam' : 'Create New Exam'}</h1>
            <p className="text-gray-500 text-sm mt-0.5">Configure exam settings and finalize your exam.</p>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-6 flex items-center justify-between">
            <div className="flex items-center gap-3 text-emerald-600">
              <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center font-bold text-sm"><Check className="w-4 h-4" /></div>
              <span className="font-bold text-sm">Basic Info</span>
            </div>
            <div className="h-0.5 flex-1 bg-emerald-600 mx-4" />
            <div className="flex items-center gap-3 text-emerald-600">
              <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center font-bold text-sm"><Check className="w-4 h-4" /></div>
              <span className="font-bold text-sm">Questions</span>
            </div>
            <div className="h-0.5 flex-1 bg-blue-600 mx-4" />
            <div className="flex items-center gap-3 text-blue-600">
              <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm">3</div>
              <span className="font-bold text-sm">Settings</span>
            </div>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 grid grid-cols-1 md:grid-cols-2 gap-8 mb-6">
            <div className="space-y-6">
              <h3 className="font-bold text-gray-900 text-base pb-2 border-b border-gray-100">Availability & Attempts</h3>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-gray-900">Allow multiple attempts</p>
                  <p className="text-xs text-gray-400">Students can retake the exam</p>
                </div>
                <input type="checkbox" defaultChecked className="w-5 h-5 rounded text-blue-600 cursor-pointer" />
              </div>

              <h3 className="font-bold text-gray-900 text-base pb-2 border-b border-gray-100 pt-4">Navigation</h3>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-gray-900">Allow Back Navigation</p>
                  <p className="text-xs text-gray-400">Students can return to previous questions</p>
                </div>
                <input type="checkbox" defaultChecked className="w-5 h-5 rounded text-blue-600 cursor-pointer" />
              </div>
            </div>

            <div className="space-y-6">
              <h3 className="font-bold text-gray-900 text-base pb-2 border-b border-gray-100">Grading & Results</h3>
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">Passing Score (%)</label>
                <input type="number" defaultValue={60} className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm" />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between gap-3">
            <button 
              onClick={handleSaveDraft}
              className="px-6 py-2.5 rounded-xl text-sm font-medium border border-gray-200 hover:bg-gray-50 cursor-pointer"
            >
              Save as Draft
            </button>
            <button 
              onClick={handlePublishExam}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-500/20 cursor-pointer"
            >
              <Send className="w-4 h-4" /> Publish Exam
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExamManagement;