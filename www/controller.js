/**
 * controller.js
 * Handles auth flow, dashboard transitions, and chat message rendering.
 * Uses REST API instead of eel.
 */

$(document).ready(function () {

    // ── Auth flow (called from main.js on page load) ──────────────────────────
    window.runAuthFlow = function () {
        // Step 1: hide loader, show face auth animation
        $("#Loader").hide();
        $("#FaceAuth").removeAttr("hidden").show();

        // Step 2: call auth API
        fetch('/api/auth', { method: 'POST' })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.authenticated) {
                    if (window.addLog) window.addLog('Face auth: AUTHENTICATED', 'success');
                    // Show success animation
                    $("#FaceAuth").hide();
                    $("#FaceAuthSuccess").removeAttr("hidden").show();

                    setTimeout(function () {
                        $("#FaceAuthSuccess").hide();
                        $("#HelloGreet").removeAttr("hidden").show();

                        setTimeout(function () {
                            launchDashboard();
                        }, 1800);
                    }, 1500);
                } else {
                    $("#WishMessage").text("Face Authentication Failed. Try again.");
                    setTimeout(window.runAuthFlow, 2000);
                }
            })
            .catch(function () {
                // Auth API not available — skip auth, go straight to dashboard
                if (window.addLog) window.addLog('Auth API unavailable — bypass', 'warn');
                launchDashboard();
            });
    };

    function launchDashboard() {
        $("#BootScreen").fadeOut(600, function () {
            $("#Dashboard").removeAttr("hidden").hide().fadeIn(400);
            setTimeout(function () {
                if (typeof window.initFileBrowser === 'function') window.initFileBrowser();
                if (typeof window.refreshSysStats  === 'function') window.refreshSysStats();
                $("#Oval").addClass("animate__animated animate__zoomIn");
            }, 300);
        });
    }

    // ── Chat helpers (called by main.js) ─────────────────────────────────────
    window.addSenderMsg = function (message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (!chatBox || !message.trim()) return;
        chatBox.innerHTML +=
            '<div class="row justify-content-end mb-4">' +
            '<div class="width-size"><div class="sender_message">' + message + '</div></div>' +
            '</div>';
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    window.addReceiverMsg = function (message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (!chatBox || !message.trim()) return;
        chatBox.innerHTML +=
            '<div class="row justify-content-start mb-4">' +
            '<div class="width-size"><div class="receiver_message">' + message + '</div></div>' +
            '</div>';
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    window.showHood = function () {
        $("#Oval").show();
        $("#SiriWave").hide();
    };

});
