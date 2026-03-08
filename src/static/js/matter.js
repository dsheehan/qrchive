// Simple Bootstrap-compatible theme toggle with persistence
(function() {
    const html = document.documentElement;
    const storageKey = 'theme';
    // Initialize theme from localStorage or system preference
    function getPreferredTheme() {
        const saved = localStorage.getItem(storageKey);
        if (saved === 'light' || saved === 'dark') return saved;
        // fallback to current attribute or system
        if (html.getAttribute('data-bs-theme')) return html.getAttribute('data-bs-theme');
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    function setTheme(t) {
        html.setAttribute('data-bs-theme', t);
        localStorage.setItem(storageKey, t);
    }
    window.toggleTheme = function() {
        const current = html.getAttribute('data-bs-theme') || getPreferredTheme();
        setTheme(current === 'dark' ? 'light' : 'dark');
    }
    // Apply on load
    setTheme(getPreferredTheme());

    // Initialize APP_CONFIG from body data attributes (deferred to DOMContentLoaded)
    window.APP_CONFIG = {
        version: '0.0.0',
        githubRepo: ''
    };

    function initConfig() {
        window.APP_CONFIG.version = document.body.getAttribute('data-version') || '0.0.0';
        window.APP_CONFIG.githubRepo = document.body.getAttribute('data-github-repo') || '';
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initConfig);
    } else {
        initConfig();
    }
    // Keep in sync with OS changes when no explicit preference stored
    if (!localStorage.getItem(storageKey) && window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            setTheme(e.matches ? 'dark' : 'light');
        });
    }
})();

const BASE38_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ -.";

function encodeBase38(val) {
    let res = "";
    while (val > 0n) {
        res += BASE38_CHARS[Number(val % 38n)];
        val /= 38n;
    }
    return res;
}

function formatMatterQR(pairingCode) {
    // Remove dashes
    const digits = pairingCode.replace(/-/g, "");
    if (digits.length !== 11) return pairingCode;

    const passcode = parseInt(digits, 10);
    
    // Default values if not provided
    const version = 0;
    const vendorId = 0xFFF1; // Test VID
    const productId = 0x8000; // Test PID
    const commissioningFlow = 0; // Standard
    const discoveryCapabilities = 2; // BLE
    const discriminator = 3840; // Default

    // Matter QR Code Bit Layout (LSB first):
    // 0-2: Version (3 bits)
    // 3-14: Discriminator (12 bits)
    // 15-41: Passcode (27 bits)
    // 42-43: Commissioning Flow (2 bits)
    // 44-51: Discovery Capabilities (8 bits)
    // 52-67: Vendor ID (16 bits)
    // 68-83: Product ID (16 bits)
    // Total: 84 bits

    let val = 0n;
    val |= BigInt(version & 0x7);
    val |= BigInt(discriminator & 0xFFF) << 3n;
    val |= BigInt(passcode & 0x7FFFFFF) << 15n;
    val |= BigInt(commissioningFlow & 0x3) << 42n;
    val |= BigInt(discoveryCapabilities & 0xFF) << 44n;
    val |= BigInt(vendorId & 0xFFFF) << 52n;
    val |= BigInt(productId & 0xFFFF) << 68n;

    return "MT:" + encodeBase38(val);
}

let qrCode;
let isMaximized = false;
let currentCode, currentProduct, currentPrecomputedQR;
let bootstrapModal;
let deviceModal;

