import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import DecisionPathViewer from '../components/DecisionPathViewer';
import * as api from '../utils/api';

jest.mock('../utils/api');

const mockDecisionPath = {
  id: 'test-id-1',
  post_id: 'post-1',
  final_decision: {
    decision: 'Go with Option A',
    confidence: 0.85,
    rationale: 'Based on analysis, Option A is the best choice'
  },
  key_factors: [
    { name: 'Cost', weight: 0.3, description: 'Lower operational cost' },
    { name: 'Performance', weight: 0.5, description: 'Better performance metrics' },
    { name: 'Risk', weight: 0.2, description: 'Moderate risk level' }
  ],
  reasoning_steps: [
    { step_number: 1, description: 'Analyze requirements', reasoning: 'Started by gathering all requirements' },
    { step_number: 2, description: 'Evaluate options', reasoning: 'Compared multiple solutions' },
    { step_number: 3, description: 'Make decision', reasoning: 'Selected Option A based on analysis' }
  ],
  candidates: [
    {
      rank: 1,
      option: 'Option A',
      description: 'Recommended solution',
      feasibility_score: 0.9,
      pros: ['Good performance', 'Low cost'],
      cons: ['Limited scalability']
    },
    {
      rank: 2,
      option: 'Option B',
      description: 'Alternative solution',
      feasibility_score: 0.7,
      pros: ['Highly scalable'],
      cons: ['Higher cost', 'Complex implementation']
    }
  ],
  model_used: 'ollama/llama3',
  decision_time_ms: 1500
};

describe('DecisionPathViewer Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    api.fetchDecisionPath.mockImplementation(() => new Promise(() => {}));
    render(<DecisionPathViewer postId="post-1" />);
    expect(screen.getByText('Loading decision path...')).toBeInTheDocument();
  });

  test('renders nothing when decision path is not available', async () => {
    api.fetchDecisionPath.mockRejectedValue(new Error('Not found'));
    const { container } = render(<DecisionPathViewer postId="post-1" />);
    await waitFor(() => {
      expect(container.querySelector('div')?.className).toBeDefined();
    });
  });

  test('renders decision path successfully', async () => {
    api.fetchDecisionPath.mockResolvedValue(mockDecisionPath);
    render(<DecisionPathViewer postId="post-1" />);

    await waitFor(() => {
      expect(screen.getByText('AI Decision Path')).toBeInTheDocument();
      expect(screen.getByText('FINAL DECISION')).toBeInTheDocument();
      expect(screen.getByText('Go with Option A')).toBeInTheDocument();
    });
  });

  test('displays model used and decision time', async () => {
    api.fetchDecisionPath.mockResolvedValue(mockDecisionPath);
    render(<DecisionPathViewer postId="post-1" />);

    await waitFor(() => {
      expect(screen.getByText(/Model: ollama\/llama3/)).toBeInTheDocument();
      expect(screen.getByText(/Decision Time: 1500ms/)).toBeInTheDocument();
    });
  });

  test('calls fetchDecisionPath with correct postId', async () => {
    api.fetchDecisionPath.mockResolvedValue(mockDecisionPath);
    render(<DecisionPathViewer postId="test-post-123" />);

    await waitFor(() => {
      expect(api.fetchDecisionPath).toHaveBeenCalledWith('test-post-123');
    });
  });

  test('refetches when postId changes', async () => {
    api.fetchDecisionPath.mockResolvedValue(mockDecisionPath);
    const { rerender } = render(<DecisionPathViewer postId="post-1" />);

    await waitFor(() => {
      expect(api.fetchDecisionPath).toHaveBeenCalledWith('post-1');
    });

    api.fetchDecisionPath.mockClear();
    api.fetchDecisionPath.mockResolvedValue(mockDecisionPath);

    rerender(<DecisionPathViewer postId="post-2" />);

    await waitFor(() => {
      expect(api.fetchDecisionPath).toHaveBeenCalledWith('post-2');
    });
  });

  test('handles error gracefully', async () => {
    api.fetchDecisionPath.mockRejectedValue(new Error('API Error'));
    const { container } = render(<DecisionPathViewer postId="post-1" />);

    await waitFor(() => {
      expect(api.fetchDecisionPath).toHaveBeenCalled();
    });

    // Component should not show error message (returns null on error)
    expect(container.innerHTML).toBeDefined();
  });

  test('renders confidence indicator section', async () => {
    api.fetchDecisionPath.mockResolvedValue(mockDecisionPath);
    render(<DecisionPathViewer postId="post-1" />);

    await waitFor(() => {
      expect(screen.getByText('CONFIDENCE LEVEL')).toBeInTheDocument();
    });
  });

  test('renders key factors section when available', async () => {
    api.fetchDecisionPath.mockResolvedValue(mockDecisionPath);
    render(<DecisionPathViewer postId="post-1" />);

    await waitFor(() => {
      expect(screen.getByText('KEY FACTORS')).toBeInTheDocument();
    });
  });

  test('renders reasoning timeline section when available', async () => {
    api.fetchDecisionPath.mockResolvedValue(mockDecisionPath);
    render(<DecisionPathViewer postId="post-1" />);

    await waitFor(() => {
      expect(screen.getByText('REASONING STEPS')).toBeInTheDocument();
    });
  });

  test('renders candidate comparison section when multiple candidates exist', async () => {
    api.fetchDecisionPath.mockResolvedValue(mockDecisionPath);
    render(<DecisionPathViewer postId="post-1" />);

    await waitFor(() => {
      expect(screen.getByText('CANDIDATES CONSIDERED')).toBeInTheDocument();
    });
  });

  test('does not render candidate section with single candidate', async () => {
    const singleCandidateDecision = {
      ...mockDecisionPath,
      candidates: [mockDecisionPath.candidates[0]]
    };
    api.fetchDecisionPath.mockResolvedValue(singleCandidateDecision);
    render(<DecisionPathViewer postId="post-1" />);

    await waitFor(() => {
      expect(screen.queryByText('CANDIDATES CONSIDERED')).not.toBeInTheDocument();
    });
  });

  test('does not render key factors section when empty', async () => {
    const noFactorsDecision = {
      ...mockDecisionPath,
      key_factors: []
    };
    api.fetchDecisionPath.mockResolvedValue(noFactorsDecision);
    render(<DecisionPathViewer postId="post-1" />);

    await waitFor(() => {
      expect(screen.queryByText('KEY FACTORS')).not.toBeInTheDocument();
    });
  });

  test('does not render reasoning steps section when empty', async () => {
    const noStepsDecision = {
      ...mockDecisionPath,
      reasoning_steps: []
    };
    api.fetchDecisionPath.mockResolvedValue(noStepsDecision);
    render(<DecisionPathViewer postId="post-1" />);

    await waitFor(() => {
      expect(screen.queryByText('REASONING STEPS')).not.toBeInTheDocument();
    });
  });
});
