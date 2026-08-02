/**
 * main.js — Jarvis UI logic (Flask REST API)
 */
$(document).ready(function () {

    // ── Siri wave init ─────────────────────────────────────────────────────
    var siriWave = null;
    try {
        if (typeof SiriWave !== 'undefined') {
            siriWave = new SiriWave({
                container: document.getElementById('siri-container'),
                width: 700, height: 180,
                style: 'ios9', amplitude: '1', speed: '0.30', autostart: true
            });
        }
    } catch (e) {}

    // ── Text animations (only on WishMessage, not response) ───────────────
    try {
        $('.text').textillate({
            loop: true, sync: true,
            in: { effect: 'bounceIn' }, out: { effect: 'bounceOut' }
        });
    } catch (e) {}

    // NOTE: We do NOT apply textillate to .siri-message because it hides
    // the response text. We set it directly via jQuery .text()

    // ── Greeting ───────────────────────────────────────────────────────────
    var hour  = new Date().getHours();
    var greet = hour < 12 ? 'Good Morning' : hour < 17 ? 'Good Afternoon' : 'Good Evening';
    $('#WishMessage').text(greet + ', Initializing...');

    setTimeout(function () {
        if (typeof window.runAuthFlow === 'function') window.runAuthFlow();
    }, 800);

    // ── Helpers ────────────────────────────────────────────────────────────
    function showAssistantText(msg) {
        if (!msg || !msg.trim()) return;
        // SiriWave section response text
        $('#jarvisResponse').text(msg);
        // Oval (idle) section — shows last response below sphere
        $('#lastResponse').text('↳ ' + msg);
    }

    function buildFallbackReply(message) {
        var t = (message || '').toLowerCase();
        if (t.includes('time'))  return 'The current time is ' + new Date().toLocaleTimeString();
        if (t.includes('date'))  return 'Today is ' + new Date().toLocaleDateString();
        if (t.includes('hello') || t.includes('hi')) return 'Hello Sir! How can I help you?';
        return 'You said: "' + message + '". Ready for your next command.';
    }

    // ── Process command ────────────────────────────────────────────────────
    function processCommand(text) {
        text = (text || '').trim();
        if (!text) {
            showAssistantText('Listening...');
            return;
        }

        if (typeof window.addSenderMsg === 'function') window.addSenderMsg(text);
        if (typeof window.addLog === 'function')       window.addLog('USER > ' + text, 'cmd');

        $('#Oval').attr('hidden', true).hide();
        $('#SiriWave').removeAttr('hidden').show();
        showAssistantText('Working on it...');

        fetch('/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var reply = (data && data.response && data.response.trim())
                ? data.response
                : buildFallbackReply(text);

            showAssistantText(reply);
            if (typeof window.addReceiverMsg === 'function') window.addReceiverMsg(reply);
            if (typeof window.addLog         === 'function') window.addLog('JARVIS > ' + reply, 'success');

            setTimeout(function () {
                if (typeof window.showHood === 'function') window.showHood();
            }, 3500);
        })
        .catch(function () {
            var reply = buildFallbackReply(text);
            showAssistantText(reply);
            if (typeof window.addReceiverMsg === 'function') window.addReceiverMsg(reply);
            setTimeout(function () {
                if (typeof window.showHood === 'function') window.showHood();
            }, 1500);
        });
    }

    // ── Mic button ─────────────────────────────────────────────────────────
    $('#MicBtn').on('click', function () {
        showAssistantText('Listening...');
        $('#Oval').attr('hidden', true).hide();
        $('#SiriWave').removeAttr('hidden').show();
        if (typeof window.addLog === 'function') window.addLog('Mic activated', 'info');

        // Show a listening timeout indicator
        var listenTimer = setTimeout(function () {
            showAssistantText("Still listening...");
        }, 4000);

        fetch('/api/listen', { method: 'POST' })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                clearTimeout(listenTimer);
                var text = (data.text || '').trim();
                if (text) {
                    processCommand(text);
                } else {
                    showAssistantText("Didn't catch that. Try again.");
                    if (typeof window.addLog === 'function') window.addLog('No speech detected', 'warn');
                    setTimeout(function () {
                        if (typeof window.showHood === 'function') window.showHood();
                    }, 1500);
                }
            })
            .catch(function () {
                clearTimeout(listenTimer);
                var val = $('#chatbox').val().trim();
                if (val) {
                    processCommand(val);
                } else {
                    showAssistantText('Microphone not available.');
                    setTimeout(function () {
                        if (typeof window.showHood === 'function') window.showHood();
                    }, 1500);
                }
            });
    });

    // ── Send / Enter ───────────────────────────────────────────────────────
    function PlayAssistant(message) {
        if (!message.trim()) return;
        processCommand(message);
        $('#chatbox').val('');
        $('#MicBtn').attr('hidden', false);
        $('#SendBtn').attr('hidden', true);
    }

    function ShowHideButton(val) {
        if (val.length === 0) {
            $('#MicBtn').attr('hidden', false);
            $('#SendBtn').attr('hidden', true);
        } else {
            $('#MicBtn').attr('hidden', true);
            $('#SendBtn').attr('hidden', false);
        }
    }

    $('#chatbox').on('keyup', function () { ShowHideButton($(this).val()); });
    $('#SendBtn').on('click', function () { PlayAssistant($('#chatbox').val()); });
    $('#chatbox').on('keypress', function (e) {
        if (e.which === 13) PlayAssistant($(this).val());
    });

    // Windows keyboard shortcut: Ctrl+Alt+J  (metaKey = Mac Command, not Windows)
    document.addEventListener('keydown', function (e) {
        if (e.ctrlKey && e.altKey && e.key.toLowerCase() === 'j') {
            e.preventDefault();
            processCommand('hello');
        }
    });

    // Expose processCommand globally for hotword post-wake API call
    window.processCommand = processCommand;

});
