import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_ENDPOINTS } from '../config';
import { 
  Trophy, Target, TrendingUp, Award, Flame, 
  BookOpen, Clock, CheckCircle, XCircle, Star 
} from 'lucide-react';

interface ProgressStats {
  total_points: number;
  questions_attempted: number;
  questions_solved: number;
  success_rate: number;
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
  progress?: number;
  target?: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<ProgressStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [streak] = useState(3); // Mock data - would come from backend
  const [topicBreakdown] = useState([
    { topic: 'Algebra', solved: 15, attempted: 20, accuracy: 75 },
    { topic: 'Geometry', solved: 8, attempted: 12, accuracy: 67 },
    { topic: 'Arithmetic', solved: 22, attempted: 25, accuracy: 88 },
    { topic: 'Statistics', solved: 5, attempted: 8, accuracy: 63 },
  ]);

  const [achievements] = useState<Achievement[]>([
    {
      id: '1',
      name: 'First Steps',
      description: 'Solve your first question',
      icon: '🎯',
      unlocked: true,
    },
    {
      id: '2',
      name: 'Speed Demon',
      description: 'Solve 5 questions in under 30 seconds each',
      icon: '⚡',
      unlocked: true,
      progress: 5,
      target: 5,
    },
    {
      id: '3',
      name: 'Perfect Score',
      description: 'Get 10 questions right on first try',
      icon: '💯',
      unlocked: false,
      progress: 7,
      target: 10,
    },
    {
      id: '4',
      name: 'Math Master',
      description: 'Solve 100 questions',
      icon: '🏆',
      unlocked: false,
      progress: 50,
      target: 100,
    },
    {
      id: '5',
      name: 'Week Warrior',
      description: 'Maintain a 7-day streak',
      icon: '🔥',
      unlocked: false,
      progress: 3,
      target: 7,
    },
    {
      id: '6',
      name: 'Topic Explorer',
      description: 'Try all 8 topics',
      icon: '🌟',
      unlocked: false,
      progress: 4,
      target: 8,
    },
  ]);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(API_ENDPOINTS.STUDENT_PROGRESS('test_student'));
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      // Use mock data for demonstration
      setStats({
        total_points: 1250,
        questions_attempted: 50,
        questions_solved: 38,
        success_rate: 0.76,
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-linear-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-blue-700 mb-2">Your Dashboard</h1>
          <p className="text-gray-600">Track your progress and achievements</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-yellow-300">
            <div className="flex items-center justify-between mb-2">
              <Trophy className="w-8 h-8 text-yellow-600" />
              <span className="text-3xl font-bold text-yellow-600">{stats?.total_points || 0}</span>
            </div>
            <p className="text-gray-600 font-medium">Total Points</p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-blue-300">
            <div className="flex items-center justify-between mb-2">
              <Target className="w-8 h-8 text-blue-600" />
              <span className="text-3xl font-bold text-blue-600">{stats?.questions_attempted || 0}</span>
            </div>
            <p className="text-gray-600 font-medium">Questions Attempted</p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-green-300">
            <div className="flex items-center justify-between mb-2">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <span className="text-3xl font-bold text-green-600">{stats?.questions_solved || 0}</span>
            </div>
            <p className="text-gray-600 font-medium">Questions Solved</p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-orange-300">
            <div className="flex items-center justify-between mb-2">
              <Flame className="w-8 h-8 text-orange-600" />
              <span className="text-3xl font-bold text-orange-600">{streak}</span>
            </div>
            <p className="text-gray-600 font-medium">Day Streak 🔥</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Performance Chart */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-lg p-6 border-2 border-indigo-300">
            <div className="flex items-center gap-2 mb-6">
              <TrendingUp className="w-6 h-6 text-indigo-600" />
              <h2 className="text-2xl font-bold text-indigo-700">Performance by Topic</h2>
            </div>
            <div className="space-y-4">
              {topicBreakdown.map((topic) => (
                <div key={topic.topic} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-gray-700">{topic.topic}</span>
                    <span className="text-sm text-gray-600">
                      {topic.solved}/{topic.attempted} ({topic.accuracy}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full transition-all duration-500"
                      style={{ width: `${topic.accuracy}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            
            {/* Overall Accuracy */}
            <div className="mt-6 pt-6 border-t-2 border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-lg font-bold text-gray-800">Overall Accuracy</span>
                <span className="text-2xl font-bold text-indigo-600">
                  {Math.round((stats?.success_rate || 0) * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-6 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-green-500 to-emerald-600 rounded-full transition-all duration-500"
                  style={{ width: `${(stats?.success_rate || 0) * 100}%` }}
                />
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-purple-300">
            <div className="flex items-center gap-2 mb-6">
              <Clock className="w-6 h-6 text-purple-600" />
              <h2 className="text-2xl font-bold text-purple-700">Recent Activity</h2>
            </div>
            <div className="space-y-3">
              <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-gray-800">Solved Algebra</p>
                  <p className="text-xs text-gray-600">2 hours ago • +150 pts</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-gray-800">Solved Geometry</p>
                  <p className="text-xs text-gray-600">5 hours ago • +180 pts</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-red-50 rounded-lg border border-red-200">
                <XCircle className="w-5 h-5 text-red-600 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-gray-800">Failed Calculus</p>
                  <p className="text-xs text-gray-600">1 day ago • 0 pts</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-gray-800">Solved Arithmetic</p>
                  <p className="text-xs text-gray-600">1 day ago • +120 pts</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Achievements */}
        <div className="mt-8 bg-white rounded-xl shadow-lg p-6 border-2 border-yellow-300">
          <div className="flex items-center gap-2 mb-6">
            <Award className="w-6 h-6 text-yellow-600" />
            <h2 className="text-2xl font-bold text-yellow-700">Achievements</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {achievements.map((achievement) => (
              <div
                key={achievement.id}
                className={`p-4 rounded-lg border-2 transition-all ${
                  achievement.unlocked
                    ? 'bg-gradient-to-br from-yellow-50 to-amber-50 border-yellow-400'
                    : 'bg-gray-50 border-gray-300 opacity-60'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="text-3xl">{achievement.icon}</div>
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-800 mb-1">{achievement.name}</h3>
                    <p className="text-sm text-gray-600 mb-2">{achievement.description}</p>
                    {!achievement.unlocked && achievement.progress !== undefined && achievement.target && (
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs text-gray-600">
                          <span>Progress</span>
                          <span>
                            {achievement.progress}/{achievement.target}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-yellow-400 to-amber-500 rounded-full"
                            style={{
                              width: `${(achievement.progress / achievement.target) * 100}%`,
                            }}
                          />
                        </div>
                      </div>
                    )}
                    {achievement.unlocked && (
                      <div className="flex items-center gap-1 text-yellow-600">
                        <Star className="w-4 h-4 fill-current" />
                        <span className="text-sm font-semibold">Unlocked!</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white rounded-xl shadow-lg p-6 border-2 border-blue-300">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-blue-700">Continue Learning</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="p-4 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all shadow-md">
              <p className="font-bold mb-1">Practice Weak Topics</p>
              <p className="text-sm opacity-90">Focus on Statistics & Geometry</p>
            </button>
            <button className="p-4 bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 transition-all shadow-md">
              <p className="font-bold mb-1">Daily Challenge</p>
              <p className="text-sm opacity-90">Complete today's mixed quiz</p>
            </button>
            <button className="p-4 bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg hover:from-purple-600 hover:to-purple-700 transition-all shadow-md">
              <p className="font-bold mb-1">Review Mistakes</p>
              <p className="text-sm opacity-90">12 questions to revisit</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
