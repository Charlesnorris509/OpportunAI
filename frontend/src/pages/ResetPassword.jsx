import React, { useState } from 'react';
import './ResetPassword.css';

const ResetPassword = () => {
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();

        if (newPassword === confirmPassword) {
            setMessage('Your password has been successfully reset!');
        } else {
            setMessage('Passwords do not match. Please try again.');
        }
    };

    return (
        <div className="reset-password-container">
            <h1>Reset Password</h1>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="new-password">New Password:</label>
                    <input
                        type="password"
                        id="new-password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="confirm-password">Confirm Password:</label>
                    <input
                        type="password"
                        id="confirm-password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Reset Password</button>
            </form>
            {message && <p className="message">{message}</p>}
        </div>
    );
};

export default ResetPassword;
