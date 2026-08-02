$(document).ready(function () {

    // Display Speak Message
    window.DisplayMessage = function (message) {
        $(".siri-message li:first").text(message);
        try { $('.siri-message').textillate('start'); } catch(e) {}
    };

    // Show Oval hood — hide siri wave
    window.showHood = function () {
        $("#Oval").attr("hidden", false).show();
        $("#SiriWave").attr("hidden", true).hide();
    };

    // Chat: sender message
    window.addSenderMsg = function (message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (!message || !message.trim()) return;
        chatBox.innerHTML += `<div class="row justify-content-end mb-4">
            <div class="width-size"><div class="sender_message">${message}</div></div>
        </div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // Chat: receiver message
    window.addReceiverMsg = function (message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (!message || !message.trim()) return;
        chatBox.innerHTML += `<div class="row justify-content-start mb-4">
            <div class="width-size"><div class="receiver_message">${message}</div></div>
        </div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // Auth flow → then show Dashboard
    window.runAuthFlow = function () {
        fetch('/api/auth', { method: 'POST' })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                // Check if face auth was successful
                if (data && data.authenticated) {
                    // Authenticated — show full boot animation
                    $("#Loader").attr("hidden", true);
                    $("#FaceAuth").attr("hidden", false);
                    setTimeout(function () {
                        $("#FaceAuth").attr("hidden", true);
                        $("#FaceAuthSuccess").attr("hidden", false);
                        setTimeout(function () {
                            $("#FaceAuthSuccess").attr("hidden", true);
                            $("#HelloGreet").attr("hidden", false);
                            setTimeout(_showDashboard, 2000);
                        }, 2000);
                    }, 2000);
                } else {
                    // Not authenticated or trainer not ready — skip animations, go straight to dashboard
                    _showDashboard();
                }
            })
            .catch(function () {
                // Auth API unavailable — skip straight to dashboard
                _showDashboard();
            });
    };

    function _showDashboard() {
        $("#BootScreen").fadeOut(600, function () {
            $("#Dashboard").removeAttr("hidden").hide().fadeIn(500, function () {
                if (typeof window.startSysStatPolling === 'function') {
                    window.startSysStatPolling();
                }
                // Greet on dashboard load
                fetch('/api/greet', { method: 'POST' })
                    .then(function (r) { return r.json(); })
                    .then(function (res) {
                        if (res && res.message) {
                            // Show greeting in the response bar
                            var lr = document.getElementById('lastResponse');
                            if (lr) lr.textContent = '↳ ' + res.message;
                            var jr = document.getElementById('jarvisResponse');
                            if (jr) jr.textContent = res.message;
                        }
                    })
                    .catch(function () {});

            });
            if (typeof window.initFileBrowser === 'function') {
                window.initFileBrowser();
            }
            if (typeof window.addLog === 'function') {
                window.addLog('Dashboard loaded', 'success');
            }
        });
    }

});
