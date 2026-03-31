import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SlackConfigModal from '../components/SlackConfigModal';

// Mock fetch
global.fetch = jest.fn();

describe('SlackConfigModal', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  afterEach(() => {
    fetch.mockReset();
  });

  test('renders modal when isOpen is true', () => {
    render(<SlackConfigModal isOpen={true} onClose={jest.fn()} />);
    expect(screen.getByText(/Slack Integration/i)).toBeInTheDocument();
  });

  test('does not render modal when isOpen is false', () => {
    render(<SlackConfigModal isOpen={false} onClose={jest.fn()} />);
    expect(screen.queryByText(/Slack Integration/i)).not.toBeInTheDocument();
  });

  test('loads existing configuration on mount', async () => {
    const mockConfig = {
      webhook_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXX',
      enabled: true,
      summary_enabled: true,
      summary_time: '10:00',
      high_mood_threshold: 4,
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockConfig,
    });

    render(<SlackConfigModal isOpen={true} onClose={jest.fn()} />);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/v1/slack/config');
    });
  });

  test('handles missing configuration gracefully', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    render(<SlackConfigModal isOpen={true} onClose={jest.fn()} />);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/v1/slack/config');
    });
  });

  test('saves configuration successfully', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: '123',
        webhook_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXX',
      }),
    });

    const onSuccess = jest.fn();
    render(<SlackConfigModal isOpen={true} onClose={jest.fn()} onSuccess={onSuccess} />);

    const webhookInput = screen.getByPlaceholderText(/hooks.slack.com/i);
    fireEvent.change(webhookInput, {
      target: { value: 'https://hooks.slack.com/services/T00000000/B00000000/XXXX' },
    });

    const saveButton = screen.getByText(/Save Configuration/i);
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  test('displays error message on save failure', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Invalid webhook URL' }),
    });

    render(<SlackConfigModal isOpen={true} onClose={jest.fn()} />);

    const webhookInput = screen.getByPlaceholderText(/hooks.slack.com/i);
    fireEvent.change(webhookInput, {
      target: { value: 'https://invalid.com' },
    });

    const saveButton = screen.getByText(/Save Configuration/i);
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText(/Invalid webhook URL/i)).toBeInTheDocument();
    });
  });

  test('tests webhook successfully', async () => {
    const mockConfig = {
      webhook_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXX',
      enabled: true,
    };

    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConfig,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'success' }),
      });

    render(<SlackConfigModal isOpen={true} onClose={jest.fn()} />);

    await waitFor(() => {
      const testButton = screen.getByText(/Test Webhook/i);
      fireEvent.click(testButton);
    });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/v1/slack/test',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
  });

  test('displays notification rule options', () => {
    render(<SlackConfigModal isOpen={true} onClose={jest.fn()} />);

    expect(screen.getByText(/Daily Summary Notification/i)).toBeInTheDocument();
    expect(screen.getByText(/High Mood Notifications/i)).toBeInTheDocument();
    expect(screen.getByText(/Milestone Notifications/i)).toBeInTheDocument();
  });

  test('toggles notification rules', () => {
    render(<SlackConfigModal isOpen={true} onClose={jest.fn()} />);

    const summaryCheckbox = screen.getByLabelText(/Daily Summary Notification/i);
    fireEvent.click(summaryCheckbox);
    expect(summaryCheckbox).not.toBeChecked();

    fireEvent.click(summaryCheckbox);
    expect(summaryCheckbox).toBeChecked();
  });

  test('updates summary time when enabled', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        webhook_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXX',
      }),
    });

    render(<SlackConfigModal isOpen={true} onClose={jest.fn()} />);

    await waitFor(() => {
      const timeInput = screen.getByDisplayValue('09:00');
      fireEvent.change(timeInput, { target: { value: '14:00' } });
    });
  });

  test('closes modal on close button click', () => {
    const onClose = jest.fn();
    render(<SlackConfigModal isOpen={true} onClose={onClose} />);

    const cancelButton = screen.getByText(/^Cancel$/);
    fireEvent.click(cancelButton);

    expect(onClose).toHaveBeenCalled();
  });

  test('deletes configuration with confirmation', async () => {
    const mockConfig = {
      webhook_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXX',
    };

    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConfig,
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

    window.confirm = jest.fn(() => true);

    const onClose = jest.fn();
    render(<SlackConfigModal isOpen={true} onClose={onClose} />);

    await waitFor(() => {
      const deleteButton = screen.getByText(/Delete Configuration/i);
      fireEvent.click(deleteButton);
    });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/v1/slack/config',
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });
  });
});
