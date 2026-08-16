/**
 * main.js — Jarvis UI logic (Flask REST API) — v2 redesign
 */
$(document).ready(function () {

    // ── Real SiriWave init ─────────────────────────────────────────────────
    var siriWave = null;
    var audioCtx = null;
    var analyser = null;
    var micStream = null;
    var waveAnimId = null;

    function initSiriWave() {
        if (siriWave) return;
        try {
            siriWave = new SiriWave({
                container: document.getElementById('siri-container'),
                width: 500,
                height: 120,
                style: 'ios9',
                amplitude: 0.1,
                speed: 0.08,
                autostart: true,
                color: '#00d4ff'
            });
        } catch(e) {
            console.warn('SiriWave init failed:', e);
        }
    }

    function startMicWave() {
        if (!siriWave) return;
        try {
            navigator.mediaDevices.getUserMedia({ audio: true, video: false })
            .then(function(stream) {
                micStream = stream;
                audioCtx  = new (window.AudioContext || window.webkitAudioContext)();
                analyser  = audioCtx.createAnalyser();
                analyser.fftSize = 256;
                var src = audioCtx.createMediaStreamSource(stream);
                src.connect(analyser);
                var dataArr = new Uint8Array(analyser.frequencyBinCount);
                function animateWave() {
                    analyser.getByteFrequencyData(dataArr);
                    var sum = 0;
                    for (var i = 0; i < dataArr.length; i++) sum += dataArr[i];
                    var avg = sum / dataArr.length;
                    var amp = Math.min(2, (avg / 255) * 4);
                    if (siriWave) siriWave.setAmplitude(amp);
                    waveAnimId = requestAnimationFrame(animateWave);
                }
                animateWave();
            })
            .catch(function() {
                if (siriWave) siriWave.setAmplitude(1);
            });
        } catch(e) {
            if (siriWave) siriWave.setAmplitude(1);
        }
    }

    function stopMicWave() {
        if (waveAnimId) { cancelAnimationFrame(waveAnimId); waveAnimId = null; }
        if (micStream)  { micStream.getTracks().forEach(function(t){ t.stop(); }); micStream = null; }
        if (audioCtx)   { audioCtx.close(); audioCtx = null; analyser = null; }
        if (siriWave)   siriWave.setAmplitude(0.05);
    }

    // ── Boot sequence ──────────────────────────────────────────────────────
    var bootMessages = [
        'LOADING NEURAL CORE...',
        'INITIALIZING VOICE SYSTEMS...',
        'CALIBRATING SENSORS...',
        'ESTABLISHING CONNECTION...',
        'RUNNING DIAGNOSTICS...',
        'ALL SYSTEMS NOMINAL...',
        'J.A.R.V.I.S READY'
    ];
    var bootIdx = 0;
    var bootPct = 0;
    var bootInterval = setInterval(function () {
        bootPct = Math.min(bootPct + Math.random() * 18 + 8, 100);
        $('#bootBar').css('width', bootPct + '%');
        if (bootIdx < bootMessages.length) {
            $('#bootStatus').text(bootMessages[bootIdx++]);
        }
        if (bootPct >= 100) {
            clearInterval(bootInterval);
            $('#bootStatus').text('J.A.R.V.I.S READY');
            setTimeout(function () {
                $.post('/api/greet').always(function () {});
                $('#BootScreen').fadeOut(800, function () {
                    $('#Dashboard').removeClass('hidden').hide().fadeIn(600);
                    startClock();
                    if (typeof window.startSysStats === 'function') window.startSysStats();
                    if (typeof window.initFileBrowser === 'function') window.initFileBrowser();
                    if (typeof window.initRightPanel === 'function') window.initRightPanel();
                    addLog('JARVIS ONLINE', 'success');
                    addLog('Say "wakeup jarvish" to activate', 'dim');
                    // Auto-start phone listener on mobile
                    if (/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)) {
                        addLog('📱 Mobile detected — tap 🎤 button to enable voice', 'info');
                    }
                });
            }, 600);
        }
    }, 280);

    // ── Clock ──────────────────────────────────────────────────────────────
    function startClock() {
        function tick() {
            var now = new Date();
            var h = String(now.getHours()).padStart(2,'0');
            var m = String(now.getMinutes()).padStart(2,'0');
            var s = String(now.getSeconds()).padStart(2,'0');
            $('#hdrTime').text(h + ':' + m + ':' + s);
            var days = ['SUN','MON','TUE','WED','THU','FRI','SAT'];
            var months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];
            $('#hdrDate').text(days[now.getDay()] + ' ' + now.getDate() + ' ' + months[now.getMonth()] + ' ' + now.getFullYear());
        }
        tick(); setInterval(tick, 1000);
    }

    // ── Helpers ────────────────────────────────────────────────────────────
    function showIdle() {
        $('#ActiveView').addClass('hidden');
        $('#IdleView').removeClass('hidden');
        $('#statusPill .status-dot').css('background','var(--blue)');
        $('#statusText').text('STANDBY');
        stopMicWave();
    }
    function showActive(msg) {
        initSiriWave();
        $('#IdleView').addClass('hidden');
        $('#ActiveView').removeClass('hidden');
        if (msg) { $('#jarvisResponse').text(msg); }
        $('#statusPill .status-dot').css({'background':'var(--cyan)','box-shadow':'0 0 8px var(--cyan)'});
        $('#statusText').text('ACTIVE');
    }

    window.showHood = showIdle;

    function showAssistantText(msg) {
        if (!msg || !msg.trim()) return;
        $('#jarvisResponse').text(msg);
        $('#lastResponse').text('↳ ' + msg);
    }

    window.addLog = function(msg, cls) {
        var $log = $('#terminalLog');
        var $line = $('<div class="log-line ' + (cls||'info') + '">').text('> ' + msg);
        $log.append($line);
        $log.scrollTop($log[0].scrollHeight);
        var lines = $log.children();
        if (lines.length > 80) lines.first().remove();
    };

    function addCmdHistory(msg, mine) {
        var $h = $('#cmdHistory');
        $('<div class="ch-item' + (mine ? ' mine' : '') + '">').text(mine ? '▶ ' + msg : '◀ ' + msg).prependTo($h);
        var items = $h.children();
        if (items.length > 10) items.last().remove();
    }

    window.addReceiverMsg = function(msg) {
        addCmdHistory(msg, false);
        var $body = $('#chat-canvas-body');
        $('<div class="d-flex mb-2"><div class="receiver_message width-size">').text(msg).appendTo($body);
        $body.scrollTop($body[0].scrollHeight);
    };
    window.addSenderMsg = function(msg) {
        addCmdHistory(msg, true);
        var $body = $('#chat-canvas-body');
        $('<div class="d-flex justify-content-end mb-2"><div class="sender_message width-size">').text(msg).appendTo($body);
        $body.scrollTop($body[0].scrollHeight);
    };

    function buildFallbackReply(message) {
        var t = (message || '').toLowerCase();
        if (t.includes('time'))  return 'The current time is ' + new Date().toLocaleTimeString();
        if (t.includes('date'))  return 'Today is ' + new Date().toLocaleDateString();
        if (t.includes('hello') || t.includes('hi')) return 'Hello Sir! How can I help you?';
        return 'Command processed: "' + message + '"';
    }

    // ── Process command (PC pe execute karo) ──────────────────────────────
    function processCommand(text) {
        text = (text || '').trim();
        if (!text) { showActive('Listening...'); return; }

        window.addSenderMsg(text);
        window.addLog('USER > ' + text, 'cmd');
        showActive('Processing...');

        fetch('/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var reply = (data && data.response && data.response.trim())
                ? data.response : buildFallbackReply(text);
            showAssistantText(reply);
            window.addReceiverMsg(reply);
            setTimeout(showIdle, 4000);
        })
        .catch(function () {
            var reply = buildFallbackReply(text);
            showAssistantText(reply);
            window.addReceiverMsg(reply);
            setTimeout(showIdle, 2000);
        });
    }

    window.processCommand = processCommand;

    // ── Quick buttons ──────────────────────────────────────────────────────
    $(document).on('click', '.qbtn', function () {
        processCommand($(this).data('cmd'));
    });

    // ── Desktop Mic button (PC mic → Flask /api/listen) ───────────────────
    $('#MicBtn').on('click', function () {
        // Agar phone voice listener chal raha hai to phone ka use karo
        if (_phoneListening) {
            window.addLog('📱 Phone voice is active — use voice or tap PhoneWakeBtn', 'info');
            return;
        }
        $(this).addClass('listening');
        initSiriWave();
        showActive('Listening...');
        $('#waveStatus').text('LISTENING');
        startMicWave();
        window.addLog('Mic activated', 'info');

        fetch('/api/listen', { method: 'POST' })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                $('#MicBtn').removeClass('listening');
                stopMicWave();
                var text = (data.text || '').trim();
                if (text) {
                    $('#waveStatus').text('PROCESSING');
                    processCommand(text);
                } else {
                    showAssistantText("Didn't catch that. Try again.");
                    window.addLog('No speech detected', 'warn');
                    setTimeout(showIdle, 2000);
                }
            })
            .catch(function () {
                $('#MicBtn').removeClass('listening');
                stopMicWave();
                var val = $('#chatbox').val().trim();
                if (val) processCommand(val);
                else { showAssistantText('Microphone unavailable.'); setTimeout(showIdle, 1500); }
            });
    });

    // ── Text input ─────────────────────────────────────────────────────────
    function showHideBtn(val) {
        if (val.length === 0) { $('#MicBtn').show(); $('#SendBtn').hide(); }
        else                  { $('#MicBtn').hide(); $('#SendBtn').show(); }
    }
    function sendText() {
        var msg = $('#chatbox').val().trim();
        if (!msg) return;
        processCommand(msg);
        $('#chatbox').val('');
        showHideBtn('');
    }
    $('#chatbox').on('keyup', function () { showHideBtn($(this).val()); });
    $('#chatbox').on('keypress', function (e) { if (e.which === 13) sendText(); });
    $('#SendBtn').on('click', sendText);

    // ── Activity Log polling ───────────────────────────────────────────────
    var _lastEventId = 0;
    function pollEvents() {
        fetch('/api/events?after=' + _lastEventId)
            .then(function(r){ return r.json(); })
            .then(function(data){
                if (data && data.events && data.events.length) {
                    data.events.forEach(function(ev){
                        window.addLog(ev.msg, ev.level || 'info');
                        if (_lastEventId < ev.id) _lastEventId = ev.id;
                    });
                }
            })
            .catch(function(){});
    }
    setTimeout(function(){
        pollEvents();
        setInterval(pollEvents, 1500);
    }, 2000);

    // ══════════════════════════════════════════════════════════════════════
    //  PHONE WAKE WORD + COMMAND SYSTEM
    //  Web Speech API — phone browser mein continuous listening
    //  "Jarvish" bolo → PC activate → command execute
    // ══════════════════════════════════════════════════════════════════════

    var _phoneListening    = false;
    var _phoneActive       = false;   // command mode
    var _phoneSR           = null;
    var _phoneRestartTimer = null;

    var _wakeWords = [
        'jarvish','jarvis','jarwish','jervish','jurvish','garvish',
        'hey jarvish','hey jarvis','ok jarvish','ok jarvis',
        'okay jarvish','okay jarvis','wakeup jarvish','wake up jarvis'
    ];
    var _sleepWords = ['shutdown','bye','goodbye','so jao','band karo'];

    function _containsWake(t) {
        t = t.toLowerCase().trim();
        return _wakeWords.some(function(w){ return t.indexOf(w) !== -1; });
    }
    function _containsSleep(t) {
        t = t.toLowerCase().trim();
        return _sleepWords.some(function(w){ return t.indexOf(w) !== -1; });
    }
    function _stripWake(t) {
        t = t.toLowerCase().trim();
        _wakeWords.forEach(function(w){
            t = t.replace(new RegExp(w.replace(/[-\/\\^$*+?.()|[\]{}]/g,'\\$&'), 'g'), '').trim();
        });
        return t.trim();
    }

    // ── Phone UI helpers ───────────────────────────────────────────────────
    function phoneSetStatus(state, msg) {
        var $btn = $('#PhoneWakeBtn');
        var $lbl = $('#phoneWakeLabel');
        if (state === 'off') {
            $btn.attr('title','Start phone voice').html('🎤').css({'background':'','box-shadow':''});
            if ($lbl.length) $lbl.text('Tap to enable phone voice');
        } else if (state === 'listening') {
            $btn.attr('title','Listening — say Jarvish').html('👂').css({
                'background':'rgba(0,212,255,0.15)',
                'box-shadow':'0 0 12px var(--cyan)'
            });
            if ($lbl.length) $lbl.text('Listening for "Jarvish"...');
            window.addLog('📱 Waiting for wake word "Jarvish"...', 'dim');
        } else if (state === 'active') {
            $btn.html('🔊').css({
                'background':'rgba(255,215,0,0.15)',
                'box-shadow':'0 0 12px #ffd700'
            });
            if ($lbl.length) $lbl.text(msg || 'Say your command...');
        }
    }

    // ── Send command to PC ─────────────────────────────────────────────────
    function phoneSendCommand(text) {
        text = text.trim();
        if (!text) return;
        window.addLog('📱 ' + text, 'cmd');
        window.addSenderMsg(text);
        showActive('📱 ' + text);

        fetch('/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text })
        })
        .then(function(r){ return r.json(); })
        .then(function(data){
            var reply = (data && data.response) ? data.response : 'Done Sir';
            showAssistantText(reply);
            window.addReceiverMsg(reply);
            phoneSetStatus('listening');
            setTimeout(showIdle, 3500);
        })
        .catch(function(){
            phoneSetStatus('listening');
            setTimeout(showIdle, 2000);
        });
    }

    // ── Web Speech API loop ────────────────────────────────────────────────
    function startPhoneListener() {
        var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) {
            window.addLog('⚠️ Voice recognition not supported. Use Chrome on Android.', 'warn');
            alert('Please use Chrome browser on Android for voice support.');
            return;
        }

        _phoneListening = true;
        phoneSetStatus('listening');

        function makeSR() {
            var sr = new SR();
            sr.lang           = 'en-IN';
            sr.continuous     = false;    // one phrase at a time — stable on mobile
            sr.interimResults = false;
            sr.maxAlternatives = 3;

            sr.onresult = function(e) {
                var best = '';
                for (var i = e.resultIndex; i < e.results.length; i++) {
                    // Pick highest confidence alternative
                    for (var j = 0; j < e.results[i].length; j++) {
                        if (!best || e.results[i][j].confidence > e.results[i][0].confidence) {
                            best = e.results[i][j].transcript;
                        }
                    }
                }
                best = best.trim();
                if (!best) return;
                console.log('[PhoneSR] heard:', best, '| active:', _phoneActive);

                if (!_phoneActive) {
                    // ── WAKE WORD MODE ────────────────────────────────────
                    if (_containsWake(best)) {
                        var cmd = _stripWake(best);
                        if (cmd && cmd.length > 2) {
                            // Combined "Jarvish open chrome" — execute directly
                            window.addLog('📱 Wake + Command: ' + cmd, 'success');
                            phoneSetStatus('active', 'Executing...');
                            fetch('/api/activate', { method: 'POST' });
                            phoneSendCommand(cmd);
                        } else {
                            // Just wake word — switch to command mode
                            _phoneActive = true;
                            window.addLog('📱 Wake word heard! Say your command...', 'success');
                            phoneSetStatus('active', 'Say your command Sir...');
                            fetch('/api/activate', { method: 'POST' });
                        }
                    }
                    // else: not wake word, ignore
                } else {
                    // ── COMMAND MODE ──────────────────────────────────────
                    _phoneActive = false;
                    if (_containsSleep(best)) {
                        window.addLog('📱 Sleep received', 'dim');
                        phoneSetStatus('listening');
                    } else {
                        phoneSendCommand(best);
                    }
                }
            };

            sr.onerror = function(e) {
                if (e.error !== 'no-speech' && e.error !== 'aborted') {
                    window.addLog('📱 Mic: ' + e.error, 'warn');
                }
            };

            sr.onend = function() {
                if (_phoneListening) {
                    clearTimeout(_phoneRestartTimer);
                    _phoneRestartTimer = setTimeout(function() {
                        if (_phoneListening) {
                            _phoneSR = makeSR();
                            try { _phoneSR.start(); } catch(ex) {
                                window.addLog('📱 Restart error: ' + ex.message, 'warn');
                            }
                        }
                    }, 250);
                }
            };

            return sr;
        }

        _phoneSR = makeSR();
        try {
            _phoneSR.start();
        } catch(ex) {
            window.addLog('📱 Cannot start mic: ' + ex.message, 'warn');
            _phoneListening = false;
            phoneSetStatus('off');
        }
    }

    function stopPhoneListener() {
        _phoneListening = false;
        _phoneActive    = false;
        clearTimeout(_phoneRestartTimer);
        if (_phoneSR) { try { _phoneSR.abort(); } catch(ex) {} _phoneSR = null; }
        phoneSetStatus('off');
        window.addLog('📱 Phone voice disabled', 'dim');
    }

    // ── PhoneWakeBtn toggle ────────────────────────────────────────────────
    $(document).on('click', '#PhoneWakeBtn', function() {
        if (_phoneListening) {
            stopPhoneListener();
        } else {
            startPhoneListener();
        }
    });

    // ── Status poll ────────────────────────────────────────────────────────
    setInterval(function () {
        fetch('/api/status')
            .then(function (r) { return r.json(); })
            .then(function (d) {
                if (d.active) {
                    $('#statusDot').css({'background':'var(--cyan)','box-shadow':'0 0 8px var(--cyan)'});
                    $('#statusText').text('ONLINE');
                } else {
                    $('#statusDot').css({'background':'var(--blue)','box-shadow':'0 0 6px var(--blue)'});
                    $('#statusText').text('STANDBY');
                }
            }).catch(function(){});
    }, 3000);

    // Keyboard shortcut
    document.addEventListener('keydown', function (e) {
        if (e.ctrlKey && e.altKey && e.key.toLowerCase() === 'j') {
            e.preventDefault(); processCommand('hello');
        }
    });

});
