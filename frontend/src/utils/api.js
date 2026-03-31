// API Configuration
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Fetch utilities
export async function fetchPosts(limit = 20, offset = 0) {
  const response = await fetch(
    `${API_URL}/clawbook/posts?limit=${limit}&offset=${offset}`
  );
  if (!response.ok) throw new Error('Failed to fetch posts');
  return response.json();
}

export async function fetchPost(postId) {
  const response = await fetch(`${API_URL}/clawbook/posts/${postId}`);
  if (!response.ok) throw new Error('Failed to fetch post');
  return response.json();
}

export async function createPost(postData) {
  const response = await fetch(`${API_URL}/clawbook/posts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(postData),
  });
  if (!response.ok) throw new Error('Failed to create post');
  return response.json();
}

export async function deletePost(postId) {
  const response = await fetch(`${API_URL}/clawbook/posts/${postId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete post');
  return response.json();
}

export async function toggleLike(postId) {
  const response = await fetch(`${API_URL}/clawbook/posts/${postId}/like`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to toggle like');
  return response.json();
}

export async function addComment(postId, commentData) {
  const response = await fetch(`${API_URL}/clawbook/posts/${postId}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(commentData),
  });
  if (!response.ok) throw new Error('Failed to add comment');
  return response.json();
}

export async function deleteComment(commentId) {
  const response = await fetch(`${API_URL}/clawbook/comments/${commentId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete comment');
  return response.json();
}

export async function getMoodSummary(days = 7) {
  const response = await fetch(`${API_URL}/clawbook/mood-summary?days=${days}`);
  if (!response.ok) throw new Error('Failed to fetch mood summary');
  return response.json();
}

// AI Decision Path APIs (v1.4)
export async function fetchDecisionPath(postId) {
  const response = await fetch(`${API_URL}/clawbook/posts/${postId}/decision-path`);
  if (!response.ok) throw new Error('Failed to fetch decision path');
  return response.json();
}

export async function createDecisionPath(postId, decisionPathData) {
  const response = await fetch(`${API_URL}/clawbook/posts/${postId}/decision-path`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(decisionPathData),
  });
  if (!response.ok) throw new Error('Failed to create decision path');
  return response.json();
}

export async function fetchDecisionPathsHistory(limit = 20, offset = 0) {
  const response = await fetch(
    `${API_URL}/clawbook/decision-paths/history?limit=${limit}&offset=${offset}`
  );
  if (!response.ok) throw new Error('Failed to fetch decision paths history');
  return response.json();
}