function openDeviceModal(mac = null, skipPushState = false) {
    const modalEl = document.getElementById("deviceModal");
    if (!deviceModal) {
        deviceModal = new bootstrap.Modal(modalEl);
        
        // Handle URL cleanup when modal is closed (via button, backdrop, or ESC)
        modalEl.addEventListener('hidden.bs.modal', () => {
            const params = new URLSearchParams(window.location.search);
            if (params.has("edit") || params.has("add")) {
                params.delete("edit");
                params.delete("add");
                const search = params.toString();
                const newUrl = window.location.pathname + (search ? "?" + search : "");
                window.history.pushState({}, "", newUrl);
            }
        });
    }

    const form = document.getElementById("deviceForm");
    form.reset();
    document.getElementById("originalMac").value = mac || "";
    document.getElementById("deviceModalLabel").innerText = mac ? "Edit Device" : "Add New Device";
    document.getElementById("deleteBtn").style.display = mac ? "block" : "none";

    if (mac) {
        // Find the row with this MAC and populate form
        const row = document.querySelector(`tr[data-mac="${mac}"]`);
        if (row) {
            const cells = row.querySelectorAll('td[data-header]');
            cells.forEach(td => {
                const header = td.getAttribute('data-header');
                const input = form.querySelector(`[name="${header}"]`);
                if (input) {
                    input.value = td.innerText;
                }
            });
        }
    }

    // Ensure scanner is stopped and hidden when modal opens
    stopScanner();
    if (document.getElementById("qr-reader")) document.getElementById("qr-reader").style.display = "none";
    if (document.getElementById("stopScannerBtn")) document.getElementById("stopScannerBtn").style.display = "none";

    if (!skipPushState) {
        const params = new URLSearchParams(window.location.search);
        if (mac) {
            params.set("edit", mac);
            params.delete("add");
        } else {
            params.set("add", "true");
            params.delete("edit");
        }
        // Also clear QR parameters when opening device modal
        params.delete("code");
        params.delete("product");
        params.delete("qr");
        params.delete("maximized");
        
        const newUrl = window.location.pathname + "?" + params.toString();
        window.history.pushState({ edit: mac, add: !mac }, "", newUrl);
    }

    deviceModal.show();
}

async function saveDevice() {
    const form = document.getElementById("deviceForm");
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        if (key !== 'originalMac') {
            data[key] = value;
        }
    });

    const originalMac = document.getElementById("originalMac").value;
    const isEdit = originalMac !== "";
    const url = isEdit ? `/matter/${encodeURIComponent(originalMac)}` : '/matter';
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            deviceModal.hide();
            window.location.href = "/"; // Navigate to root after save
        } else {
            const error = await response.json();
            alert("Error: " + (error.error || "Failed to save device"));
        }
    } catch (err) {
        console.error("Save error:", err);
        alert("An error occurred while saving.");
    }
}

