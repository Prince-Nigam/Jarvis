/**
 * rightpanel.js
 * - Terminal activity log
 * - Quick command buttons
 * - Live clock in status bar
 * NOTE: No fetch monkey-patching — main.js calls addLog() directly.
 */

(function () {
    'use strict';

    var logEl    = document.getElementById('terminalLog');
    var clockEl  = document.getElementById('clockDisplay');
    var MAX_LINES = 120;

    // ── Clock ─────────────────────────────────────────────────────────────
    function updateClock() {
        if (!clockEl) return;
        var now = new Date();
        var h = String(now.getHours()).padStart(2,'0');
        var m = String(now.getMinutes()).padStart(2,'0');
        var s = String(now.getSeconds()).padStart(2,'0');
        clockEl.textContent = h + ':' + m + ':' + s;
    }
    setInterval(updateClock, 1000);
    updateClock();

    // ── Log helper ─────────────────────────────────────────────────────────
    function ts() {
        var n = new Date();
        return '[' +
            String(n.getHours()).padStart(2,'0')   + ':' +
            String(n.getMinutes()).padStart(2,'0') + ':' +
            String(n.getSeconds()).padStart(2,'0') + ']';
    }

    function addLog(text, type) {
        if (!logEl) return;
        type = type || 'info';

        // Remove old cursor
        var oldCursor = logEl.querySelector('.log-cursor');
        if (oldCursor) oldCursor.parentElement.removeChild(oldCursor);

        var line = document.createElement('div');
        line.className = 'log-line ' + type;
        line.textContent = ts() + ' ' + text;
        logEl.appendChild(line);

        // Blinking cursor on last line
        var cursor = document.createElement('span');
        cursor.className = 'log-cursor';
        line.appendChild(cursor);

        // Trim old lines
        var lines = logEl.querySelectorAll('.log-line');
        if (lines.length > MAX_LINES) {
            lines[0].parentElement.removeChild(lines[0]);
        }

        logEl.scrollTop = logEl.scrollHeight;
    }

    // Expose globally — main.js and other files call window.addLog()
    window.addLog = addLog;

    // ── Boot sequence ──────────────────────────────────────────────────────
    var bootLines = [
        ['JARVIS v3.0 — INITIALIZING...', 'dim'],
        ['Loading neural interface...', 'dim'],
        ['Connecting to system bus...', 'dim'],
        ['psutil.sensors OK', 'success'],
        ['Flask server: ONLINE', 'success'],
        ['Database: jarvis.db LOADED', 'success'],
        ['Face auth module: READY', 'info'],
        ['Speech engine: STANDBY', 'info'],
        ['File system access: GRANTED', 'success'],
        ['All systems nominal.', 'success'],
        ['Awaiting authentication...', 'warn'],
    ];

    var bi = 0;
    function runBootLog() {
        if (bi >= bootLines.length) return;
        var entry = bootLines[bi++];
        addLog(entry[0], entry[1]);
        if (bi < bootLines.length) {
            setTimeout(runBootLog, 150 + Math.random() * 250);
        }
    }

    // ── Ambient log — true variable delays via recursive setTimeout ────────
    var ambientPool = [
        ['Scanning memory pages...', 'dim'],
        ['CPU thermal check OK', 'success'],
        ['Network heartbeat sent', 'dim'],
        ['Cache flush complete', 'dim'],
        ['Voice buffer cleared', 'dim'],
        ['Entropy pool refilled', 'dim'],
        ['Packet inspection idle', 'dim'],
        ['Socket keepalive OK', 'success'],
        ['ASLR bypass check: CLEAR', 'success'],
        ['Kernel tick: nominal', 'dim'],
        ['GPIO poll: no signal', 'dim'],
        ['DNS cache: 12 entries', 'dim'],
        ['Firewall rules: active', 'success'],
        ['Idle process monitor ON', 'dim'],
    ];

    function scheduleAmbient() {
        var delay = 3000 + Math.random() * 4000;   // 3-7s, different every time
        setTimeout(function () {
            var entry = ambientPool[Math.floor(Math.random() * ambientPool.length)];
            addLog(entry[0], entry[1]);
            scheduleAmbient();   // schedule next with a new random delay
        }, delay);
    }

    // ── Quick command buttons ──────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        // Start boot log
        setTimeout(runBootLog, 400);

        // Start ambient log after boot finishes
        setTimeout(scheduleAmbient, bootLines.length * 400 + 1500);

        // Quick command buttons — use main.js processCommand if available
        var btns = document.querySelectorAll('.quick-btn');
        btns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var cmd = btn.getAttribute('data-cmd');
                if (!cmd) return;
                addLog('CMD> ' + cmd.toUpperCase(), 'cmd');

                if (typeof window.processCommand === 'function') {
                    // Use the full UI flow (shows SiriWave, updates panels)
                    window.processCommand(cmd);
                } else {
                    // Fallback: direct API call
                    fetch('/api/command', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: cmd })
                    })
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        var reply = (data && data.response) ? data.response : 'Done';
                        addLog('JARVIS > ' + reply, 'success');
                    })
                    .catch(function () {
                        addLog('ERR: command failed', 'error');
                    });
                }
            });
        });
    });

}());
