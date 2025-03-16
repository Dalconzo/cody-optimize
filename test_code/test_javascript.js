// A utility function that formats a number as currency
// Supports different currency symbols
function formatCurrency(amount, symbol = '$', decimals = 2) {
    return `${symbol}${amount.toFixed(decimals)}`;
}

/**
 * User class for managing user data
 * Handles authentication and profile information
 */
class User {
    /**
     * Create a new user
     * @param {string} username - The user's username
     * @param {string} email - The user's email address
     */
    constructor(username, email) {
        this.username = username;
        this.email = email;
        this.isLoggedIn = false;
    }
    
    // Log the user in
    login() {
        this.isLoggedIn = true;
        return this;
    }
    
    // Log the user out
    logout() {
        this.isLoggedIn = false;
        return this;
    }
}

// Arrow function with comment
const calculateTax = (amount, rate = 0.1) => {
    // Apply the tax rate to the amount
    return amount * rate;
};
