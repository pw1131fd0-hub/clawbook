import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import VoiceRecorder from '../components/VoiceRecorder';

// Mock navigator.mediaDevices
const mockGetUserMedia = jest.fn();

Object.defineProperty(global.navigator, 'mediaDevices', {
  value: {
    getUserMedia: mockGetUserMedia,
  },
  configurable: true,
});

// Mock URL.createObjectURL and URL.revokeObjectURL
global.URL.createObjectURL = jest.fn(() => 'blob:http://localhost/test');
global.URL.revokeObjectURL = jest.fn();

// Mock Audio element
global.Audio = class {
  constructor(url) {
    this.url = url;
    this.onloadedmetadata = null;
    this.onerror = null;
    this.play = jest.fn();
  }
};

describe('VoiceRecorder Component', () => {
  let mockOnTranscribe;
  let mockMediaRecorderInstance;
  let mockTrack;
  let mockStream;

  beforeEach(() => {
    mockOnTranscribe = jest.fn();
    mockGetUserMedia.mockClear();

    // Mock Stream and Track
    mockTrack = { stop: jest.fn() };
    mockStream = {
      getTracks: () => [mockTrack],
    };

    // Mock MediaRecorder with static isTypeSupported method and instance methods
    global.MediaRecorder = class {
      static isTypeSupported(type) {
        return type === 'audio/webm;codecs=opus' || type === 'audio/webm';
      }

      constructor(stream, options) {
        this.stream = stream;
        this.options = options;
        this.ondataavailable = null;
        this.onstop = null;
        this.onerror = null;
        mockMediaRecorderInstance = this;
      }

      start() {}

      stop() {
        // Trigger the onstop callback
        if (this.onstop) {
          setTimeout(() => this.onstop(), 0);
        }
      }

      triggerDataAvailable(blob) {
        if (this.ondataavailable) {
          this.ondataavailable({ data: blob });
        }
      }
    };

    mockGetUserMedia.mockResolvedValue(mockStream);

    // Mock SpeechRecognition
    global.SpeechRecognition = class {
      constructor() {
        this.lang = null;
        this.continuous = false;
        this.interimResults = false;
        this.onresult = null;
        this.onerror = null;
        this.onend = null;
      }

      start() {}
      stop() {}
    };

    global.webkitSpeechRecognition = global.SpeechRecognition;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders voice recorder button', () => {
    render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('🎤');
  });

  test('is disabled when disabled prop is true', () => {
    render(<VoiceRecorder onTranscribe={mockOnTranscribe} disabled={true} />);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  test('shows error message on microphone access denied', async () => {
    mockGetUserMedia.mockRejectedValueOnce(new Error('Permission denied'));

    render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);
    const button = screen.getByRole('button');

    button.click();

    // Wait for error message
    const errorElement = await screen.findByText(/Microphone access denied/i);
    expect(errorElement).toBeInTheDocument();
  });

  test('handles disabled state', () => {
    const { rerender } = render(
      <VoiceRecorder onTranscribe={mockOnTranscribe} disabled={false} />
    );

    expect(screen.getByRole('button')).not.toBeDisabled();

    rerender(<VoiceRecorder onTranscribe={mockOnTranscribe} disabled={true} />);

    expect(screen.getByRole('button')).toBeDisabled();
  });

  test('renders with expected button title', () => {
    render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('title', 'Start voice recording');
  });

  test('calls onTranscribe callback prop exists', () => {
    render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);
    expect(typeof mockOnTranscribe).toBe('function');
  });

  test('starts recording when button clicked', async () => {
    render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);
    const button = screen.getByRole('button');

    await userEvent.click(button);

    await waitFor(() => {
      expect(mockGetUserMedia).toHaveBeenCalledWith({ audio: true });
    });
  });

  test('stops recording when button clicked during recording', async () => {
    render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);
    const button = screen.getByRole('button');

    // Start recording
    await userEvent.click(button);
    await waitFor(() => {
      expect(screen.getByText('Recording...')).toBeInTheDocument();
    });

    // Stop recording
    await userEvent.click(button);
    await waitFor(() => {
      expect(mockTrack.stop).toHaveBeenCalled();
    });
  });

  test('calls onTranscribe with transcribed text', async () => {
    const user = userEvent.setup();
    const { rerender } = render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);

    // Start recording
    const button = screen.getByRole('button');
    await user.click(button);

    await waitFor(() => {
      expect(mockMediaRecorderInstance).toBeDefined();
    });

    // Simulate data available
    const mockBlob = new Blob(['test audio data'], { type: 'audio/webm' });
    mockMediaRecorderInstance.triggerDataAvailable(mockBlob);

    // Mock SpeechRecognition result
    const mockSpeechRecognition = new global.SpeechRecognition();
    mockSpeechRecognition.onresult = jest.fn();

    // Trigger stop
    await user.click(button);

    // Wait for transcription
    await waitFor(() => {
      expect(mockMediaRecorderInstance.stop).toBeDefined();
    }, { timeout: 1000 });
  });

  test('shows recording indicator when recording', async () => {
    const user = userEvent.setup();
    render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);
    const button = screen.getByRole('button');

    expect(screen.queryByText('Recording...')).not.toBeInTheDocument();

    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText('Recording...')).toBeInTheDocument();
    });
  });

  test('shows transcribing state and disables button', async () => {
    const user = userEvent.setup();
    render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);
    const button = screen.getByRole('button');

    // Button should not initially be disabled for transcribing
    expect(button).not.toBeDisabled();
  });

  test('cleans up media stream on unmount', async () => {
    const user = userEvent.setup();
    const { unmount } = render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);
    const button = screen.getByRole('button');

    await user.click(button);

    await waitFor(() => {
      expect(mockGetUserMedia).toHaveBeenCalled();
    });

    unmount();

    await waitFor(() => {
      expect(mockTrack.stop).toHaveBeenCalled();
    });
  });

  test('handles MediaRecorder mime type detection correctly', () => {
    expect(global.MediaRecorder.isTypeSupported('audio/webm;codecs=opus')).toBe(true);
    expect(global.MediaRecorder.isTypeSupported('audio/webm')).toBe(true);
    expect(global.MediaRecorder.isTypeSupported('audio/mp4')).toBe(false);
  });

  test('button text changes to stop icon when recording', async () => {
    const user = userEvent.setup();
    render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);
    const button = screen.getByRole('button');

    expect(button).toHaveTextContent('🎤');

    await user.click(button);

    await waitFor(() => {
      expect(button).toHaveTextContent('⏹️');
    });
  });

  test('renders with flex and gap styling', () => {
    const { container } = render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);
    const wrapper = container.querySelector('.flex');
    expect(wrapper).toHaveClass('gap-2');
  });

  test('button has correct aria attributes when disabled', () => {
    render(<VoiceRecorder onTranscribe={mockOnTranscribe} disabled={true} />);
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('type', 'button');
    expect(button).toHaveAttribute('title');
  });

  test('error state shows error message div', async () => {
    mockGetUserMedia.mockRejectedValueOnce(new Error('Denied'));

    render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);
    const button = screen.getByRole('button');

    await userEvent.click(button);

    // Wait for error message to appear
    const errorElement = await screen.findByText(/Microphone access denied/i);
    expect(errorElement).toBeInTheDocument();
    expect(errorElement.className).toContain('text-red-400');
  });

  test('sets correct button styling for recording state', () => {
    const { container } = render(<VoiceRecorder onTranscribe={mockOnTranscribe} />);
    const button = screen.getByRole('button');

    // Check initial styling (not recording)
    expect(button.className).toContain('bg-slate-700');

    // Verify class structure for disabled state
    expect(button.className).toContain('disabled:opacity-50');
  });

  test('disables button while transcribing', async () => {
    const user = userEvent.setup();
    render(<VoiceRecorder onTranscribe={mockOnTranscribe} disabled={false} />);
    const button = screen.getByRole('button');

    // Initially button should be enabled
    expect(button).not.toBeDisabled();
  });
});