async function deleteDevice() {
    const originalMac = document.getElementById("originalMac").value;
    if (!originalMac) return;

    if (!confirm(`Are you sure you want to delete the device with MAC: ${originalMac}?`)) {
        return;
    }

    try {
        const response = await fetch(`/matter/${encodeURIComponent(originalMac)}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            deviceModal.hide();
            window.location.href = "/"; // Navigate to root after delete
        } else {
            const error = await response.json();
            alert("Error: " + (error.error || "Failed to delete device"));
        }
    } catch (err) {
        console.error("Delete error:", err);
        alert("An error occurred while deleting.");
    }
}

function showQRCode(code, product, precomputedQR, skipPushState = false, maximized = null) {
    currentCode = code;
    currentProduct = product;
    currentPrecomputedQR = precomputedQR;

    const modalEl = document.getElementById("qrModal");
    const modalDialog = document.getElementById("modalDialog");
    const qrcodeDiv = document.getElementById("qrcode");
    const productTitle = document.getElementById("productTitle");
    const codeText = document.getElementById("pairingCodeText");

    if (!bootstrapModal) {
        bootstrapModal = new bootstrap.Modal(modalEl);

        // Handle URL cleanup when modal is closed
        modalEl.addEventListener('hidden.bs.modal', () => {
            const params = new URLSearchParams(window.location.search);
            if (params.has("code") || params.has("product") || params.has("qr") || params.has("maximized")) {
                params.delete("code");
                params.delete("product");
                params.delete("qr");
                params.delete("maximized");
                const search = params.toString();
                const newUrl = window.location.pathname + (search ? "?" + search : "");
                window.history.pushState({}, "", newUrl);
            }
        });
    }

    if (!skipPushState) {
        isMaximized = maximized !== null ? maximized : false;
    } else if (maximized !== null) {
        isMaximized = maximized;
    }

    if (isMaximized) {
        modalDialog.classList.add("modal-fullscreen");
        document.getElementById("maximizeBtn").innerHTML = '<i class="fa-solid fa-down-left-and-up-right-to-center"></i>'; // Restore/Minimize
        document.getElementById("maximizeBtn").title = "Restore";
    } else {
        modalDialog.classList.remove("modal-fullscreen");
        document.getElementById("maximizeBtn").innerHTML = '<i class="fa-solid fa-up-right-and-down-left-from-center"></i>'; // Maximize
        document.getElementById("maximizeBtn").title = "Maximize";
    }

    const matterCode = precomputedQR || formatMatterQR(code);

    if (productTitle) {
        productTitle.innerText = product;
    }
    codeText.innerText = "Setup Code: " + code; 
    const matterText = document.getElementById("matterCodeText");
    if (matterText) {
        matterText.innerText = "QR Data: " + matterCode;
    }
    qrcodeDiv.innerHTML = "";
    
    bootstrapModal.show();

    const size = isMaximized ? Math.min(window.innerWidth, window.innerHeight) * 0.7 : 250;

    qrCode = new QRCodeStyling({
        width: size,
        height: size,
        type: "canvas",
        data: matterCode,
        dotsOptions: {
            color: "#000000",
            type: "square"
        },
        backgroundOptions: {
            color: "#ffffff",
        },
        qrOptions: {
            errorCorrectionLevel: "H"
        }
    });

    qrCode.append(qrcodeDiv);

    if (!skipPushState) {
        const params = new URLSearchParams(window.location.search);
        params.set("code", code);
        params.set("product", product);
        if (precomputedQR) {
            params.set("qr", precomputedQR);
        } else {
            params.delete("qr");
        }
        if (isMaximized) {
            params.set("maximized", "true");
        } else {
            params.delete("maximized");
        }
        const newUrl = window.location.pathname + "?" + params.toString();
        window.history.pushState({ code, product, qr: precomputedQR, maximized: isMaximized }, "", newUrl);
    }
}

function toggleMaximize() {
    isMaximized = !isMaximized;
    
    // Update URL and history state
    if (currentCode) {
        const params = new URLSearchParams(window.location.search);
        if (isMaximized) {
            params.set("maximized", "true");
        } else {
            params.delete("maximized");
        }
        const newUrl = window.location.pathname + "?" + params.toString();
        window.history.pushState({ code: currentCode, product: currentProduct, qr: currentPrecomputedQR, maximized: isMaximized }, "", newUrl);
        
        // Re-render QR code with new size
        showQRCode(currentCode, currentProduct, currentPrecomputedQR, true, isMaximized);
    }
}

function closeModal() {
    if (bootstrapModal) {
        bootstrapModal.hide();
    }
}

window.onclick = function(event) {
    // Bootstrap handles closing on backdrop click
}

function closeDeviceModal() {
    if (deviceModal) {
        deviceModal.hide();
    }
    stopScanner();
}

async function importCSV(input) {
    if (input.files && input.files[0]) {
        const formData = new FormData();
        formData.append('file', input.files[0]);

        try {
            const response = await fetch('/matter/import', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                alert(`Imported successfully. ${result.added_count} new records added.`);
                window.location.reload();
            } else {
                const error = await response.json();
                alert("Error during import: " + (error.error || "Unknown error"));
            }
        } catch (err) {
            console.error("Import error:", err);
            alert("An error occurred while importing.");
        } finally {
            input.value = ''; // Reset file input
        }
    }
}

let html5QrCode = null;
let latestRelease = null;

async function fetchLatestRelease() {
    if (!window.APP_CONFIG || !window.APP_CONFIG.githubRepo) {
        console.warn("APP_CONFIG or githubRepo missing, skipping release fetch.");
        return null;
    }
    try {
        console.log(`Fetching latest release from GitHub: ${window.APP_CONFIG.githubRepo}`);
        const response = await fetch(`https://api.github.com/repos/${window.APP_CONFIG.githubRepo}/releases/latest`, {
            headers: {
                'Accept': 'application/vnd.github.v3.html+json'
            }
        });
        if (response.ok) {
            const data = await response.json();
            const latestTag = data.tag_name || "0.0.0";
            const result = {
                current_version: window.APP_CONFIG.version,
                latest_version: latestTag,
                is_newer: isNewerVersion(latestTag, window.APP_CONFIG.version),
                release_notes_html: data.body_html,
                html_url: data.html_url
            };
            console.log("Latest release fetch result:", result);
            return result;
        } else {
            console.error(`GitHub API responded with status: ${response.status} ${response.statusText}`);
            // Check for rate limiting
            if (response.status === 403 && response.headers.get('X-RateLimit-Remaining') === '0') {
                console.warn("GitHub API rate limit exceeded.");
            }
        }
    } catch (err) {
        console.error("Failed to fetch release info from GitHub:", err);
    }
    return null;
}

