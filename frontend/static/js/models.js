// Models Page - Training and Evaluation

let modelCharts = {};

async function checkModelStatus() {
    try {
        const data = await apiGet('/api/ml/status');
        const banner = document.getElementById('modelStatus');

        if (data.trained) {
            banner.innerHTML = `
                <i class="fas fa-check-circle"></i>
                Model trained: <strong>${data.info.best_model}</strong> — Accuracy: ${(data.info.best_accuracy * 100).toFixed(1)}%
            `;
            banner.classList.add('success');
            displayResults(data.info);
        } else {
            banner.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                No trained model found. Click "Train All Models" to begin.
            `;
            banner.classList.add('warning');
        }
    } catch (err) {
        console.error(err);
    }
}

async function trainModels() {
    const btn = document.getElementById('trainBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Training models...';

    showToast('Training in progress... This may take a minute.', 'info');

    try {
        const result = await apiPost('/api/ml/train', {});

        if (result.success) {
            showToast(`Training complete! Best model: ${result.report.best_model}`, 'success');
            displayResults(result.report);
        } else {
            showToast(result.error || 'Training failed', 'error');
        }
    } catch (err) {
        showToast('Training failed: ' + err.message, 'error');
        console.error(err);
    }

    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-play"></i> Train All Models';
}

function displayResults(report) {
    document.getElementById('modelsResults').style.display = 'block';

    // Best model banner
    document.getElementById('bestModelBanner').innerHTML = `
        <i class="fas fa-trophy"></i>
        Best Model: <strong>${report.best_model}</strong> with ${(report.best_accuracy * 100).toFixed(1)}% accuracy
        <span class="train-info">— Trained on ${formatNumber(report.train_size)} samples, tested on ${formatNumber(report.test_size)}</span>
    `;

    // Model comparison table
    const tbody = document.querySelector('#modelTable tbody');
    tbody.innerHTML = Object.entries(report.all_models).map(([name, m]) => `
        <tr class="${name === report.best_model ? 'best-row' : ''}">
            <td><strong>${name}</strong> ${name === report.best_model ? '<i class="fas fa-crown best-icon"></i>' : ''}</td>
            <td>${(m.accuracy * 100).toFixed(1)}%</td>
            <td>${(m.precision * 100).toFixed(1)}%</td>
            <td>${(m.recall * 100).toFixed(1)}%</td>
            <td>${(m.f1_score * 100).toFixed(1)}%</td>
            <td>${(m.cv_mean * 100).toFixed(1)}%</td>
            <td>±${(m.cv_std * 100).toFixed(1)}%</td>
        </tr>
    `).join('');

    // Accuracy chart
    const modelNames = Object.keys(report.all_models);
    const accuracies = modelNames.map(n => (report.all_models[n].accuracy * 100).toFixed(1));
    const f1Scores = modelNames.map(n => (report.all_models[n].f1_score * 100).toFixed(1));

    if (modelCharts.accuracy) modelCharts.accuracy.destroy();
    modelCharts.accuracy = new Chart(document.getElementById('accuracyChart'), {
        type: 'bar',
        data: {
            labels: modelNames,
            datasets: [{
                label: 'Accuracy %',
                data: accuracies,
                backgroundColor: ['#6366f1', '#8b5cf6', '#06b6d4'],
                borderRadius: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } }
        }
    });

    if (modelCharts.f1) modelCharts.f1.destroy();
    modelCharts.f1 = new Chart(document.getElementById('f1Chart'), {
        type: 'bar',
        data: {
            labels: modelNames,
            datasets: [{
                label: 'F1 Score %',
                data: f1Scores,
                backgroundColor: ['#10b981', '#14b8a6', '#84cc16'],
                borderRadius: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } }
        }
    });

    // Confusion matrix
    const bestModel = report.all_models[report.best_model];
    if (bestModel && bestModel.confusion_matrix) {
        const cm = bestModel.confusion_matrix;
        const classes = report.classes;

        if (modelCharts.confusion) modelCharts.confusion.destroy();
        modelCharts.confusion = new Chart(document.getElementById('confusionChart'), {
            type: 'bar',
            data: {
                labels: classes,
                datasets: classes.map((cls, i) => ({
                    label: `True: ${cls}`,
                    data: cm[i],
                    backgroundColor: ['#6366f1', '#8b5cf6', '#06b6d4'][i % 3] + 'cc',
                    borderRadius: 4,
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { stacked: true, grid: { display: false } },
                    y: { stacked: true, beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });
    }

    // Feature importance
    if (report.feature_importance) {
        const fi = report.feature_importance;
        if (modelCharts.importance) modelCharts.importance.destroy();
        modelCharts.importance = new Chart(document.getElementById('importanceChart'), {
            type: 'bar',
            data: {
                labels: fi.map(f => f[0]),
                datasets: [{
                    label: 'Importance',
                    data: fi.map(f => f[1]),
                    backgroundColor: '#f59e0b',
                    borderRadius: 6,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } }, y: { grid: { display: false } } }
            }
        });
    }

    // Classification report
    const bestReport = report.all_models[report.best_model];
    if (bestReport && bestReport.classification_report) {
        document.getElementById('reportContent').textContent = bestReport.classification_report;
    }

    document.getElementById('modelsResults').scrollIntoView({ behavior: 'smooth' });
}

document.addEventListener('DOMContentLoaded', checkModelStatus);
