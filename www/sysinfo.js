/**
 * sysinfo.js — polls /api/system_stats and updates UI panels
 */
(function () {
    'use strict';
    var POLL_MS = 2500;

    function setBar(id, pct) {
        var el = document.getElementById(id);
        if (el) el.style.width = Math.min(100, pct) + '%';
    }
    function setTxt(id, txt) {
        var el = document.getElementById(id);
        if (el) el.textContent = txt;
    }
    function applyBarColor(id, pct) {
        var el = document.getElementById(id);
        if (!el) return;
        if (pct > 85) { el.style.background = 'linear-gradient(90deg,#330000,#ff2255)'; }
        else if (pct > 65) { el.style.background = 'linear-gradient(90deg,#331100,#ff6a00)'; }
        // else keep default
    }

    function updateUI(s) {
        // Side panel
        setBar('cpuBar',  s.cpu);          applyBarColor('cpuBar',  s.cpu);
        setTxt('cpuVal',  s.cpu + '%');
        setBar('ramBar',  s.ram_percent);  applyBarColor('ramBar',  s.ram_percent);
        setTxt('ramVal',  s.ram_used + '/' + s.ram_total + 'GB');
        setBar('diskBar', s.disk_percent); applyBarColor('diskBar', s.disk_percent);
        setTxt('diskVal', s.disk_used + '/' + s.disk_total + 'GB');

        // Header mini stats
        setTxt('hdrCpuVal', s.cpu + '%');
        setTxt('hdrRamVal', s.ram_percent + '%');

        // Temp
        setTxt('tempVal', s.cpu_temp != null ? s.cpu_temp + ' °C' : 'N/A');

        // Battery
        if (s.battery != null) {
            setTxt('batVal', s.battery + '%');
            setTxt('hdrBatVal', s.battery + '%');
            var icon = s.battery_charging ? 'bi-battery-charging' :
                       s.battery <= 20    ? 'bi-battery' :
                       s.battery <= 50    ? 'bi-battery-half' : 'bi-battery-full';
            ['batIcon','hdrBatIcon'].forEach(function(id){
                var el = document.getElementById(id);
                if (el) el.className = 'bi ' + icon;
            });
        } else {
            setTxt('batVal', 'AC');
            setTxt('hdrBatVal', 'AC');
        }
    }

    function poll() {
        fetch('/api/system_stats')
            .then(function(r){ return r.json(); })
            .then(function(s){ if(s) updateUI(s); })
            .catch(function(){});
    }

    window.startSysStats = function () { poll(); setInterval(poll, POLL_MS); };
    window.refreshSysStats = poll;
    window.startSysStatPolling = window.startSysStats; // legacy alias
}());
