/**
 * QUICK TEST - Messaging Components
 * 
 * Run this in browser console to check if components are present
 */

console.log('=== MESSAGING COMPONENT TEST ===');

// Test 1: Check if MessagingTab component exists in EditorDashboard
const messagingTab = document.querySelector('button[onclick*="messaging"], button');
const allButtons = document.querySelectorAll('button');
console.log(`Total buttons found: ${allButtons.length}`);

// Find messaging button
let messagingButton = null;
allButtons.forEach((btn, index) => {
    if (btn.textContent.includes('Messaging')) {
        console.log(`✓ Found Messaging button at index ${index}:`, btn);
        messagingButton = btn;
    }
});

if (!messagingButton) {
    console.log('✗ Messaging button not found');
    console.log('Available button texts:', Array.from(allButtons).map(b => b.textContent.trim()).filter(t => t.length > 0));
}

// Test 2: Check if UserMessagingFloat component exists
const floatingButton = document.querySelector('.fixed.bottom-6.right-6');
if (floatingButton) {
    console.log('✓ Found floating button:', floatingButton);
} else {
    console.log('✗ Floating button not found');
    // Try to find any fixed bottom-right elements
    const fixedElements = document.querySelectorAll('.fixed');
    console.log(`Found ${fixedElements.length} fixed position elements:`, fixedElements);
}

// Test 3: Check if MessagingTab import is working
const scripts = document.querySelectorAll('script');
console.log(`Total scripts loaded: ${scripts.length}`);

// Test 4: Check current path/dashboard
const path = window.location.pathname;
console.log(`Current path: ${path}`);

// Test 5: Check for React components in window
if (window.React) {
    console.log('✓ React is loaded');
} else {
    console.log('✗ React not found in window');
}

console.log('=== END TEST ===');
console.log('');
console.log('INSTRUCTIONS:');
console.log('1. If you see "✓ Found Messaging button" → Button exists but may not be visible due to styling');
console.log('2. If you see "✗ Messaging button not found" → Component not rendering');
console.log('3. Check "Available button texts" to see what buttons are actually there');
console.log('4. If floating button not found, check current path - should be on UserDashboard');
