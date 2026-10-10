// Preprocessing Page - ETL Pipeline

async function uploadFile(input) {
    const file = input.files[0];
    if (!file) return;

    const progressDiv = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('uploadProgressFill');
    const statusSpan = document.getElementById('uploadStatus');

    progressDiv.style.display = 'block';
    progressFill.style.width = '30%';
    statusSpan.textContent = 'Uploading...';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const xhr = new XMLHttpRequest();
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const pct = Math.round((e.loaded / e.total) * 100);
                progressFill.style.width = pct + '%';
                statusSpan.textContent = `Uploading... ${pct}%`;
            }
        });

        xhr.addEventListener('load', () => {
            progressFill.style.width = '100%';
            const result = JSON.parse(xhr.responseText);
            if (result.success) {
                statusSpan.textContent = 'Upload complete!';
                showToast('Dataset uploaded successfully!', 'success');
                setTimeout(() => checkStatus(), 1000);
            } else {
                statusSpan.textContent = result.error || 'Upload failed';
                showToast(result.error || 'Upload failed', 'error');
            }
        });

        xhr.addEventListener('error', () => {
            statusSpan.textContent = 'Upload failed';
            showToast('Upload failed', 'error');
        });

        xhr.open('POST', '/api/upload');
        xhr.send(formData);
    } catch (err) {
        statusSpan.textContent = err.message;
        showToast('Upload failed: ' + err.message, 'error');
    }
}

async function checkStatus() {
    try {
        const data = await apiGet('/api/etl/status');
        const statusEl = document.getElementById('etlStatus');

        if (data.db_ready) {
            statusEl.innerHTML = `
                <div class="status-indicator success">
                    <i class="fas fa-check-circle"></i> Database ready — ETL has been run
                </div>
            `;
            loadPreprocessingInfo();
        } else if (data.raw_csv_exists) {
            statusEl.innerHTML = `
                <div class="status-indicator warning">
                    <i class="fas fa-exclamation-circle"></i> Raw CSV found but ETL not yet run
                </div>
            `;
        } else {
            statusEl.innerHTML = `
                <div class="status-indicator error">
                    <i class="fas fa-times-circle"></i> No raw CSV found. Place healthcare_raw_data_150000.csv in data/raw/
                </div>
            `;
        }
    } catch (err) {
        console.error(err);
    }
}

async function runETL() {
    const btn = document.getElementById('runEtlBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running ETL...';

    // Animate pipeline steps
    animateStep('step-extract', 'extract-status', 'Extracting...');

    try {
        const result = await apiPost('/api/etl/run', {});

        if (result.success) {
            animateStep('step-transform', 'transform-status', 'Transforming...');
            await sleep(500);
            animateStep('step-load', 'load-status', 'Loading...');
            await sleep(500);

            // Mark all complete
            completeStep('step-extract', 'extract-status');
            completeStep('step-transform', 'transform-status');
            completeStep('step-load', 'load-status');

            showToast('ETL pipeline completed successfully!', 'success');
            displayResults(result);
        } else {
            showToast(result.error || 'ETL failed', 'error');
            resetSteps();
        }
    } catch (err) {
        showToast('ETL failed: ' + err.message, 'error');
        resetSteps();
    }

    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-play"></i> Run ETL Pipeline';
}

async function loadPreprocessingInfo() {
    try {
        const data = await apiGet('/api/preprocessing/info');
        if (data.error) return;

        document.getElementById('preprocessingResults').style.display = 'block';
        document.getElementById('rawRows').textContent = formatNumber(data.raw_profile.total_rows);
        document.getElementById('cleanRows').textContent = formatNumber(data.clean_rows);
        document.getElementById('dupRemoved').textContent = formatNumber(data.raw_profile.duplicates);
        document.getElementById('missingFilled').textContent = formatNumber(
            Object.values(data.raw_profile.missing).reduce((a, b) => a + b, 0)
        );

        // Transform steps
        const stepsContainer = document.getElementById('transformSteps');
        stepsContainer.innerHTML = data.transform_report.steps.map((s, i) => `
            <div class="transform-step">
                <div class="transform-step-num">${i + 1}</div>
                <div class="transform-step-content">
                    <strong>${s.step}</strong>
                    <p>${s.description}</p>
                </div>
            </div>
        `).join('');

        // Profile table
        const tbody = document.querySelector('#profileTable tbody');
        tbody.innerHTML = data.raw_profile.columns.map(col => `
            <tr>
                <td>${col}</td>
                <td><span class="dtype-badge">${data.raw_profile.dtypes[col]}</span></td>
                <td>${data.raw_profile.missing[col]}</td>
                <td>
                    <div class="missing-bar">
                        <div class="missing-fill" style="width: ${data.raw_profile.missing_pct[col]}%"></div>
                        <span>${data.raw_profile.missing_pct[col]}%</span>
                    </div>
                </td>
            </tr>
        `).join('');

    } catch (err) {
        console.error(err);
    }
}

function displayResults(result) {
    document.getElementById('preprocessingResults').style.display = 'block';
    document.getElementById('rawRows').textContent = formatNumber(result.profile.total_rows);
    document.getElementById('cleanRows').textContent = formatNumber(result.transform.rows_after);
    document.getElementById('dupRemoved').textContent = formatNumber(result.profile.duplicates);
    document.getElementById('missingFilled').textContent = formatNumber(
        Object.values(result.profile.missing).reduce((a, b) => a + b, 0)
    );

    const stepsContainer = document.getElementById('transformSteps');
    stepsContainer.innerHTML = result.transform.steps.map((s, i) => `
        <div class="transform-step">
            <div class="transform-step-num">${i + 1}</div>
            <div class="transform-step-content">
                <strong>${s.step}</strong>
                <p>${s.description}</p>
            </div>
        </div>
    `).join('');

    const tbody = document.querySelector('#profileTable tbody');
    tbody.innerHTML = result.profile.columns.map(col => `
        <tr>
            <td>${col}</td>
            <td><span class="dtype-badge">${result.profile.dtypes[col]}</span></td>
            <td>${result.profile.missing[col]}</td>
            <td>
                <div class="missing-bar">
                    <div class="missing-fill" style="width: ${result.profile.missing_pct[col]}%"></div>
                    <span>${result.profile.missing_pct[col]}%</span>
                </div>
            </td>
        </tr>
    `).join('');
}

function animateStep(stepId, statusId, text) {
    document.getElementById(stepId).classList.add('active');
    document.getElementById(statusId).textContent = text;
    document.getElementById(statusId).className = 'step-status running';
}

function completeStep(stepId, statusId) {
    document.getElementById(stepId).classList.remove('active');
    document.getElementById(stepId).classList.add('complete');
    document.getElementById(statusId).textContent = 'Complete';
    document.getElementById(statusId).className = 'step-status complete';
}

function resetSteps() {
    ['step-extract', 'step-transform', 'step-load'].forEach(id => {
        document.getElementById(id).classList.remove('active', 'complete');
    });
    ['extract-status', 'transform-status', 'load-status'].forEach(id => {
        document.getElementById(id).textContent = 'Pending';
        document.getElementById(id).className = 'step-status';
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

document.addEventListener('DOMContentLoaded', checkStatus);
