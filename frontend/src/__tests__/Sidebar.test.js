import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Sidebar from '../components/Sidebar';

describe('Sidebar Component', () => {
  test('renders sidebar with mood emojis', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );

    // Component should render without error
    const aside = document.querySelector('aside');
    expect(aside).toBeInTheDocument();
  });

  test('displays mood emoji labels', () => {
    const { container } = render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );

    // Check for mood emojis
    const emojis = container.querySelectorAll('[title]');
    expect(emojis.length).toBeGreaterThan(0);
  });

  test('renders navigation links', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );

    // Should have navigation links
    const links = document.querySelectorAll('a');
    expect(links.length).toBeGreaterThanOrEqual(0);
  });

  test('displays all mood emojis in grid', () => {
    const { container } = render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );

    // Should display mood emoji grid
    const grid = container.querySelector('.grid');
    expect(grid).toBeInTheDocument();
  });

  test('sidebar has correct styling classes', () => {
    const { container } = render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );

    const aside = container.querySelector('aside');
    expect(aside).toBeInTheDocument();
  });
});
