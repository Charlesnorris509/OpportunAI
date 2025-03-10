import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

// Mock the lazy-loaded components
jest.mock('./pages/Login', () => () => <div>Login Page</div>);
jest.mock('./pages/Signup', () => () => <div>Signup Page</div>);
jest.mock('./pages/DashboardPage', () => () => <div>Dashboard Page</div>);
jest.mock('./pages/ProfilePage', () => () => <div>Profile Page</div>);
jest.mock('./pages/ForgotPassword', () => () => <div>Forgot Password Page</div>);
jest.mock('./pages/ResetPassword', () => () => <div>Reset Password Page</div>);
jest.mock('./components/Profile/EditProfile', () => () => <div>Edit Profile Page</div>);

// Mock the suspense fallback
jest.mock('./components/common/LoadingSpinner', () => () => <div>Loading...</div>);

describe('App Component', () => {
  test('renders login page on root path', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );
    
    // Wait for lazy loaded component
    expect(await screen.findByText('Login Page')).toBeInTheDocument();
  });

  test('redirects to login when accessing protected route without auth', async () => {
    // Mock localStorage to return null for token
    localStorage.getItem.mockReturnValue(null);
    
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App />
      </MemoryRouter>
    );
    
    // Should redirect to login
    expect(await screen.findByText('Login Page')).toBeInTheDocument();
  });

  test('shows dashboard when authenticated', async () => {
    // Mock localStorage to return a token
    localStorage.getItem.mockReturnValue('fake-token');
    
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App />
      </MemoryRouter>
    );
    
    // Should show dashboard inside layout
    expect(await screen.findByText('Dashboard Page')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument(); // From MainLayout
  });
});
