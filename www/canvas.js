/**
 * canvas.js — JARVIS HUD Circle (Iron Man style)
 * Outer tick ring + glowing arc bands + rotating segments + center text
 */
(function () {
    'use strict';

    var canvas, ctx, W, H, cx, cy;
    var raf;
    var angle1 = 0, angle2 = 0, angle3 = 0;
    var yellowArcAngle = 0;
    var dotAngles = [0, 1.1, 2.3, 3.7, 4.9];

    function init() {
        canvas = document.getElementById('particleCanvas');
        if (!canvas) return;
        ctx = canvas.getContext('2d');
        resize();
        loop();
        window.addEventListener('resize', resize);
    }

    function resize() {
        var wrap = canvas.parentElement;
        W = canvas.width  = wrap.offsetWidth;
        H = canvas.height = wrap.offsetHeight;
        cx = W / 2;
        cy = H / 2;
    }

    function loop() {
        ctx.clearRect(0, 0, W, H);

        var R = Math.min(W, H) * 0.44;  // outer radius

        drawOuterTickRing(R);
        drawOuterGlowBand(R);
        drawMiddleRing(R);
        drawInnerArcBand(R);
        drawSegmentedRing(R);
        drawYellowArc(R);
        drawDots(R);
        drawCenterText(R);
        drawGlowCore(R);

        // advance angles
        angle1 += 0.002;
        angle2 -= 0.003;
        angle3 += 0.007;
        yellowArcAngle += 0.008;
        for (var i = 0; i < dotAngles.length; i++) dotAngles[i] += 0.015;

        raf = requestAnimationFrame(loop);
    }

    /* ── 1. Outer tick ring ───────────────────────────────── */
    function drawOuterTickRing(R) {
        var tickCount = 120;
        for (var i = 0; i < tickCount; i++) {
            var a = (i / tickCount) * Math.PI * 2 + angle1;
            var isMajor = i % 10 === 0;
            var isMed   = i % 5  === 0;
            var len  = isMajor ? 14 : isMed ? 8 : 4;
            var w    = isMajor ? 1.5 : 0.8;
            var r1   = R;
            var r2   = R - len;
            var alpha = isMajor ? 0.9 : isMed ? 0.55 : 0.3;

            ctx.beginPath();
            ctx.moveTo(cx + Math.cos(a) * r1, cy + Math.sin(a) * r1);
            ctx.lineTo(cx + Math.cos(a) * r2, cy + Math.sin(a) * r2);
            ctx.strokeStyle = 'rgba(0,220,255,' + alpha + ')';
            ctx.lineWidth = w;
            ctx.stroke();
        }

        // outer border circle
        ctx.beginPath();
        ctx.arc(cx, cy, R, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0,200,255,0.5)';
        ctx.lineWidth = 2;
        ctx.stroke();

        // outer glow ring
        ctx.beginPath();
        ctx.arc(cx, cy, R + 4, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0,200,255,0.12)';
        ctx.lineWidth = 8;
        ctx.stroke();
    }

    /* ── 2. Outer glow band (thick cyan arc) ─────────────── */
    function drawOuterGlowBand(R) {
        var r1 = R - 18;
        var r2 = R - 38;

        // solid fill band
        ctx.beginPath();
        ctx.arc(cx, cy, r1, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0,210,255,0.18)';
        ctx.lineWidth = 20;
        ctx.stroke();

        // bright rotating highlight arc
        var start = angle2;
        var end   = angle2 + Math.PI * 0.6;
        var grad = ctx.createConicalGradient
            ? null
            : null;

        ctx.beginPath();
        ctx.arc(cx, cy, r1, start, end);
        ctx.strokeStyle = 'rgba(0,230,255,0.55)';
        ctx.lineWidth = 18;
        ctx.shadowColor = '#00d4ff';
        ctx.shadowBlur  = 18;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // inner edge line
        ctx.beginPath();
        ctx.arc(cx, cy, r2, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0,180,255,0.4)';
        ctx.lineWidth = 1.5;
        ctx.stroke();
    }

    /* ── 3. Middle solid ring ─────────────────────────────── */
    function drawMiddleRing(R) {
        var r = R - 46;

        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0,200,255,0.65)';
        ctx.lineWidth = 3;
        ctx.shadowColor = '#00d4ff';
        ctx.shadowBlur  = 12;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // inner glow
        ctx.beginPath();
        ctx.arc(cx, cy, r - 5, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0,180,255,0.2)';
        ctx.lineWidth = 8;
        ctx.stroke();
    }

    /* ── 4. Inner arc band with tick marks ───────────────── */
    function drawInnerArcBand(R) {
        var r = R - 62;

        // tick marks on inner band (rotate opposite)
        var tickCount = 80;
        for (var i = 0; i < tickCount; i++) {
            var a = (i / tickCount) * Math.PI * 2 - angle3 * 0.4;
            var isMajor = i % 8 === 0;
            var len  = isMajor ? 10 : 5;
            var r1   = r + 2;
            var r2   = r + 2 - len;
            ctx.beginPath();
            ctx.moveTo(cx + Math.cos(a) * r1, cy + Math.sin(a) * r1);
            ctx.lineTo(cx + Math.cos(a) * r2, cy + Math.sin(a) * r2);
            ctx.strokeStyle = isMajor ? 'rgba(0,200,255,0.6)' : 'rgba(0,180,255,0.25)';
            ctx.lineWidth = isMajor ? 1.2 : 0.7;
            ctx.stroke();
        }

        // band border
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0,190,255,0.5)';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(cx, cy, r + 14, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0,160,220,0.3)';
        ctx.lineWidth = 1;
        ctx.stroke();
    }

    /* ── 5. Segmented rotating ring ──────────────────────── */
    function drawSegmentedRing(R) {
        var r    = R - 74;
        var segs = 24;
        var gap  = 0.04;

        for (var i = 0; i < segs; i++) {
            var start = (i / segs) * Math.PI * 2 + angle3 + gap;
            var end   = ((i + 1) / segs) * Math.PI * 2 + angle3 - gap;
            var bright = (i % 4 === 0);
            ctx.beginPath();
            ctx.arc(cx, cy, r, start, end);
            ctx.strokeStyle = bright
                ? 'rgba(0,220,255,0.55)'
                : 'rgba(0,170,220,0.25)';
            ctx.lineWidth = bright ? 3 : 1.5;
            if (bright) { ctx.shadowColor = '#00d4ff'; ctx.shadowBlur = 8; }
            ctx.stroke();
            ctx.shadowBlur = 0;
        }
    }

    /* ── 6. Yellow indicator arc ─────────────────────────── */
    function drawYellowArc(R) {
        var r     = R - 55;
        var start = yellowArcAngle + Math.PI * 0.75;
        var end   = yellowArcAngle + Math.PI * 0.75 + Math.PI * 0.18;

        ctx.beginPath();
        ctx.arc(cx, cy, r, start, end);
        ctx.strokeStyle = '#ffe600';
        ctx.lineWidth = 4;
        ctx.shadowColor = '#ffe600';
        ctx.shadowBlur  = 14;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // small yellow dot at start
        var dx = cx + Math.cos(start) * r;
        var dy = cy + Math.sin(start) * r;
        ctx.beginPath();
        ctx.arc(dx, dy, 3.5, 0, Math.PI * 2);
        ctx.fillStyle = '#ffe600';
        ctx.shadowColor = '#ffe600';
        ctx.shadowBlur = 10;
        ctx.fill();
        ctx.shadowBlur = 0;
    }

    /* ── 7. Glowing dots on ring ─────────────────────────── */
    function drawDots(R) {
        var r = R - 28;
        var colors = ['#00ffe7','#00d4ff','#00ffe7','#ffe600','#00d4ff'];
        for (var i = 0; i < dotAngles.length; i++) {
            var dx = cx + Math.cos(dotAngles[i]) * r;
            var dy = cy + Math.sin(dotAngles[i]) * r;
            ctx.beginPath();
            ctx.arc(dx, dy, 3, 0, Math.PI * 2);
            ctx.fillStyle = colors[i];
            ctx.shadowColor = colors[i];
            ctx.shadowBlur = 10;
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }

    /* ── 8. Center text ──────────────────────────────────── */
    function drawCenterText(R) {
        var innerR = R - 82;

        // dark center fill
        ctx.beginPath();
        ctx.arc(cx, cy, innerR, 0, Math.PI * 2);
        var grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, innerR);
        grad.addColorStop(0,   'rgba(0,30,55,0.85)');
        grad.addColorStop(0.7, 'rgba(0,15,30,0.9)');
        grad.addColorStop(1,   'rgba(0,5,15,0.95)');
        ctx.fillStyle = grad;
        ctx.fill();

        // inner border
        ctx.beginPath();
        ctx.arc(cx, cy, innerR, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0,180,255,0.35)';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // J.A.R.V.I.S. text
        ctx.save();
        ctx.font = 'bold ' + Math.round(innerR * 0.26) + 'px Orbitron, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = '#00d4ff';
        ctx.shadowBlur  = 18;
        ctx.fillText('J.A.R.V.I.S.', cx, cy);
        ctx.shadowBlur = 0;
        ctx.restore();

        // sub-text
        ctx.save();
        ctx.font = Math.round(innerR * 0.1) + 'px Share Tech Mono, monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = 'rgba(0,200,255,0.5)';
        ctx.fillText('ONLINE', cx, cy + innerR * 0.35);
        ctx.restore();
    }

    /* ── 9. Center glow pulse ────────────────────────────── */
    function drawGlowCore(R) {
        var r = R - 82;
        var pulse = 0.5 + 0.5 * Math.sin(Date.now() * 0.002);
        var grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r * 0.6);
        grad.addColorStop(0,   'rgba(0,180,255,' + (0.04 + pulse * 0.06) + ')');
        grad.addColorStop(1,   'rgba(0,100,200,0)');
        ctx.beginPath();
        ctx.arc(cx, cy, r * 0.6, 0, Math.PI * 2);
        ctx.fillStyle = grad;
        ctx.fill();
    }

    // ── Init ──────────────────────────────────────────────────────────────
    var checkInterval = setInterval(function () {
        var el = document.getElementById('particleCanvas');
        if (el && el.offsetWidth > 0) {
            clearInterval(checkInterval);
            init();
        }
    }, 200);

}());