async function checkUpdates() {
    try {
        latestRelease = await fetchLatestRelease();
        if (latestRelease && latestRelease.is_newer) {
            const indicator = document.getElementById('updateIndicator');
            if (indicator) indicator.style.display = 'inline-block';
        }
    } catch (err) {
        console.error("Failed to check for updates:", err);
    }
}

async function showWhatsNew() {
    const modalEl = document.getElementById('whatsNewModal');
    if (!modalEl) {
        console.error("whatsNewModal element not found!");
        return;
    }
    const modal = new bootstrap.Modal(modalEl);
    
    if (!latestRelease) {
        latestRelease = await fetchLatestRelease();
    }

    if (latestRelease) {
        document.getElementById('whatsNewVersion').innerText = `Version ${latestRelease.latest_version}`;
        // Use a fallback if body_html is missing (though our header requests it)
        const notes = latestRelease.release_notes_html || "<p>No release notes provided in HTML format.</p>";
        document.getElementById('whatsNewContent').innerHTML = notes;
        
        const viewOnGithubBtn = document.getElementById('viewOnGithub');
        if (viewOnGithubBtn && latestRelease.html_url) {
            viewOnGithubBtn.href = latestRelease.html_url;
        }
    } else {
        document.getElementById('whatsNewContent').innerHTML = "<p class='text-danger'>Could not fetch release notes from GitHub.</p>";
    }
    
    modal.show();
}

window.startScanner = function() {
    const readerDiv = document.getElementById('qr-reader');
    const stopBtn = document.getElementById('stopScannerBtn');
    if (readerDiv) readerDiv.style.display = 'block';
    if (stopBtn) stopBtn.style.display = 'block';

    if (!html5QrCode) {
        html5QrCode = new Html5Qrcode("qr-reader");
    }

    const config = { fps: 10, qrbox: { width: 250, height: 250 } };

    html5QrCode.start({ facingMode: "environment" }, config, (decodedText, decodedResult) => {
        const qrInput = document.getElementById('qr');
        if (qrInput) qrInput.value = decodedText;
        stopScanner();
    }).catch((err) => {
        console.error("Error starting QR scanner: ", err);
        alert("Could not start camera. Please ensure you have given permission.");
        if (readerDiv) readerDiv.style.display = 'none';
        if (stopBtn) stopBtn.style.display = 'none';
    });
}

window.stopScanner = function() {
    if (html5QrCode && html5QrCode.isScanning) {
        html5QrCode.stop().then(() => {
            const readerDiv = document.getElementById('qr-reader');
            const stopBtn = document.getElementById('stopScannerBtn');
            if (readerDiv) readerDiv.style.display = 'none';
            if (stopBtn) stopBtn.style.display = 'none';
        }).catch((err) => {
            console.error("Error stopping QR scanner: ", err);
        });
    } else {
        const readerDiv = document.getElementById('qr-reader');
        const stopBtn = document.getElementById('stopScannerBtn');
        if (readerDiv) readerDiv.style.display = 'none';
        if (stopBtn) stopBtn.style.display = 'none';
    }
}

window.handleQRFile = function(input) {
    if (input.files && input.files[0]) {
        // Use a temporary scanner for file scan if main one is not initialized or is busy
        const scanner = html5QrCode || new Html5Qrcode("qr-reader");
        const imageFile = input.files[0];
        scanner.scanFile(imageFile, true)
            .then(decodedText => {
                const qrInput = document.getElementById('qr');
                if (qrInput) qrInput.value = decodedText;
                input.value = ""; // Reset input
            })
            .catch(err => {
                console.error("Error scanning file: ", err);
                alert("Could not find a QR code in this image.");
                input.value = ""; // Reset input
            });
    }
}

function checkUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const product = params.get("product");
    const qr = params.get("qr");
    const maximized = params.get("maximized") === "true";
    
    const editMac = params.get("edit");
    const addMode = params.get("add") === "true";

    if (code && product) {
        showQRCode(code, product, qr, true, maximized);
    } else if (editMac) {
        openDeviceModal(editMac, true);
    } else if (addMode) {
        openDeviceModal(null, true);
    }
}

window.addEventListener("load", checkUrlParams);
window.addEventListener("popstate", (event) => {
    if (event.state && event.state.code && event.state.product) {
        showQRCode(event.state.code, event.state.product, event.state.qr, true, event.state.maximized);
    } else if (event.state && (event.state.edit || event.state.add)) {
        openDeviceModal(event.state.edit || null, true);
    } else {
        const params = new URLSearchParams(window.location.search);
        const code = params.get("code");
        const product = params.get("product");
        const qr = params.get("qr");
        const maximized = params.get("maximized") === "true";
        
        const editMac = params.get("edit");
        const addMode = params.get("add") === "true";

        if (code && product) {
            showQRCode(code, product, qr, true, maximized);
        } else if (editMac) {
            openDeviceModal(editMac, true);
        } else if (addMode) {
            openDeviceModal(null, true);
        } else {
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
            if (deviceModal) {
                deviceModal.hide();
            }
        }
    }
});

