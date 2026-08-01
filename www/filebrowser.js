/**
 * filebrowser.js — left-lower panel file explorer.
 * Uses REST API: /api/drives, /api/list_directory, /api/open_file, /api/open_explorer
 */

(function () {
    'use strict';

    var EXT_ICONS = {
        '.pdf':  'bi-file-pdf',
        '.doc':  'bi-file-word', '.docx': 'bi-file-word',
        '.xls':  'bi-file-excel','.xlsx': 'bi-file-excel',
        '.ppt':  'bi-file-ppt',  '.pptx': 'bi-file-ppt',
        '.png':  'bi-file-image','.jpg':  'bi-file-image',
        '.jpeg': 'bi-file-image','.gif':  'bi-file-image','.webp':'bi-file-image',
        '.mp3':  'bi-file-music','.wav':  'bi-file-music','.flac':'bi-file-music',
        '.mp4':  'bi-file-play', '.avi':  'bi-file-play', '.mkv': 'bi-file-play',
        '.zip':  'bi-file-zip',  '.rar':  'bi-file-zip',  '.7z': 'bi-file-zip',
        '.py':   'bi-file-code', '.js':   'bi-file-code', '.ts': 'bi-file-code',
        '.html': 'bi-file-code', '.css':  'bi-file-code', '.json':'bi-file-code',
        '.txt':  'bi-file-text', '.md':   'bi-file-text', '.log':'bi-file-text',
        '.exe':  'bi-gear-fill', '.bat':  'bi-terminal',  '.ps1':'bi-terminal',
    };

    function iconFor(ext) {
        return EXT_ICONS[ext] || 'bi-file-earmark';
    }

    var currentPath = null;
    var pathStack   = [];

    var fileList       = document.getElementById('fileList');
    var fileBreadcrumb = document.getElementById('fileBreadcrumb');
    var openExpBtn     = document.getElementById('openInExplorerBtn');

    function setList(html) {
        if (fileList) fileList.innerHTML = html;
    }

    function renderLoading() {
        setList('<div class="file-empty"><i class="bi bi-hourglass-split"></i> Loading...</div>');
    }

    function renderError(msg) {
        setList('<div class="file-error"><i class="bi bi-exclamation-triangle"></i> ' + (msg || 'Error') + '</div>');
    }

    // ── Breadcrumb ────────────────────────────────────────────────────────────
    function buildBreadcrumb() {
        if (!fileBreadcrumb) return;
        var html = '<span class="bc-item" data-path="">Drives</span>';
        for (var i = 0; i < pathStack.length; i++) {
            html += '<span class="bc-sep">›</span>';
            html += '<span class="bc-item" data-path="' + escHtml(pathStack[i].path) + '">' + escHtml(pathStack[i].label) + '</span>';
        }
        fileBreadcrumb.innerHTML = html;

        fileBreadcrumb.querySelectorAll('.bc-item').forEach(function (el) {
            el.addEventListener('click', function () {
                var p = el.getAttribute('data-path');
                if (p === '') {
                    showDrives();
                } else {
                    var idx = pathStack.findIndex(function (s) { return s.path === p; });
                    if (idx >= 0) pathStack = pathStack.slice(0, idx + 1);
                    navigateTo(p);
                }
            });
        });
    }

    // ── Drives ────────────────────────────────────────────────────────────────
    function showDrives() {
        currentPath = null;
        pathStack   = [];
        buildBreadcrumb();
        renderLoading();

        fetch('/api/drives')
            .then(function (r) { return r.json(); })
            .then(function (drives) {
                if (!drives || drives.length === 0) {
                    setList('<div class="file-empty">No drives found</div>');
                    return;
                }
                var html = '';
                drives.forEach(function (d) {
                    html += '<div class="drive-item" data-path="' + escHtml(d.name) + '">'
                          + '<i class="bi bi-device-hdd-fill"></i>'
                          + '<div>'
                          + '<div class="drive-label">' + escHtml(d.label) + '</div>'
                          + '<div class="drive-sub">' + d.free + ' GB free / ' + d.total + ' GB</div>'
                          + '</div></div>';
                });
                setList(html);
                fileList.querySelectorAll('.drive-item').forEach(function (el) {
                    el.addEventListener('click', function () {
                        var p = el.getAttribute('data-path');
                        pathStack = [{ path: p, label: p }];
                        navigateTo(p);
                    });
                });
            })
            .catch(function (e) { renderError(e.message); });
    }

    // ── Directory ─────────────────────────────────────────────────────────────
    function navigateTo(path) {
        currentPath = path;
        buildBreadcrumb();
        renderLoading();

        fetch('/api/list_directory?path=' + encodeURIComponent(path))
            .then(function (r) { return r.json(); })
            .then(function (result) {
                if (!result) { renderError('No result'); return; }
                if (result.error) { renderError(result.error); return; }

                var html = '';

                if (result.parent) {
                    html += '<div class="file-item is-dir go-back" data-path="' + escHtml(result.parent) + '">'
                          + '<i class="bi bi-arrow-up-circle"></i>'
                          + '<span class="file-name">..</span></div>';
                }

                result.dirs.forEach(function (d) {
                    html += '<div class="file-item is-dir" data-path="' + escHtml(d.path) + '" data-name="' + escHtml(d.name) + '">'
                          + '<i class="bi bi-folder-fill"></i>'
                          + '<span class="file-name">' + escHtml(d.name) + '</span></div>';
                });

                result.files.forEach(function (f) {
                    var ico = iconFor(f.ext);
                    html += '<div class="file-item is-file" data-path="' + escHtml(f.path) + '">'
                          + '<i class="bi ' + ico + '"></i>'
                          + '<span class="file-name">' + escHtml(f.name) + '</span>'
                          + '<span class="file-size">' + f.size + '</span></div>';
                });

                if (!result.dirs.length && !result.files.length) {
                    html += '<div class="file-empty">Folder is empty</div>';
                }

                setList(html);
                bindListItems();
            })
            .catch(function (e) { renderError(e.message); });
    }

    function bindListItems() {
        fileList.querySelectorAll('.go-back').forEach(function (el) {
            el.addEventListener('click', function () {
                var p = el.getAttribute('data-path');
                if (pathStack.length > 1) pathStack.pop();
                else pathStack = [];
                navigateTo(p);
            });
        });

        fileList.querySelectorAll('.file-item.is-dir:not(.go-back)').forEach(function (el) {
            el.addEventListener('click', function () {
                var p    = el.getAttribute('data-path');
                var name = el.getAttribute('data-name');
                pathStack.push({ path: p, label: name });
                navigateTo(p);
            });
        });

        fileList.querySelectorAll('.file-item.is-file').forEach(function (el) {
            el.addEventListener('dblclick', function () {
                var p = el.getAttribute('data-path');
                fetch('/api/open_file', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: p })
                }).catch(function () {});
            });
        });
    }

    // ── Open in Explorer ──────────────────────────────────────────────────────
    if (openExpBtn) {
        openExpBtn.addEventListener('click', function () {
            if (!currentPath) return;
            fetch('/api/open_explorer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: currentPath })
            }).catch(function () {});
        });
    }

    function escHtml(str) {
        return String(str)
            .replace(/&/g,  '&amp;')
            .replace(/"/g,  '&quot;')
            .replace(/'/g,  '&#39;')
            .replace(/</g,  '&lt;')
            .replace(/>/g,  '&gt;');
    }

    window.initFileBrowser = function () { showDrives(); };

}());
