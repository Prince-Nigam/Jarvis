/**
 * main.js — Jarvis UI logic
 * Uses REST API (/api/*) instead of eel.
 */

$(document).ready(function () {

    // ── Siri wave init ────────────────────────────────────────────────────────
    try {
        if (typeof SiriWave !== 'undefined') {
            new SiriWave({
                container: document.getElementById('siri-container'),
                width: 700, height: 180,
                style: 'ios9', amplitude: '1', speed: '0.30', autostart: true
            });
        }
    } catch (e) {}

    // ── Text animations ───────────────────────────────────────────────────────
    try {
        $('.text').textillate({
            loop: true, sync: true,
            in: { effect: 'bounceIn' }, out: { effect: 'bounceOut' }
        });
    } catch (e) {}

    try {
        $('.siri-message').textillate({
            loop: true, sync: true,
            in:  { effect: 'fadeInUp',  sync: true },
            out: { effect: 'fadeOutUp', sync: true }
        });
    } catch (e) {}

    // ── Boot: show WishMessage then run auth ──────────────────────────────────
    var hour = new Date().getHours();
    var greet = hour < 12 ? 'Good Morning' : hour < 17 ? 'Good Afternoon' : 'Good Evening';
    $('#WishMessage').text(greet + ', Initializing...');

    // Give the server 800ms then kick off auth
    setTimeout(function () {
        if (typeof window.runAuthFlow === 'function') window.runAuthFlow();
    }, 800);

    // ── Helpers ───────────────────────────────────────────────────────────────
    function showAssistantText(msg) {
        if (msg) $('.siri-message').text(msg);
    }

    function buildFallbackReply(message) {
        var t = (message || '').toLowerCase();
        if (t.includes('time'))  return 'The current time is ' + new Date().toLocaleTimeString();
        if (t.includes('date'))  return 'Today is ' + new Date().toLocaleDateString();
        if (t.includes('hello') || t.includes('hi')) return 'Hello Sir! How can I help you?';
        return 'You said: "' + message + '". Ready for your next command.';
    }

    // ── Process a command ─────────────────────────────────────────────────────
    function processCommand(text) {
        text = (text || '').trim();
        if (!text) { showAssistantText('Listening...'); return; }

        if (typeof window.addSenderMsg === 'function') window.addSenderMsg(text);
        $('#Oval').hide();
        $('#SiriWave').removeAttr('hidden').show();
        showAssistantText('Working on it...');

        fetch('/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text })
        })
        .then(function (r) { return r.json(); })
        .then(function () {
            // Response comes via speak API — just restore UI after delay
            setTimeout(function () {
                if (typeof window.showHood === 'function') window.showHood();
            }, 3000);
        })
        .catch(function () {
            var reply = buildFallbackReply(text);
            if (typeof window.addReceiverMsg === 'function') window.addReceiverMsg(reply);
            showAssistantText(reply);
            setTimeout(function () {
                if (typeof window.showHood === 'function') window.showHood();
            }, 1500);
        });
    }

    // ── Mic button: listen via API ────────────────────────────────────────────
    $('#MicBtn').click(function () {
        showAssistantText('Listening...');
        $('#Oval').hide();
        $('#SiriWave').removeAttr('hidden').show();

        fetch('/api/listen', { method: 'POST' })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var text = (data.text || '').trim();
                if (text) {
                    processCommand(text);
                } else {
                    showAssistantText("Didn't catch that. Try again.");
                    if (typeof window.showHood === 'function') window.showHood();
                }
            })
            .catch(function () {
                // Mic not available — use text box value
                var val = $('#chatbox').val().trim();
                if (val) processCommand(val);
                else if (typeof window.showHood === 'function') window.showHood();
            });
    });

    // ── Send button / Enter ───────────────────────────────────────────────────
    function PlayAssistant(message) {
        if (!message.trim()) return;
        processCommand(message);
        $('#chatbox').val('');
        $('#MicBtn').show();
        $('#SendBtn').hide();
    }

    function ShowHideButton(val) {
        if (val.length === 0) { $('#MicBtn').show(); $('#SendBtn').hide(); }
        else                  { $('#MicBtn').hide(); $('#SendBtn').show(); }
    }

    $('#chatbox').on('keyup', function () { ShowHideButton($(this).val()); });
    $('#SendBtn').click(function () { PlayAssistant($('#chatbox').val()); });
    $('#chatbox').on('keypress', function (e) {
        if (e.which === 13) PlayAssistant($(this).val());
    });

    // Win + J shortcut
    document.addEventListener('keyup', function (e) {
        if (e.key === 'j' && e.metaKey) processCommand('hello');
    });

});
