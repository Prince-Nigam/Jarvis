/**
 * sysinfo.js — polls Python backend for live system stats and updates the
 * left-upper panel every 2 seconds.
 */

(function () {
    'use strict';

    var POLL_MS = 2000;

    function setBar(barId, pct) {
        var el = document.getElementById(barId);
        if (el) el.style.width = Math.min(100, pct) + '%';
    }

    function setTxt(id, txt) {
        var el = document.getElementById(id);
        if (el) el.textContent = txt;
    }

    function applyBarColor(barId, pct) {
        var el = document.getElementById(barId);
        if (!el) return;
        el.classList.remove('bar-warn', 'bar-crit');
        if (pct > 85) el.classList.add('bar-crit');
        else if (pct > 65) el.classList.add('bar-warn');
    }

    function updateUI(stats) {
        // CPU
        setBar('cpuBar', stats.cpu);
        applyBarColor('cpuBar', stats.cpu);
        setTxt('cpuVal', stats.cpu + '%');

        // RAM
        setBar('ramBar', stats.ram_percent);
        applyBarColor('ramBar', stats.ram_percent);
        setTxt('ramVal', stats.ram_used + ' / ' + stats.ram_total + ' GB');

        // Disk
        setBar('diskBar', stats.disk_percent);
        applyBarColor('diskBar', stats.disk_percent);
        setTxt('diskVal', stats.disk_used + ' / ' + stats.disk_total + ' GB');

        // Temperature
        if (stats.cpu_temp !== null && stats.cpu_temp !== undefined) {
            setTxt('tempVal', stats.cpu_temp + ' °C');
            var tb = document.getElementById('tempBadge');
            if (tb) {
                tb.classList.remove('temp-hot', 'temp-ok');
                tb.classList.add(stats.cpu_temp > 80 ? 'temp-hot' : 'temp-ok');
            }
        } else {
            setTxt('tempVal', 'N/A');
        }

        // Battery
        var batVal = document.getElementById('batVal');
        var batIcon = document.getElementById('batIcon');
        if (stats.battery !== null && stats.battery !== undefined) {
            setTxt('batVal', stats.battery + '%');
            if (batIcon) {
                batIcon.className = '';   // clear all bi classes
                if (stats.battery_charging) {
                    batIcon.className = 'bi bi-battery-charging bat-charging';
                } else if (stats.battery <= 20) {
                    batIcon.className = 'bi bi-battery bat-low';
                } else if (stats.battery <= 50) {
                    batIcon.className = 'bi bi-battery-half';
                } else {
                    batIcon.className = 'bi bi-battery-full';
                }
            }
        } else {
            setTxt('batVal', 'Plugged');
            if (batIcon) batIcon.className = 'bi bi-plug-fill';
        }
    }

    function poll() {
        fetch('/api/system_stats')
            .then(function (r) { return r.json(); })
            .then(function (stats) { if (stats) updateUI(stats); })
            .catch(function () { /* server not ready yet */ });
    }

    // Start polling — called by controller.js after dashboard is shown
    // Also poll immediately on dashboard reveal
    window.refreshSysStats = poll;
    window.startSysStatPolling = function () {
        poll();
        setInterval(poll, POLL_MS);
    };

    // Fallback: if dashboard is already shown on DOMContentLoaded, start polling
    document.addEventListener('DOMContentLoaded', function () {
        var dash = document.getElementById('Dashboard');
        if (dash && !dash.hidden) {
            poll();
            setInterval(poll, POLL_MS);
        }
    });

}());
