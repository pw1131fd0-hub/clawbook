import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import DecisionPaths from '../pages/DecisionPaths';
import * as api from '../utils/api';

jest.mock('../utils/api');
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn()
}));

const mockDecisionPathsHistory = {
  paths: [
    {
      id: 'dp-1',
      post_id: 'post-1',
      final_decision: 'Go with Option A',
      created_at: '2026-04-01T10:00:00Z',
      confidence_score: 0.85,
      model_used: 'ollama/llama3'
    },
    {
      id: 'dp-2',
      post_id: 'post-2',
      final_decision: 'Choose Option B',
      created_at: '2026-03-31T15:30:00Z',
      confidence_score: 0.72,
      model_used: 'openai/gpt-4o'
    },
    {
      id: 'dp-3',
      post_id: 'post-3',
      final_decision: 'Select Option C',
      created_at: '2026-03-30T09:15:00Z',
      confidence_score: 0.65,
      model_used: 'gemini-2.0-flash'
    }
  ],
  total: 3
};

describe('DecisionPaths Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    api.fetchDecisionPathsHistory.mockImplementation(() => new Promise(() => {}));
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );
    expect(screen.getByText('Loading decision paths...')).toBeInTheDocument();
  });

  test('renders page title and subtitle', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue(mockDecisionPathsHistory);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('AI Decision Paths')).toBeInTheDocument();
      expect(screen.getByText('Explore the reasoning behind AI decisions')).toBeInTheDocument();
    });
  });

  test('displays all decision paths', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue(mockDecisionPathsHistory);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Go with Option A')).toBeInTheDocument();
      expect(screen.getByText('Choose Option B')).toBeInTheDocument();
      expect(screen.getByText('Select Option C')).toBeInTheDocument();
    });
  });

  test('displays confidence scores for each path', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue(mockDecisionPathsHistory);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('85%')).toBeInTheDocument();
      expect(screen.getByText('72%')).toBeInTheDocument();
      expect(screen.getByText('65%')).toBeInTheDocument();
    });
  });

  test('displays model used for each path', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue(mockDecisionPathsHistory);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Model: ollama\/llama3/)).toBeInTheDocument();
      expect(screen.getByText(/Model: openai\/gpt-4o/)).toBeInTheDocument();
      expect(screen.getByText(/Model: gemini-2.0-flash/)).toBeInTheDocument();
    });
  });

  test('displays creation timestamps', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue(mockDecisionPathsHistory);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      const timestamps = screen.getAllByText(/Created:/);
      expect(timestamps.length).toBeGreaterThan(0);
    });
  });

  test('calls fetchDecisionPathsHistory with correct parameters on first load', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue(mockDecisionPathsHistory);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(api.fetchDecisionPathsHistory).toHaveBeenCalledWith(20, 0);
    });
  });

  test('displays empty state when no paths available', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue({ paths: [], total: 0 });
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('No decision paths found')).toBeInTheDocument();
    });
  });

  test('shows pagination controls', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue(mockDecisionPathsHistory);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('← Previous')).toBeInTheDocument();
      expect(screen.getByText('Next →')).toBeInTheDocument();
      expect(screen.getByText('Page 1')).toBeInTheDocument();
    });
  });

  test('previous button is disabled on first page', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue(mockDecisionPathsHistory);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      const prevButton = screen.getByText('← Previous');
      expect(prevButton).toBeDisabled();
    });
  });

  test('next button is disabled when items less than limit', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue(mockDecisionPathsHistory);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      const nextButton = screen.getByText('Next →');
      expect(nextButton).toBeDisabled();
    });
  });

  test('navigates to next page when Next button clicked', async () => {
    const manyPaths = {
      ...mockDecisionPathsHistory,
      paths: Array.from({ length: 20 }, (_, i) => ({
        ...mockDecisionPathsHistory.paths[0],
        id: `dp-${i}`,
        post_id: `post-${i}`
      }))
    };

    api.fetchDecisionPathsHistory.mockResolvedValue(manyPaths);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Page 1')).toBeInTheDocument();
    });

    const nextButton = screen.getByText('Next →');
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(api.fetchDecisionPathsHistory).toHaveBeenCalledWith(20, 20);
    });
  });

  test('displays error message on fetch failure', async () => {
    api.fetchDecisionPathsHistory.mockRejectedValue(new Error('API Error'));
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });

  test('shows back to feed button on error', async () => {
    api.fetchDecisionPathsHistory.mockRejectedValue(new Error('API Error'));
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Back to Feed')).toBeInTheDocument();
    });
  });

  test('shows back to feed button in empty state', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue({ paths: [], total: 0 });
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      const buttons = screen.getAllByText('Back to Feed');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  test('path items are clickable', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue(mockDecisionPathsHistory);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      const pathItem = screen.getByText('Go with Option A').closest('div[class*="p-4"]');
      expect(pathItem).toBeInTheDocument();
    });
  });

  test('renders confidence indicator for each path', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue(mockDecisionPathsHistory);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      const confidenceElements = screen.getAllByText(/%/);
      expect(confidenceElements.length).toBeGreaterThan(0);
    });
  });

  test('handles empty model_used field gracefully', async () => {
    const pathsNoModel = {
      paths: [
        {
          id: 'dp-1',
          post_id: 'post-1',
          final_decision: 'Decision 1',
          created_at: '2026-04-01T10:00:00Z',
          confidence_score: 0.85,
          model_used: null
        }
      ],
      total: 1
    };

    api.fetchDecisionPathsHistory.mockResolvedValue(pathsNoModel);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Decision 1')).toBeInTheDocument();
    });
  });

  test('handles missing confidence_score field', async () => {
    const pathsNoScore = {
      paths: [
        {
          id: 'dp-1',
          post_id: 'post-1',
          final_decision: 'Decision 1',
          created_at: '2026-04-01T10:00:00Z',
          model_used: 'ollama/llama3'
        }
      ],
      total: 1
    };

    api.fetchDecisionPathsHistory.mockResolvedValue(pathsNoScore);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Decision 1')).toBeInTheDocument();
    });
  });

  test('formats dates correctly', async () => {
    api.fetchDecisionPathsHistory.mockResolvedValue(mockDecisionPathsHistory);
    render(
      <BrowserRouter>
        <DecisionPaths />
      </BrowserRouter>
    );

    await waitFor(() => {
      const timestamps = screen.getAllByText(/Created:/);
      expect(timestamps.length).toBeGreaterThan(0);
    });
  });
});
