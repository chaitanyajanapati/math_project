import { useState, useEffect, useCallback } from 'react';
import { Clock, Play, Pause, RotateCcw } from 'lucide-react';

interface TimerProps {
  mode?: 'countdown' | 'stopwatch';
  initialSeconds?: number;
  onTimeUp?: () => void;
  onTimeUpdate?: (seconds: number) => void;
  autoStart?: boolean;
}

export default function Timer({ 
  mode = 'stopwatch', 
  initialSeconds = 300, 
  onTimeUp, 
  onTimeUpdate,
  autoStart = false 
}: TimerProps) {
  const [seconds, setSeconds] = useState(mode === 'countdown' ? initialSeconds : 0);
  const [isRunning, setIsRunning] = useState(autoStart);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null;

    if (isRunning) {
      interval = setInterval(() => {
        setSeconds(prev => {
          const newValue = mode === 'countdown' ? prev - 1 : prev + 1;
          
          // Notify parent of time update
          if (onTimeUpdate) {
            onTimeUpdate(newValue);
          }

          // Handle countdown reaching zero
          if (mode === 'countdown' && newValue <= 0) {
            setIsRunning(false);
            if (onTimeUp) {
              onTimeUp();
            }
            return 0;
          }

          return newValue;
        });
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRunning, mode, onTimeUp, onTimeUpdate]);

  const toggleTimer = useCallback(() => {
    setIsRunning(prev => !prev);
  }, []);

  const resetTimer = useCallback(() => {
    setIsRunning(false);
    setSeconds(mode === 'countdown' ? initialSeconds : 0);
  }, [mode, initialSeconds]);

  const formatTime = (totalSeconds: number): string => {
    const mins = Math.floor(Math.abs(totalSeconds) / 60);
    const secs = Math.abs(totalSeconds) % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getColor = (): string => {
    if (mode === 'countdown') {
      if (seconds <= 10) return 'text-red-600';
      if (seconds <= 30) return 'text-orange-600';
      return 'text-blue-600';
    }
    return 'text-blue-600';
  };

  return (
    <div className="flex items-center gap-2 bg-white rounded-lg shadow-md px-4 py-2 border-2 border-blue-200">
      <Clock className={`w-5 h-5 ${getColor()}`} />
      <span className={`font-mono text-xl font-bold ${getColor()}`}>
        {formatTime(seconds)}
      </span>
      <div className="flex gap-1 ml-2">
        <button
          onClick={toggleTimer}
          className="p-1.5 rounded-md hover:bg-blue-100 transition"
          title={isRunning ? 'Pause' : 'Start'}
        >
          {isRunning ? (
            <Pause className="w-4 h-4 text-blue-600" />
          ) : (
            <Play className="w-4 h-4 text-green-600" />
          )}
        </button>
        <button
          onClick={resetTimer}
          className="p-1.5 rounded-md hover:bg-gray-100 transition"
          title="Reset"
        >
          <RotateCcw className="w-4 h-4 text-gray-600" />
        </button>
      </div>
    </div>
  );
}
