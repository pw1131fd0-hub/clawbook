import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ConfidenceIndicator from '../components/ConfidenceIndicator';

describe('ConfidenceIndicator Component', () => {
  test('renders high confidence (>= 0.8)', () => {
    render(
      <ConfidenceIndicator
        confidence={0.85}
        rationale="All factors align well"
      />
    );

    expect(screen.getByText('CONFIDENCE LEVEL')).toBeInTheDocument();
    expect(screen.getByText('High Confidence')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  test('renders medium confidence (0.6 - 0.8)', () => {
    render(
      <ConfidenceIndicator
        confidence={0.7}
        rationale="Some uncertainty remains"
      />
    );

    expect(screen.getByText('Medium Confidence')).toBeInTheDocument();
    expect(screen.getByText('70%')).toBeInTheDocument();
  });

  test('renders low confidence (< 0.6)', () => {
    render(
      <ConfidenceIndicator
        confidence={0.45}
        rationale="Limited data available"
      />
    );

    expect(screen.getByText('Low Confidence')).toBeInTheDocument();
    expect(screen.getByText('45%')).toBeInTheDocument();
  });

  test('displays rationale text', () => {
    const rationale = 'This decision has strong supporting evidence';
    render(<ConfidenceIndicator confidence={0.8} rationale={rationale} />);

    expect(screen.getByText(rationale)).toBeInTheDocument();
  });

  test('handles 100% confidence', () => {
    render(
      <ConfidenceIndicator
        confidence={1.0}
        rationale="Absolutely certain"
      />
    );

    expect(screen.getByText('High Confidence')).toBeInTheDocument();
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  test('handles 0% confidence', () => {
    render(
      <ConfidenceIndicator
        confidence={0}
        rationale="No confidence"
      />
    );

    expect(screen.getByText('Low Confidence')).toBeInTheDocument();
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  test('handles missing rationale', () => {
    const { container } = render(
      <ConfidenceIndicator confidence={0.75} />
    );

    expect(screen.getByText('Medium Confidence')).toBeInTheDocument();
    // Should render without error even without rationale
    expect(container).toBeInTheDocument();
  });

  test('handles default confidence value', () => {
    render(<ConfidenceIndicator />);

    expect(screen.getByText('Low Confidence')).toBeInTheDocument();
    expect(screen.getByText('50%')).toBeInTheDocument();
  });

  test('boundary test: exactly 0.8', () => {
    render(
      <ConfidenceIndicator
        confidence={0.8}
        rationale="Edge case"
      />
    );

    expect(screen.getByText('High Confidence')).toBeInTheDocument();
  });

  test('boundary test: exactly 0.6', () => {
    render(
      <ConfidenceIndicator
        confidence={0.6}
        rationale="Edge case"
      />
    );

    expect(screen.getByText('Medium Confidence')).toBeInTheDocument();
  });

  test('renders confidence level label section', () => {
    render(<ConfidenceIndicator confidence={0.85} />);

    expect(screen.getByText('CONFIDENCE LEVEL')).toBeInTheDocument();
  });

  test('percentage calculation is correct', () => {
    render(
      <ConfidenceIndicator
        confidence={0.337}
        rationale="Test"
      />
    );

    expect(screen.getByText('34%')).toBeInTheDocument();
  });

  test('handles decimal rounding correctly', () => {
    render(
      <ConfidenceIndicator
        confidence={0.567}
        rationale="Test"
      />
    );

    expect(screen.getByText('57%')).toBeInTheDocument();
  });
});
