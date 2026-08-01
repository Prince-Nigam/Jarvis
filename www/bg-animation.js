/**
 * bg-animation.js — Sci-Fi Jarvis Holographic Background Animation
 * Features:
 * - Fullscreen Canvas
 * - Rotating Arc-Reactor Concentric HUD Rings at Center
 * - Interactive Floating Particle Neural Network Matrix (Constellation Effect)
 * - Pulsing Blue Core & Cyber Grid Glow
 */

(function () {
    'use strict';

    var canvas = document.createElement('canvas');
    canvas.id = 'bg-animation-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100vw';
    canvas.style.height = '100vh';
    canvas.style.zIndex = '0';
    canvas.style.pointerEvents = 'none';
    document.body.prepend(canvas);

    var ctx = canvas.getContext('2d');
    var w, h, cx, cy;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
        cx = w / 2;
        cy = h / 2;
    }
    window.addEventListener('resize', resize);
    resize();

    // ── Mouse tracking ──────────────────────────────────────────────────
    var mouse = { x: cx, y: cy, active: false };
    window.addEventListener('mousemove', function (e) {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
        mouse.active = true;
    });
    window.addEventListener('mouseleave', function () {
        mouse.active = false;
    });

    // ── Particle System ─────────────────────────────────────────────────
    var NUM_PARTICLES = 75;
    var particles = [];

    function Particle() {
        this.reset();
    }

    Particle.prototype.reset = function () {
        this.x = Math.random() * w;
        this.y = Math.random() * h;
        this.vx = (Math.random() - 0.5) * 0.8;
        this.vy = (Math.random() - 0.5) * 0.8;
        this.radius = Math.random() * 2.2 + 0.8;
        this.alpha = Math.random() * 0.5 + 0.3;
        this.color = Math.random() > 0.3 ? '0, 170, 255' : '0, 255, 230'; // blue or cyan
    };

    Particle.prototype.update = function () {
        this.x += this.vx;
        this.y += this.vy;

        // Wrap edges
        if (this.x < 0) this.x = w;
        if (this.x > w) this.x = 0;
        if (this.y < 0) this.y = h;
        if (this.y > h) this.y = 0;

        // Subtle mouse push
        if (mouse.active) {
            var dx = this.x - mouse.x;
            var dy = this.y - mouse.y;
            var dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 120 && dist > 0) {
                var force = (120 - dist) / 120;
                this.x += (dx / dist) * force * 1.5;
                this.y += (dy / dist) * force * 1.5;
            }
        }
    };

    Particle.prototype.draw = function () {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(' + this.color + ', ' + this.alpha + ')';
        ctx.shadowBlur = 8;
        ctx.shadowColor = 'rgba(' + this.color + ', 0.8)';
        ctx.fill();
        ctx.shadowBlur = 0;
    };

    for (var i = 0; i < NUM_PARTICLES; i++) {
        particles.push(new Particle());
    }

    // ── Rotating HUD Rings Parameters ────────────────────────────────────
    var angle1 = 0;
    var angle2 = 0;
    var angle3 = 0;

    function drawHoloHUD() {
        ctx.save();
        ctx.translate(cx, cy);

        // Ambient radial glow core
        var radGlow = ctx.createRadialGradient(0, 0, 10, 0, 0, 320);
        radGlow.addColorStop(0, 'rgba(0, 170, 255, 0.12)');
        radGlow.addColorStop(0.5, 'rgba(0, 100, 200, 0.04)');
        radGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = radGlow;
        ctx.beginPath();
        ctx.arc(0, 0, 320, 0, Math.PI * 2);
        ctx.fill();

        // 1. Outer Segmented Ring (Clockwise)
        ctx.save();
        ctx.rotate(angle1);
        ctx.strokeStyle = 'rgba(0, 170, 255, 0.25)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([12, 18, 4, 18]);
        ctx.beginPath();
        ctx.arc(0, 0, 260, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();

        // 2. Middle Dashed Ring (Counter-Clockwise)
        ctx.save();
        ctx.rotate(-angle2);
        ctx.strokeStyle = 'rgba(0, 255, 230, 0.3)';
        ctx.lineWidth = 2;
        ctx.setLineDash([30, 15, 60, 15]);
        ctx.beginPath();
        ctx.arc(0, 0, 210, 0, Math.PI * 2);
        ctx.stroke();

        // Crosshair tick marks
        ctx.strokeStyle = 'rgba(0, 170, 255, 0.4)';
        ctx.lineWidth = 1;
        ctx.setLineDash([]);
        for (var a = 0; a < Math.PI * 2; a += Math.PI / 4) {
            var x1 = Math.cos(a) * 195;
            var y1 = Math.sin(a) * 195;
            var x2 = Math.cos(a) * 215;
            var y2 = Math.sin(a) * 215;
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
        }
        ctx.restore();

        // 3. Inner Fine Ring (Fast Clockwise)
        ctx.save();
        ctx.rotate(angle3);
        ctx.strokeStyle = 'rgba(0, 170, 255, 0.35)';
        ctx.lineWidth = 1;
        ctx.setLineDash([8, 12]);
        ctx.beginPath();
        ctx.arc(0, 0, 160, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();

        ctx.restore();

        // Update rotation angles
        angle1 += 0.002;
        angle2 += 0.0035;
        angle3 += 0.005;
    }

    // ── Animation Loop ───────────────────────────────────────────────────
    function animate() {
        ctx.clearRect(0, 0, w, h);

        // Draw Central HUD Animation
        drawHoloHUD();

        // Draw Particles & Neural Connections
        for (var i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
        }

        // Draw connecting lines between close particles
        for (var i = 0; i < particles.length; i++) {
            for (var j = i + 1; j < particles.length; j++) {
                var dx = particles[i].x - particles[j].x;
                var dy = particles[i].y - particles[j].y;
                var dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 130) {
                    var alpha = (1 - dist / 130) * 0.25;
                    ctx.strokeStyle = 'rgba(0, 170, 255, ' + alpha + ')';
                    ctx.lineWidth = 0.8;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }

        requestAnimationFrame(animate);
    }

    // Start background animation
    requestAnimationFrame(animate);

})();
