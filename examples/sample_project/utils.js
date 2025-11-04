/**
 * Sample JavaScript utilities for testing Code Tokenizer
 */

class StringUtils {
    /**
     * Capitalize the first letter of a string
     * @param {string} str - Input string
     * @returns {string} - Capitalized string
     */
    static capitalize(str) {
        if (!str) return str;
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    /**
     * Reverse a string
     * @param {string} str - Input string
     * @returns {string} - Reversed string
     */
    static reverse(str) {
        return str.split('').reverse().join('');
    }

    /**
     * Check if a string is a palindrome
     * @param {string} str - Input string
     * @returns {boolean} - True if palindrome
     */
    static isPalindrome(str) {
        const cleaned = str.toLowerCase().replace(/[^a-z0-9]/g, '');
        return cleaned === cleaned.split('').reverse().join('');
    }
}

class ArrayUtils {
    /**
     * Remove duplicates from array
     * @param {Array} arr - Input array
     * @returns {Array} - Array with duplicates removed
     */
    static unique(arr) {
        return [...new Set(arr)];
    }

    /**
     * Shuffle array elements
     * @param {Array} arr - Input array
     * @returns {Array} - Shuffled array
     */
    static shuffle(arr) {
        const shuffled = [...arr];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    }

    /**
     * Calculate sum of array elements
     * @param {Array<number>} arr - Array of numbers
     * @returns {number} - Sum of elements
     */
    static sum(arr) {
        return arr.reduce((acc, val) => acc + val, 0);
    }
}

// Example usage
function demonstrateUtils() {
    // String utilities
    const testString = "hello world";
    console.log(`Original: ${testString}`);
    console.log(`Capitalized: ${StringUtils.capitalize(testString)}`);
    console.log(`Reversed: ${StringUtils.reverse(testString)}`);
    console.log(`Is 'racecar' a palindrome: ${StringUtils.isPalindrome('racecar')}`);

    // Array utilities
    const numbers = [1, 2, 3, 4, 5, 1, 2, 3];
    console.log(`Original array: ${numbers}`);
    console.log(`Unique array: ${ArrayUtils.unique(numbers)}`);
    console.log(`Shuffled array: ${ArrayUtils.shuffle(numbers)}`);
    console.log(`Sum: ${ArrayUtils.sum(numbers)}`);
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { StringUtils, ArrayUtils };
}

// Run demonstration if called directly
if (require.main === module) {
    demonstrateUtils();
}