import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import MainLayout from './MainLayout';

// Wrap the component in BrowserRouter for testing
const MockMainLayout = ({ children }) => (
  <BrowserRouter>
    <MainLayout>{children}</MainLayout>
  </BrowserRouter>
);

describe('MainLayout Component', () => {
  test('renders navigation buttons', () => {
    render(<MockMainLayout>Test Content</MockMainLayout>);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });

  test('renders children content', () => {
    render(<MockMainLayout>Test Content</MockMainLayout>);
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });
});
