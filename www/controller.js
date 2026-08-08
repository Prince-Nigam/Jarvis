/**
 * controller.js — misc helpers for v2 UI
 */
$(document).ready(function () {

    // Legacy compat stubs (main.js now handles these)
    window.DisplayMessage = function (message) {
        if (message) $('#jarvisResponse').text(message);
    };

    // showHood is defined in main.js — keep stub for safety
    if (!window.showHood) {
        window.showHood = function () {
            $('#ActiveView').addClass('hidden');
            $('#IdleView').removeClass('hidden');
        };
    }

    // addLog stub if main.js not loaded yet
    if (!window.addLog) {
        window.addLog = function (msg, cls) {
            var $log = $('#terminalLog');
            $('<div class="log-line ' + (cls||'info') + '">').text('> ' + msg).appendTo($log);
            $log.scrollTop($log[0].scrollHeight);
        };
    }

    // addSenderMsg / addReceiverMsg stubs (main.js defines real ones)
    if (!window.addSenderMsg) {
        window.addSenderMsg = function (message) {
            var $body = $('#chat-canvas-body');
            $('<div class="d-flex justify-content-end mb-2"><div class="sender_message width-size">').text(message).appendTo($body);
            $body.scrollTop($body[0].scrollHeight);
        };
    }
    if (!window.addReceiverMsg) {
        window.addReceiverMsg = function (message) {
            var $body = $('#chat-canvas-body');
            $('<div class="d-flex mb-2"><div class="receiver_message width-size">').text(message).appendTo($body);
            $body.scrollTop($body[0].scrollHeight);
        };
    }

});