// ---- Advanced table features: filtering, sorting, column hiding ----
(function(){
    function getTable() {
        return document.getElementById('devicesTable');
    }
    function getHeaderCells(table){
        return table ? table.tHead.querySelectorAll('th[data-col-index]') : [];
    }
    function getBodyRows(table){
        return table ? table.tBodies[0].rows : [];
    }
    function isColumnVisible(idx){
        const cb = document.getElementById('col-toggle-' + idx);
        return !cb || cb.checked; // default visible if control missing
    }
    function applyColumnVisibility(){
        const table = getTable();
        if (!table) return;
        const headers = getHeaderCells(table);
        headers.forEach((th)=>{
            const idx = parseInt(th.getAttribute('data-col-index'));
            const show = isColumnVisible(idx);
            th.style.display = show ? '' : 'none';
        });
        const rows = getBodyRows(table);
        Array.from(rows).forEach((tr)=>{
            Array.from(tr.cells).forEach((td, i)=>{
                // last column is QR Code button; do not control it here
                if (i < headers.length) {
                    const show = isColumnVisible(i);
                    td.style.display = show ? '' : 'none';
                }
            });
        });
    }
    function normalize(val){
        return (val||'').toString().trim();
    }
    function cmp(a,b){
        const an = parseFloat(a); const bn = parseFloat(b);
        const aNum = !isNaN(an) && a.match(/^[-+]?\d+(?:\.\d+)?$/);
        const bNum = !isNaN(bn) && b.match(/^[-+]?\d+(?:\.\d+)?$/);
        if (aNum && bNum) return an - bn;
        return a.localeCompare(b, undefined, { sensitivity: 'base', numeric: true });
    }
    function clearSortIndicators(table){
        getHeaderCells(table).forEach(th=>{
            th.setAttribute('aria-sort','none');
            const icon = th.querySelector('i.fa-solid');
            if (icon){ icon.classList.remove('fa-sort-up','fa-sort-down'); icon.classList.add('fa-sort'); }
        });
    }
    function setSortIndicator(th, asc){
        th.setAttribute('aria-sort', asc ? 'ascending' : 'descending');
        const icon = th.querySelector('i.fa-solid');
        if (icon){ icon.classList.remove('fa-sort'); icon.classList.add(asc ? 'fa-sort-up' : 'fa-sort-down'); }
    }
    function sortTableByColumn(table, column, asc){
        const tbody = table.tBodies[0];
        const rows = Array.from(tbody.querySelectorAll('tr'));
        rows.sort((r1, r2)=>{
            const c1 = normalize((r1.cells[column] || {}).innerText || '');
            const c2 = normalize((r2.cells[column] || {}).innerText || '');
            const res = cmp(c1, c2);
            return asc ? res : -res;
        });
        rows.forEach(r=>tbody.appendChild(r));
    }
    function applyGlobalFilter(){
        const table = getTable();
        const q = (document.getElementById('globalFilter')?.value || '').toLowerCase().trim();
        const words = q.split(/\s+/).filter(w => w.length > 0);

        // Filter Table Rows
        if (table) {
            const headers = getHeaderCells(table);
            const rows = getBodyRows(table);
            
            Array.from(rows).forEach(tr=>{
                let match = true;
                if (words.length > 0) {
                    for (const word of words) {
                        let wordFound = false;
                        for (let i=0; i<headers.length; i++) {
                            if (!isColumnVisible(i)) continue;
                            const text = (tr.cells[i]?.innerText || '').toLowerCase();
                            if (text.includes(word)) {
                                wordFound = true;
                                break;
                            }
                        }
                        if (!wordFound) {
                            match = false;
                            break;
                        }
                    }
                }
                tr.style.display = match ? '' : 'none';
            });
        }

        // Filter Grid Cards
        const gridItems = document.querySelectorAll('.device-card-col');
        gridItems.forEach(item => {
            let match = true;
            if (words.length > 0) {
                const text = item.innerText.toLowerCase();
                for (const word of words) {
                    if (!text.includes(word)) {
                        match = false;
                        break;
                    }
                }
            }
            item.classList.toggle('d-none', !match);
        });
    }
    function bindSorting(){
        const table = getTable();
        if (!table) return;
        const headers = getHeaderCells(table);
        const state = {};
        headers.forEach((th)=>{
            const idx = parseInt(th.getAttribute('data-col-index'));
            function activate(){
                const asc = !(state[idx] === true); // toggle
                clearSortIndicators(table);
                sortTableByColumn(table, idx, asc);
                setSortIndicator(th, asc);
                state[idx] = asc;
            }
            th.addEventListener('click', activate);
            th.addEventListener('keypress', (e)=>{ if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(); }});
        });
    }
    function bindColumnToggles(){
        const toggles = document.querySelectorAll('.column-toggle');
        toggles.forEach(cb=>{
            cb.addEventListener('change', ()=>{
                applyColumnVisibility();
                applyGlobalFilter();
            });
        });
    }
    function bindFilter(){
        const input = document.getElementById('globalFilter');
        if (input){ input.addEventListener('input', applyGlobalFilter); }
    }
    window.setView = function(view) {
        const listView = document.getElementById('listView');
        const gridView = document.getElementById('gridView');
        const listViewBtn = document.getElementById('listViewBtn');
        const gridViewBtn = document.getElementById('gridViewBtn');

        if (view === 'grid') {
            listView.classList.add('d-none');
            gridView.classList.remove('d-none');
            listViewBtn.classList.remove('active');
            gridViewBtn.classList.add('active');
            renderGridQRCodes();
        } else {
            listView.classList.remove('d-none');
            gridView.classList.add('d-none');
            listViewBtn.classList.add('active');
            gridViewBtn.classList.remove('active');
        }
        localStorage.setItem('preferredView', view);
    };

    window.printGrid = function() {
        // Ensure we are in grid view and QR codes are rendered
        const currentView = localStorage.getItem('preferredView');
        if (currentView !== 'grid') {
            window.setView('grid');
        } else {
            renderGridQRCodes();
        }
        
        // Short delay to ensure everything is rendered before print dialog
        setTimeout(() => {
            window.print();
        }, 300);
    };

    function renderGridQRCodes() {
        const placeholders = document.querySelectorAll('.qr-placeholder');
        placeholders.forEach(ph => {
            if (ph.dataset.rendered) return;
            const code = ph.dataset.code;
            const precomputed = ph.dataset.precomputed;
            const finalCode = precomputed || formatMatterQR(code);
            
            if (typeof QRCodeStyling === 'undefined') {
                console.error("QRCodeStyling is not loaded!");
                return;
            }
            const qr = new QRCodeStyling({
                width: 200,
                height: 200,
                type: "canvas",
                data: finalCode,
                dotsOptions: { color: "#000000", type: "square" },
                backgroundOptions: { color: "#ffffff" },
                qrOptions: { errorCorrectionLevel: "H" }
            });
            ph.innerHTML = '';
            qr.append(ph);
            ph.dataset.rendered = "true";
        });
    }

    function init(){
        applyColumnVisibility();
        bindSorting();
        bindColumnToggles();
        bindFilter();
        checkUpdates();

        const savedView = localStorage.getItem('preferredView') || 'list';
        setView(savedView);
    }
    if (document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
