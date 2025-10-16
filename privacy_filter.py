"""
Privacy Filter Component
Blurs screen after 1 minute of inactivity to protect sensitive data
"""

import streamlit as st
import streamlit.components.v1 as components

def inject_privacy_filter(timeout_seconds=60):
    """
    Inject JavaScript to blur screen after inactivity

    Args:
        timeout_seconds: Number of seconds of inactivity before blurring (default: 60)
    """

    privacy_js = f"""
    <script>
    (function() {{
        let inactivityTimer;
        let privacyOverlay = null;
        const INACTIVITY_TIMEOUT = {timeout_seconds * 1000}; // Convert to milliseconds

        // Create privacy overlay
        function createPrivacyOverlay() {{
            if (privacyOverlay) return privacyOverlay;

            privacyOverlay = document.createElement('div');
            privacyOverlay.id = 'privacy-overlay';
            privacyOverlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(44, 82, 130, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                z-index: 999999;
                display: none;
                align-items: center;
                justify-content: center;
                font-family: 'Inter', sans-serif;
                cursor: pointer;
            `;

            privacyOverlay.innerHTML = `
                <div style="text-align: center; color: white; padding: 2rem;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">🔒</div>
                    <h2 style="font-size: 2rem; font-weight: 600; margin-bottom: 1rem;">
                        Privacy Screen Active
                    </h2>
                    <p style="font-size: 1.2rem; opacity: 0.9; margin-bottom: 2rem;">
                        Screen locked due to inactivity
                    </p>
                    <p style="font-size: 1rem; opacity: 0.7;">
                        Click anywhere or press any key to continue
                    </p>
                </div>
            `;

            document.body.appendChild(privacyOverlay);
            return privacyOverlay;
        }}

        // Show privacy overlay
        function showPrivacyScreen() {{
            const overlay = createPrivacyOverlay();
            overlay.style.display = 'flex';
            console.log('🔒 Privacy screen activated');
        }}

        // Hide privacy overlay
        function hidePrivacyScreen() {{
            if (privacyOverlay) {{
                privacyOverlay.style.display = 'none';
                console.log('🔓 Privacy screen deactivated');
            }}
            resetInactivityTimer();
        }}

        // Reset inactivity timer
        function resetInactivityTimer() {{
            clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(showPrivacyScreen, INACTIVITY_TIMEOUT);
        }}

        // Event listeners for user activity
        const activityEvents = [
            'mousedown',
            'mousemove',
            'keypress',
            'scroll',
            'touchstart',
            'click'
        ];

        // Add event listeners
        activityEvents.forEach(event => {{
            document.addEventListener(event, function(e) {{
                // If privacy screen is active, hide it
                if (privacyOverlay && privacyOverlay.style.display === 'flex') {{
                    hidePrivacyScreen();
                    e.preventDefault();
                    e.stopPropagation();
                }} else {{
                    // Otherwise, just reset timer
                    resetInactivityTimer();
                }}
            }}, true);
        }});

        // Handle keyboard events to unlock
        document.addEventListener('keydown', function(e) {{
            if (privacyOverlay && privacyOverlay.style.display === 'flex') {{
                hidePrivacyScreen();
                e.preventDefault();
                e.stopPropagation();
            }}
        }}, true);

        // Click to unlock
        if (privacyOverlay) {{
            privacyOverlay.addEventListener('click', hidePrivacyScreen);
        }}

        // Start timer
        resetInactivityTimer();

        console.log('🛡️ Privacy filter initialized (timeout: {timeout_seconds}s)');
    }})();
    </script>
    """

    # Inject the JavaScript
    components.html(privacy_js, height=0, width=0)

def show_privacy_indicator(timeout_seconds=60):
    """
    Show a small indicator that privacy filter is active
    """
    st.markdown(f"""
        <div style="
            position: fixed;
            bottom: 10px;
            right: 10px;
            background: rgba(44, 82, 130, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 500;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        ">
            🔒 Privacy Filter Active ({timeout_seconds}s)
        </div>
    """, unsafe_allow_html=True)
