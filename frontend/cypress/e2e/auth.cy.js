describe('Authentication Flows', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    cy.clearLocalStorage();
  });

  it('should redirect unauthenticated users from protected routes to login', () => {
    cy.visit('/dashboard');
    cy.url().should('include', '/');
  });

  it('should allow login with valid credentials', () => {
    // Mock the login API response
    cy.intercept('POST', '**/login', {
      statusCode: 200,
      body: { token: 'fake-token' },
    }).as('loginRequest');

    cy.visit('/');
    
    // Fill in login form (adjust selectors as needed)
    cy.get('[data-testid="email-input"]').type('user@example.com');
    cy.get('[data-testid="password-input"]').type('password123');
    cy.get('[data-testid="login-button"]').click();
    
    cy.wait('@loginRequest');
    
    // Should redirect to dashboard
    cy.url().should('include', '/dashboard');
  });

  it('should show error message with invalid credentials', () => {
    // Mock failed login
    cy.intercept('POST', '**/login', {
      statusCode: 401,
      body: { error: 'Invalid credentials' },
    }).as('failedLogin');

    cy.visit('/');
    
    // Fill in login form with invalid credentials
    cy.get('[data-testid="email-input"]').type('wrong@example.com');
    cy.get('[data-testid="password-input"]').type('wrongpassword');
    cy.get('[data-testid="login-button"]').click();
    
    cy.wait('@failedLogin');
    
    // Should show error message
    cy.get('[data-testid="error-message"]').should('be.visible');
  });
});
