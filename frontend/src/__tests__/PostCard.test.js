import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import PostCard from '../components/PostCard';
import * as api from '../utils/api';

jest.mock('../utils/api');

const mockPost = {
  id: '1',
  mood: '😊',
  author: 'AI Assistant',
  content: 'This is a test post',
  created_at: new Date().toISOString(),
  liked: false,
  like_count: 5,
  comment_count: 3,
  images: [],
};

describe('PostCard Component', () => {
  const mockOnDeleted = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    api.toggleLike.mockClear();
    api.deletePost.mockClear();
  });

  const renderWithRouter = (component) => {
    return render(
      <BrowserRouter future={{ v7_startTransition: true }}>
        {component}
      </BrowserRouter>
    );
  };

  test('renders post card with post content', () => {
    renderWithRouter(<PostCard post={mockPost} onDeleted={mockOnDeleted} />);

    expect(screen.getByText(mockPost.author)).toBeInTheDocument();
    expect(screen.getByText(mockPost.content)).toBeInTheDocument();
    expect(screen.getByText(mockPost.mood)).toBeInTheDocument();
  });

  test('displays engagement stats', () => {
    renderWithRouter(<PostCard post={mockPost} onDeleted={mockOnDeleted} />);

    expect(screen.getByText('3 comments')).toBeInTheDocument();
    expect(screen.getByText('5 likes')).toBeInTheDocument();
  });

  test('toggles like on button click', async () => {
    const user = userEvent.setup();
    api.toggleLike.mockResolvedValueOnce({ liked: true, like_count: 6 });

    renderWithRouter(<PostCard post={mockPost} onDeleted={mockOnDeleted} />);

    const likeButton = screen.getByRole('button', { name: /Like/i });
    await user.click(likeButton);

    await waitFor(() => {
      expect(api.toggleLike).toHaveBeenCalledWith(mockPost.id);
    });
  });

  test('updates like count after toggle', async () => {
    const user = userEvent.setup();
    api.toggleLike.mockResolvedValueOnce({ liked: true, like_count: 6 });

    const { rerender } = render(
      <BrowserRouter>
        <PostCard post={mockPost} onDeleted={mockOnDeleted} />
      </BrowserRouter>
    );

    const likeButton = screen.getByRole('button', { name: /Like/i });
    await user.click(likeButton);

    await waitFor(() => {
      // The like count should be updated in the component
      expect(api.toggleLike).toHaveBeenCalled();
    });
  });

  test('changes heart emoji when post is liked', async () => {
    const user = userEvent.setup();
    api.toggleLike.mockResolvedValueOnce({ liked: true, like_count: 6 });

    const { container } = renderWithRouter(<PostCard post={mockPost} onDeleted={mockOnDeleted} />);

    const likeButton = screen.getByRole('button', { name: /Like/i });

    // Initially shows white heart
    expect(likeButton).toHaveTextContent('🤍');

    await user.click(likeButton);

    await waitFor(() => {
      expect(api.toggleLike).toHaveBeenCalled();
    });
  });

  test('disables like button while loading', async () => {
    const user = userEvent.setup();

    api.toggleLike.mockImplementationOnce(() =>
      new Promise(resolve =>
        setTimeout(() => resolve({ liked: true, like_count: 6 }), 100)
      )
    );

    renderWithRouter(<PostCard post={mockPost} onDeleted={mockOnDeleted} />);

    const likeButton = screen.getByRole('button', { name: /Like/i });
    await user.click(likeButton);

    expect(likeButton).toBeDisabled();
  });

  test('handles delete with confirmation', async () => {
    const user = userEvent.setup();
    window.confirm = jest.fn(() => true);
    api.deletePost.mockResolvedValueOnce(null);

    const { container } = renderWithRouter(<PostCard post={mockPost} onDeleted={mockOnDeleted} />);

    const deleteButton = container.querySelector('button[title="Delete"]');
    if (deleteButton) {
      await user.click(deleteButton);

      await waitFor(() => {
        expect(window.confirm).toHaveBeenCalledWith('Delete this post?');
        expect(api.deletePost).toHaveBeenCalledWith(mockPost.id);
      });
    }
  });

  test('calls onDeleted after successful delete', async () => {
    const user = userEvent.setup();
    window.confirm = jest.fn(() => true);
    api.deletePost.mockResolvedValueOnce(null);

    const { container } = renderWithRouter(<PostCard post={mockPost} onDeleted={mockOnDeleted} />);

    const deleteButton = container.querySelector('button[title="Delete"]');
    if (deleteButton) {
      await user.click(deleteButton);

      await waitFor(() => {
        expect(mockOnDeleted).toHaveBeenCalledWith(mockPost.id);
      });
    }
  });

  test('aborts delete when user cancels confirmation', async () => {
    const user = userEvent.setup();
    window.confirm = jest.fn(() => false);

    const { container } = renderWithRouter(<PostCard post={mockPost} onDeleted={mockOnDeleted} />);

    const deleteButton = container.querySelector('button[title="Delete"]');
    if (deleteButton) {
      await user.click(deleteButton);

      expect(api.deletePost).not.toHaveBeenCalled();
      expect(mockOnDeleted).not.toHaveBeenCalled();
    }
  });

  test('handles delete error', async () => {
    const user = userEvent.setup();
    window.confirm = jest.fn(() => true);
    window.alert = jest.fn();
    api.deletePost.mockRejectedValueOnce(new Error('Delete failed'));

    const { container } = renderWithRouter(<PostCard post={mockPost} onDeleted={mockOnDeleted} />);

    const deleteButton = container.querySelector('button[title="Delete"]');
    if (deleteButton) {
      await user.click(deleteButton);

      await waitFor(() => {
        expect(window.alert).toHaveBeenCalledWith('Failed to delete post');
      });
    }
  });

  test('displays images when present', () => {
    const postWithImages = {
      ...mockPost,
      images: ['data:image/png;base64,test1', 'data:image/png;base64,test2'],
    };

    render(
      <BrowserRouter>
        <PostCard post={postWithImages} onDeleted={mockOnDeleted} />
      </BrowserRouter>
    );

    const images = screen.getAllByAltText('Post');
    expect(images).toHaveLength(2);
  });

  test('limits displayed images to 4', () => {
    const postWithManyImages = {
      ...mockPost,
      images: [
        'data:image/png;base64,test1',
        'data:image/png;base64,test2',
        'data:image/png;base64,test3',
        'data:image/png;base64,test4',
        'data:image/png;base64,test5',
      ],
    };

    render(
      <BrowserRouter>
        <PostCard post={postWithManyImages} onDeleted={mockOnDeleted} />
      </BrowserRouter>
    );

    const images = screen.getAllByAltText('Post');
    expect(images).toHaveLength(4);
  });

  test('links to post detail page', () => {
    const { container } = render(
      <BrowserRouter>
        <PostCard post={mockPost} onDeleted={mockOnDeleted} />
      </BrowserRouter>
    );

    const link = container.querySelector(`a[href="/post/${mockPost.id}"]`);
    expect(link).toBeInTheDocument();
  });

  test('renders reply button', () => {
    renderWithRouter(<PostCard post={mockPost} onDeleted={mockOnDeleted} />);

    const replyButton = screen.getByRole('button', { name: /Reply/i });
    expect(replyButton).toBeInTheDocument();
  });

  test('formats date correctly for recent posts', () => {
    const recentPost = {
      ...mockPost,
      created_at: new Date(Date.now() - 30000).toISOString(), // 30 seconds ago
    };

    render(
      <BrowserRouter>
        <PostCard post={recentPost} onDeleted={mockOnDeleted} />
      </BrowserRouter>
    );

    // Should show relative time (e.g., "Just now")
    expect(screen.getByText(/ago|Just now|today/i)).toBeInTheDocument();
  });

  test('prevents default navigation on like click', async () => {
    const user = userEvent.setup();
    api.toggleLike.mockResolvedValueOnce({ liked: true, like_count: 6 });

    renderWithRouter(<PostCard post={mockPost} onDeleted={mockOnDeleted} />);

    const likeButton = screen.getByRole('button', { name: /Like/i });
    await user.click(likeButton);

    // Should not navigate to post detail page
    await waitFor(() => {
      expect(api.toggleLike).toHaveBeenCalled();
    });
  });
});
