// assets/autoscroll.js

// safety fallback
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.no_update = window.dash_clientside.no_update || null;

// ENTER key should trigger Send button.
// We attach a keydown listener to the whole document, but
// only fire when focus is in #user-input and key is Enter.
(function () {
    function handleKeydown(e) {
        const isEnter = (e.key === "Enter");
        const inputEl = document.getElementById("user-input");
        const sendBtn = document.getElementById("send-btn");

        if (!inputEl || !sendBtn) return;

        const active = document.activeElement;
        if (active === inputEl && isEnter) {
            // prevent native form submit / newlines
            e.preventDefault();
            // click the Send button programmatically
            sendBtn.click();
        }
    }

    document.addEventListener("keydown", handleKeydown, true);
})();
