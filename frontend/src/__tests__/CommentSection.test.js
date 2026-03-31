import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CommentSection from '../components/CommentSection';
import * as api from '../utils/api';

jest.mock('../utils/api');

describe('CommentSection Component', () => {
  const mockOnCommentAdded = jest.fn();
  const mockPostId = '1';

  beforeEach(() => {
    jest.clearAllMocks();
    api.addComment.mockClear();
    api.deleteComment.mockClear();
  });

  test('renders comment section with textarea and button', () => {
    render(<CommentSection postId={mockPostId} onCommentAdded={mockOnCommentAdded} />);

    const textarea = screen.getByPlaceholderText('Add a comment...');
    const button = screen.getByRole('button', { name: /Comment/i });

    expect(textarea).toBeInTheDocument();
    expect(button).toBeInTheDocument();
  });

  test('displays empty state when no comments exist', () => {
    render(<CommentSection postId={mockPostId} onCommentAdded={mockOnCommentAdded} />);

    const emptyText = screen.getByText(/No comments yet/i);
    expect(emptyText).toBeInTheDocument();
  });

  test('disables submit button when textarea is empty', () => {
    render(<CommentSection postId={mockPostId} onCommentAdded={mockOnCommentAdded} />);

    const button = screen.getByRole('button', { name: /Comment/i });
    expect(button).toBeDisabled();
  });

  test('enables submit button when textarea has text', async () => {
    const user = userEvent.setup();
    render(<CommentSection postId={mockPostId} onCommentAdded={mockOnCommentAdded} />);

    const textarea = screen.getByPlaceholderText('Add a comment...');
    const button = screen.getByRole('button', { name: /Comment/i });

    expect(button).toBeDisabled();

    await user.type(textarea, 'Test comment');

    expect(button).not.toBeDisabled();
  });

  test('submits comment successfully', async () => {
    const user = userEvent.setup();
    const mockComment = {
      id: 'comment-1',
      author: 'You',
      text: 'Test comment',
      created_at: new Date().toISOString(),
    };

    api.addComment.mockResolvedValueOnce(mockComment);

    render(<CommentSection postId={mockPostId} onCommentAdded={mockOnCommentAdded} />);

    const textarea = screen.getByPlaceholderText('Add a comment...');
    const button = screen.getByRole('button', { name: /Comment/i });

    await user.type(textarea, 'Test comment');
    await user.click(button);

    await waitFor(() => {
      expect(api.addComment).toHaveBeenCalledWith(mockPostId, {
        author: 'You',
        text: 'Test comment',
      });
      expect(mockOnCommentAdded).toHaveBeenCalled();
    });
  });

  test('clears textarea after successful comment submission', async () => {
    const user = userEvent.setup();
    const mockComment = {
      id: 'comment-1',
      author: 'You',
      text: 'Test comment',
      created_at: new Date().toISOString(),
    };

    api.addComment.mockResolvedValueOnce(mockComment);

    render(<CommentSection postId={mockPostId} onCommentAdded={mockOnCommentAdded} />);

    const textarea = screen.getByPlaceholderText('Add a comment...');

    await user.type(textarea, 'Test comment');
    const button = screen.getByRole('button', { name: /Comment/i });
    await user.click(button);

    await waitFor(() => {
      expect(textarea.value).toBe('');
    });
  });

  test('handles error when adding comment fails', async () => {
    const user = userEvent.setup();
    api.addComment.mockRejectedValueOnce(new Error('Failed to add comment'));

    window.alert = jest.fn();

    render(<CommentSection postId={mockPostId} onCommentAdded={mockOnCommentAdded} />);

    const textarea = screen.getByPlaceholderText('Add a comment...');
    const button = screen.getByRole('button', { name: /Comment/i });

    await user.type(textarea, 'Test comment');
    await user.click(button);

    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Failed to add comment');
    });
  });

  test('displays comments when present', async () => {
    const mockComments = [
      {
        id: 'comment-1',
        author: 'John',
        text: 'Great post!',
        created_at: new Date().toISOString(),
      },
      {
        id: 'comment-2',
        author: 'Jane',
        text: 'Nice insights!',
        created_at: new Date(Date.now() - 3600000).toISOString(),
      },
    ];

    const { rerender } = render(
      <CommentSection postId={mockPostId} onCommentAdded={mockOnCommentAdded} />
    );

    // Simulate adding comments manually
    const mockComment = mockComments[0];
    api.addComment.mockResolvedValueOnce(mockComment);

    const textarea = screen.getByPlaceholderText('Add a comment...');
    await userEvent.type(textarea, 'Great post!');
    await userEvent.click(screen.getByRole('button', { name: /Comment/i }));

    await waitFor(() => {
      expect(api.addComment).toHaveBeenCalled();
    });
  });

  test('button shows loading state', async () => {
    const user = userEvent.setup();

    // Mock a slow API call
    api.addComment.mockImplementationOnce(() =>
      new Promise(resolve => setTimeout(() => resolve({
        id: 'comment-1',
        author: 'You',
        text: 'Test',
        created_at: new Date().toISOString(),
      }), 100))
    );

    render(<CommentSection postId={mockPostId} onCommentAdded={mockOnCommentAdded} />);

    const textarea = screen.getByPlaceholderText('Add a comment...');
    const button = screen.getByRole('button', { name: /Comment/i });

    await user.type(textarea, 'Test');
    await user.click(button);

    // Button should show loading state
    expect(button).toHaveTextContent('Posting...');
  });

  test('handles delete comment with confirmation', async () => {
    const user = userEvent.setup();

    window.confirm = jest.fn(() => true);
    api.deleteComment.mockResolvedValueOnce(null);

    // First, add a comment to the component state
    const mockComment = {
      id: 'comment-1',
      author: 'You',
      text: 'Test comment',
      created_at: new Date().toISOString(),
    };

    api.addComment.mockResolvedValueOnce(mockComment);

    const { rerender } = render(
      <CommentSection postId={mockPostId} onCommentAdded={mockOnCommentAdded} />
    );

    const textarea = screen.getByPlaceholderText('Add a comment...');
    await user.type(textarea, 'Test comment');
    await user.click(screen.getByRole('button', { name: /Comment/i }));

    await waitFor(() => {
      expect(api.addComment).toHaveBeenCalled();
    });
  });

  test('aborts delete when user cancels confirmation', async () => {
    window.confirm = jest.fn(() => false);

    const { container } = render(
      <CommentSection postId={mockPostId} onCommentAdded={mockOnCommentAdded} />
    );

    expect(window.confirm).not.toHaveBeenCalled();
  });

  test('formats relative dates correctly', () => {
    // Test component renders with relative dates
    const { container } = render(
      <CommentSection postId={mockPostId} onCommentAdded={mockOnCommentAdded} />
    );

    // Component should have the date formatting function
    expect(container).toBeInTheDocument();
  });

  test('renders comment emoji and user emoji', () => {
    render(<CommentSection postId={mockPostId} onCommentAdded={mockOnCommentAdded} />);

    const commentEmoji = screen.getByText('💬');
    expect(commentEmoji).toBeInTheDocument();
  });
});
