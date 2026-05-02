/**
 * ELITE SECURITY CONFIGURATION
 * ----------------------------
 * This module strictly relies on HttpOnly cookies.
 * Tokens are NOT stored in JS-accessible memory to prevent XSS theft.
 */

const Auth = {
    // Session state
    user: null,

    async checkSession() {
        try {
            const resp = await fetch('/api/auth/me');
            if (resp.ok) {
                this.user = await resp.json();
                localStorage.setItem('procurement_user_session', 'active');
                return this.user;
            }
        } catch (e) {
            console.warn("Session check failed (might be logged out)");
        }
        this.user = null;
        localStorage.removeItem('procurement_user_session');
        return null;
    },

    async logout() {
        console.log("Professional Logout Initialized...");
        try {
            await fetch('/api/auth/logout', { method: 'POST' });
        } catch (e) {
            console.error("Server logout failed", e);
        }
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = '/?logged_out=true';
    },

    // Legacy support for UI components that check sync
    isAuthenticatedSync() {
        return localStorage.getItem('procurement_user_session') === 'active';
    }
};

window.Auth = Auth;
