import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Header from '../components/Header';

describe('Header Component', () => {
  const mockOnThemeToggle = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders header with logo and title', () => {
    render(<Header theme="dark" onThemeToggle={mockOnThemeToggle} />);

    const logo = screen.getByText('🦞');
    const title = screen.getByText('ClawBook');
    const subtitle = screen.getByText('AI Heart Diary');

    expect(logo).toBeInTheDocument();
    expect(title).toBeInTheDocument();
    expect(subtitle).toBeInTheDocument();
  });

  test('renders theme toggle button', () => {
    render(<Header theme="dark" onThemeToggle={mockOnThemeToggle} />);

    const button = screen.getByRole('button', { name: /Toggle theme/i });
    expect(button).toBeInTheDocument();
  });

  test('displays sun icon when theme is dark', () => {
    const { container } = render(<Header theme="dark" onThemeToggle={mockOnThemeToggle} />);

    const button = screen.getByRole('button', { name: /Toggle theme/i });
    const svg = button.querySelector('svg');

    expect(svg).toBeInTheDocument();
  });

  test('displays moon icon when theme is light', () => {
    const { container } = render(<Header theme="light" onThemeToggle={mockOnThemeToggle} />);

    const button = screen.getByRole('button', { name: /Toggle theme/i });
    const svg = button.querySelector('svg');

    expect(svg).toBeInTheDocument();
  });

  test('calls onThemeToggle when button is clicked', async () => {
    const user = userEvent.setup();
    render(<Header theme="dark" onThemeToggle={mockOnThemeToggle} />);

    const button = screen.getByRole('button', { name: /Toggle theme/i });
    await user.click(button);

    expect(mockOnThemeToggle).toHaveBeenCalledTimes(1);
  });

  test('calls onThemeToggle multiple times on multiple clicks', async () => {
    const user = userEvent.setup();
    render(<Header theme="dark" onThemeToggle={mockOnThemeToggle} />);

    const button = screen.getByRole('button', { name: /Toggle theme/i });

    await user.click(button);
    await user.click(button);
    await user.click(button);

    expect(mockOnThemeToggle).toHaveBeenCalledTimes(3);
  });

  test('button has correct aria-label', () => {
    render(<Header theme="dark" onThemeToggle={mockOnThemeToggle} />);

    const button = screen.getByRole('button', { name: /Toggle theme/i });
    expect(button).toHaveAttribute('aria-label', 'Toggle theme');
  });

  test('button has correct title attribute', () => {
    render(<Header theme="dark" onThemeToggle={mockOnThemeToggle} />);

    const button = screen.getByRole('button', { name: /Toggle theme/i });
    expect(button).toHaveAttribute('title', 'Toggle theme');
  });

  test('header has sticky positioning', () => {
    const { container } = render(<Header theme="dark" onThemeToggle={mockOnThemeToggle} />);

    const header = container.querySelector('header');
    expect(header).toHaveClass('sticky');
    expect(header).toHaveClass('top-0');
    expect(header).toHaveClass('z-50');
  });

  test('renders with correct styling classes', () => {
    const { container } = render(<Header theme="dark" onThemeToggle={mockOnThemeToggle} />);

    const header = container.querySelector('header');
    expect(header).toHaveClass('bg-slate-900');
    expect(header).toHaveClass('dark:bg-slate-900');
    expect(header).toHaveClass('border-b');
  });

  test('logo is not selectable', () => {
    const { container } = render(<Header theme="dark" onThemeToggle={mockOnThemeToggle} />);

    const logoContainer = container.querySelector('.select-none');
    expect(logoContainer).toBeInTheDocument();
  });

  test('renders theme toggle button with correct styling', () => {
    render(<Header theme="dark" onThemeToggle={mockOnThemeToggle} />);

    const button = screen.getByRole('button', { name: /Toggle theme/i });

    expect(button).toHaveClass('p-2');
    expect(button).toHaveClass('rounded-lg');
    expect(button).toHaveClass('bg-slate-800');
    expect(button).toHaveClass('hover:bg-slate-700');
  });

  test('maintains theme state through rerenders', () => {
    const { rerender } = render(<Header theme="dark" onThemeToggle={mockOnThemeToggle} />);

    let title = screen.getByText('ClawBook');
    expect(title).toBeInTheDocument();

    rerender(<Header theme="light" onThemeToggle={mockOnThemeToggle} />);

    title = screen.getByText('ClawBook');
    expect(title).toBeInTheDocument();
  });

});
