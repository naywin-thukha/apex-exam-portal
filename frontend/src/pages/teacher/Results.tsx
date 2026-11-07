import React, { useState } from 'react';
import { 
  Users, 
  TrendingUp, 
  CheckCircle2, 
  Clock, 
  Search, 
  BookOpen, 
  SlidersHorizontal, 
  RotateCcw, 
  Eye,
  X,
  Check,
  AlertCircle
} from 'lucide-react';

interface QuestionAnswerDetail {
  questionId: string;
  questionText: string;
  studentAnswer: string;
  correctAnswer: string;
  isCorrect: boolean;
}

interface ResultItem {
  id: string;
  studentName: string;
  studentInitials: string;
  exam: string;
  score: string;
  status: 'Passed' | 'Failed';
  answers: QuestionAnswerDetail[];
}

export const Results: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('All Subjects');
  const [selectedStatus, setSelectedStatus] = useState('All Statuses');

  const [resultsList] = useState<ResultItem[]>([
    { 
      id: '1', 
      studentName: 'Mg Mg', 
      studentInitials: 'MM', 
      exam: 'Maths', 
      score: '58/100', 
      status: 'Passed',
      answers: [
        { questionId: 'q1', questionText: 'What is the value of 5 x 6?', studentAnswer: 'Option B (30)', correctAnswer: 'Option B (30)', isCorrect: true },
        { questionId: 'q2', questionText: 'Solve for x: 2x + 3 = 11', studentAnswer: 'Option A (3)', correctAnswer: 'Option B (4)', isCorrect: false },
        { questionId: 'q3', questionText: 'What is the square root of 64?', studentAnswer: 'Option C (8)', correctAnswer: 'Option C (8)', isCorrect: true },
      ]
    },
    { 
      id: '2', 
      studentName: 'Aye Aye', 
      studentInitials: 'AA', 
      exam: 'Physics', 
      score: '30/100', 
      status: 'Failed',
      answers: [
        { questionId: 'q1', questionText: 'Which planet is known as the "Red Planet"?', studentAnswer: 'Option A (Venus)', correctAnswer: 'Option B (Mars)', isCorrect: false },
        { questionId: 'q2', questionText: 'What is the unit of Force?', studentAnswer: 'Option C (Joule)', correctAnswer: 'Option A (Newton)', isCorrect: false },
        { questionId: 'q3', questionText: 'Speed of light in vacuum?', studentAnswer: 'Option A (3x10^8 m/s)', correctAnswer: 'Option A (3x10^8 m/s)', isCorrect: true },
      ]
    },
    { 
      id: '3', 
      studentName: 'Su Su', 
      studentInitials: 'SS', 
      exam: 'Chemistry', 
      score: '82/100', 
      status: 'Passed',
      answers: [
        { questionId: 'q1', questionText: 'What is the chemical symbol for Gold?', studentAnswer: 'Option A (Au)', correctAnswer: 'Option A (Au)', isCorrect: true },
        { questionId: 'q2', questionText: 'What is the pH of pure water?', studentAnswer: 'Option B (7)', correctAnswer: 'Option B (7)', isCorrect: true },
      ]
    },
    { 
      id: '4', 
      studentName: 'Kyaw Kyaw', 
      studentInitials: 'KK', 
      exam: 'English', 
      score: '75/100', 
      status: 'Passed',
      answers: [
        { questionId: 'q1', questionText: 'Synonym for "Happy"?', studentAnswer: 'Option A (Joyful)', correctAnswer: 'Option A (Joyful)', isCorrect: true },
        { questionId: 'q2', questionText: 'Antonym for "Ancient"?', studentAnswer: 'Option C (Modern)', correctAnswer: 'Option C (Modern)', isCorrect: true },
      ]
    },
  ]);

  // Selected result item for viewing details modal
  const [activeResult, setActiveResult] = useState<ResultItem | null>(null);

  const handleReset = () => {
    setSearchTerm('');
    setSelectedSubject('All Subjects');
    setSelectedStatus('All Statuses');
  };

  const filteredResults = resultsList.filter((item) => {
    const matchesSearch = item.studentName.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          item.exam.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSubject = selectedSubject === 'All Subjects' || item.exam === selectedSubject;
    const matchesStatus = selectedStatus === 'All Statuses' || item.status === selectedStatus;
    return matchesSearch && matchesSubject && matchesStatus;
  });

  return (
    <div className="p-8 bg-[#F0F5FA] min-h-screen">
      {/* Page Title */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Exam Results & Student Performance</h1>
      </div>

      {/* Top Metric Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Total Evaluated</p>
            <h3 className="text-2xl font-bold text-gray-900">1,234</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <Users className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Average Score</p>
            <h3 className="text-2xl font-bold text-gray-900">76.4%</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Pass Rate</p>
            <h3 className="text-2xl font-bold text-gray-900">88.2%</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <CheckCircle2 className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Pending Review</p>
            <h3 className="text-2xl font-bold text-gray-900">18</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
            <Clock className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 mb-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search students or exams..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-gray-50/50 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div className="flex items-center gap-2 px-3 py-2.5 bg-gray-50/50 rounded-xl border border-gray-200 text-sm text-gray-700">
            <BookOpen className="w-4 h-4 text-gray-400" />
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="bg-transparent focus:outline-none cursor-pointer text-sm"
            >
              <option>All Subjects</option>
              <option>Maths</option>
              <option>Physics</option>
              <option>Chemistry</option>
              <option>English</option>
            </select>
          </div>

          <div className="flex items-center gap-2 px-3 py-2.5 bg-gray-50/50 rounded-xl border border-gray-200 text-sm text-gray-700">
            <SlidersHorizontal className="w-4 h-4 text-gray-400" />
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-transparent focus:outline-none cursor-pointer text-sm"
            >
              <option>All Statuses</option>
              <option>Passed</option>
              <option>Failed</option>
            </select>
          </div>

          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-gray-200 text-sm font-semibold text-gray-600 hover:bg-gray-50 transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset
          </button>
        </div>
      </div>

      {/* Results Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-100 text-gray-400 text-xs font-semibold uppercase tracking-wider">
                <th className="py-4 px-6">Student</th>
                <th className="py-4 px-6">Exam</th>
                <th className="py-4 px-6">Score</th>
                <th className="py-4 px-6">Status</th>
                <th className="py-4 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm">
              {filteredResults.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="py-4 px-6 flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-blue-50 text-blue-600 font-bold text-xs flex items-center justify-center border border-blue-100">
                      {item.studentInitials}
                    </div>
                    <span className="font-semibold text-gray-900">{item.studentName}</span>
                  </td>
                  <td className="py-4 px-6 text-gray-600">{item.exam}</td>
                  <td className="py-4 px-6 font-bold text-gray-900">{item.score}</td>
                  <td className="py-4 px-6">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                      item.status === 'Passed' 
                        ? 'bg-emerald-50 text-emerald-600' 
                        : 'bg-rose-50 text-rose-600'
                    }`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-right">
                    <button 
                      onClick={() => setActiveResult(item)}
                      className="p-2 rounded-lg text-blue-600 hover:bg-blue-50 transition-colors cursor-pointer inline-flex items-center gap-1 text-xs font-semibold"
                    >
                      <Eye className="w-4 h-4" /> View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-gray-100 text-xs text-gray-500">
          <p>Showing 1 - {filteredResults.length} of {resultsList.length} results</p>
          <div className="flex items-center gap-1">
            <button className="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">Prev</button>
            <button className="px-3 py-1.5 rounded-lg bg-blue-600 text-white font-semibold cursor-pointer">1</button>
            <button className="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">2</button>
            <button className="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">3</button>
            <span className="px-2 text-gray-400">...</span>
            <button className="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">12</button>
            <button className="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">Next</button>
          </div>
        </div>
      </div>

      {/* VIEW DETAILS MODAL WITH ANSWER SELECTIONS */}
      {activeResult && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-xl max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-100 flex-shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 font-bold text-sm flex items-center justify-center border border-blue-100">
                  {activeResult.studentInitials}
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 text-base">{activeResult.studentName}</h3>
                  <p className="text-xs text-gray-400">{activeResult.exam} Exam Performance Breakdown</p>
                </div>
              </div>
              <button onClick={() => setActiveResult(null)} className="text-gray-400 hover:text-gray-600 cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Overview Summary Bar */}
            <div className="grid grid-cols-2 gap-4 mb-4 p-3 bg-gray-50 rounded-xl border border-gray-100 text-xs flex-shrink-0">
              <div>
                <span className="text-gray-400 font-medium">Obtained Score</span>
                <p className="text-base font-bold text-gray-900 mt-0.5">{activeResult.score}</p>
              </div>
              <div>
                <span className="text-gray-400 font-medium">Result Status</span>
                <p className="mt-0.5">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                    activeResult.status === 'Passed' ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'
                  }`}>
                    {activeResult.status}
                  </span>
                </p>
              </div>
            </div>

            {/* Answered Questions Breakdown */}
            <div className="overflow-y-auto flex-1 pr-1 space-y-3 mb-4">
              <h4 className="text-xs font-bold uppercase text-gray-400 tracking-wider">Question Breakdown</h4>
              {activeResult.answers.map((ans, idx) => (
                <div 
                  key={ans.questionId} 
                  className={`p-4 rounded-xl border ${
                    ans.isCorrect ? 'bg-emerald-50/40 border-emerald-100' : 'bg-rose-50/40 border-rose-100'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <p className="text-xs font-bold text-gray-900">
                      Q{idx + 1}. {ans.questionText}
                    </p>
                    <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full flex-shrink-0 ${
                      ans.isCorrect ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
                    }`}>
                      {ans.isCorrect ? (
                        <>
                          <Check className="w-3 h-3" /> Correct
                        </>
                      ) : (
                        <>
                          <AlertCircle className="w-3 h-3" /> Wrong
                        </>
                      )}
                    </span>
                  </div>

                  <div className="space-y-1 text-xs">
                    <p className="text-gray-700">
                      <span className="font-semibold text-gray-500">Student Chose: </span>
                      <span className={ans.isCorrect ? 'font-bold text-emerald-700' : 'font-bold text-rose-600'}>
                        {ans.studentAnswer}
                      </span>
                    </p>
                    {!ans.isCorrect && (
                      <p className="text-gray-700">
                        <span className="font-semibold text-gray-500">Correct Answer: </span>
                        <span className="font-bold text-emerald-700">{ans.correctAnswer}</span>
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end flex-shrink-0 pt-2 border-t border-gray-100">
              <button 
                onClick={() => setActiveResult(null)}
                className="px-5 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 cursor-pointer"
              >
                Close Details
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Results;