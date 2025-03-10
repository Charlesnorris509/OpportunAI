# Manual Testing Procedure

## Authentication Flow Testing
- [ ] User can access the login page
- [ ] User can successfully log in with correct credentials
- [ ] User is redirected to dashboard after login
- [ ] User can sign up for a new account
- [ ] "Forgot password" flow works correctly
- [ ] Password reset flow works correctly
- [ ] Incorrect login attempts show appropriate error messages

## Protected Routes Testing
- [ ] Unauthenticated users are redirected to login when trying to access:
  - [ ] Dashboard
  - [ ] Profile
  - [ ] Edit Profile
- [ ] Authenticated users can access all protected routes
- [ ] Logout functionality removes authentication token and redirects to login

## Navigation Testing
- [ ] Navigation buttons in MainLayout work correctly:
  - [ ] Dashboard button navigates to dashboard
  - [ ] Profile button navigates to profile
  - [ ] Logout button logs out the user
- [ ] Browser back/forward navigation works correctly

## Error Handling Testing
- [ ] ErrorBoundary catches JavaScript errors
- [ ] Users are presented with a friendly error message when errors occur
- [ ] Loading states show the spinner component

## Responsiveness Testing
- [ ] Application works on mobile devices (320px - 480px)
- [ ] Application works on tablets (481px - 768px)
- [ ] Application works on laptops (769px - 1024px)
- [ ] Application works on desktops (>1025px)

## Cross-Browser Testing
- [ ] Application functions correctly in Chrome
- [ ] Application functions correctly in Firefox
- [ ] Application functions correctly in Safari
- [ ] Application functions correctly in Edge

## Accessibility Testing
- [ ] Run Lighthouse audit for accessibility score
- [ ] Ensure all interactive elements are keyboard accessible
- [ ] Verify proper focus management
- [ ] Check color contrast for all text elements
- [ ] Ensure all images have appropriate alt text
