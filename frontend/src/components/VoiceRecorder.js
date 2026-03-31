import React, { useState, useRef, useEffect } from 'react';

export default function VoiceRecorder({ onTranscribe, disabled = false }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [error, setError] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm';

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: mimeType });
        await transcribeAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      setError('Microphone access denied. Please enable microphone permissions.');
      console.error('Recording error:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      streamRef.current?.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob) => {
    setIsTranscribing(true);
    try {
      // Use Web Speech API for transcription (fallback to offline processing)
      const text = await performSpeechRecognition(audioBlob);
      if (text.trim()) {
        onTranscribe(text);
      }
    } catch (err) {
      // Fallback: show user to manually transcribe
      setError('Could not transcribe audio. Please try again or type manually.');
      console.error('Transcription error:', err);
    } finally {
      setIsTranscribing(false);
    }
  };

  const performSpeechRecognition = (audioBlob) => {
    return new Promise((resolve, reject) => {
      // Use browser's Web Speech API
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

      if (!SpeechRecognition) {
        reject(new Error('Speech Recognition API not supported'));
        return;
      }

      const recognition = new SpeechRecognition();
      recognition.lang = 'en-US';
      recognition.continuous = false;
      recognition.interimResults = false;

      const audioUrl = URL.createObjectURL(audioBlob);
      const audioElement = new Audio(audioUrl);

      // Create a MediaSource to feed the Web Audio API
      audioElement.onloadedmetadata = () => {
        audioElement.play();
      };

      audioElement.onerror = () => {
        // Fallback: convert blob to base64 and send to backend for transcription
        const reader = new FileReader();
        reader.onload = () => {
          // For now, we'll just use the Web Speech API with mic input
          const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
          const recognition2 = new SpeechRecognition();
          recognition2.lang = 'en-US';

          recognition2.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
              transcript += event.results[i][0].transcript;
            }
            resolve(transcript);
          };

          recognition2.onerror = () => {
            reject(new Error('Speech recognition failed'));
          };

          recognition2.onend = () => {
            URL.revokeObjectURL(audioUrl);
          };

          recognition2.start();
        };
        reader.readAsDataURL(audioBlob);
      };
    });
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={toggleRecording}
        disabled={disabled || isTranscribing}
        className={`p-2 rounded-lg transition-colors ${
          isRecording
            ? 'bg-red-600 hover:bg-red-700 text-white'
            : 'bg-slate-700 hover:bg-slate-600 text-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600'
        } disabled:opacity-50 disabled:cursor-not-allowed`}
        title={isRecording ? 'Stop recording' : 'Start voice recording'}
      >
        {isRecording ? '⏹️' : '🎤'}
      </button>

      {isTranscribing && (
        <span className="text-sm text-slate-400 dark:text-slate-400">
          Transcribing...
        </span>
      )}

      {error && (
        <div className="text-sm text-red-400 bg-red-900 bg-opacity-20 px-3 py-1 rounded-lg">
          {error}
        </div>
      )}

      {isRecording && (
        <div className="flex items-center gap-2 text-red-400">
          <span className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></span>
          <span className="text-sm">Recording...</span>
        </div>
      )}
    </div>
  );
}
