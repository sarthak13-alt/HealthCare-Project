// Prediction Page - ML Model Interaction

async function checkModelStatus() {
    try {
        const data = await apiGet('/api/ml/status');
        const banner = document.getElementById('modelStatus');

        if (data.trained) {
            banner.innerHTML = `
                <i class="fas fa-check-circle"></i>
                Model trained: <strong>${data.info.best_model}</strong> (Accuracy: ${(data.info.best_accuracy * 100).toFixed(1)}%)
            `;
            banner.classList.add('success');
        } else {
            banner.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                Model not trained yet. Go to <a href="/models">Models page</a> to train.
            `;
            banner.classList.add('warning');
        }
    } catch (err) {
        console.error(err);
    }
}

async function loadSymptoms() {
    try {
        const data = await apiGet('/api/data/filters');
        if (data.error) return;

        const select = document.getElementById('predSymptoms');
        select.innerHTML = data.symptoms.map(s => `<option value="${s}">${s}</option>`).join('');
    } catch (err) {
        console.error(err);
    }
}

async function makePrediction(event) {
    event.preventDefault();

    const form = document.getElementById('predictionForm');
    const formData = new FormData(form);
    const record = {};

    formData.forEach((value, key) => {
        record[key] = isNaN(value) || value === '' ? value : Number(value);
    });

    const btn = document.getElementById('predictBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Predicting...';

    try {
        const result = await apiPost('/api/predict', record);

        if (result.error) {
            showToast(result.error, 'error');
            return;
        }

        displayResult(result);
        showToast('Prediction complete!', 'success');
    } catch (err) {
        showToast('Prediction failed', 'error');
        console.error(err);
    }

    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-brain"></i> Predict Severity';
}

function displayResult(result) {
    const card = document.getElementById('resultCard');
    card.style.display = 'block';

    const dept = result.department || result.severity || 'Unknown';
    document.getElementById('resultSeverity').innerHTML = `
        <div class="severity-badge">
            <i class="fas fa-hospital"></i>
            ${dept}
        </div>
    `;

    document.getElementById('resultConfidence').innerHTML = `
        <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${result.confidence * 100}%"></div>
            <span>Confidence: ${(result.confidence * 100).toFixed(1)}%</span>
        </div>
    `;

    const probs = result.probabilities || {};
    document.getElementById('probabilities').innerHTML = `
        <h4>Department Probabilities</h4>
        ${Object.entries(probs).map(([d, prob]) => `
            <div class="prob-row">
                <span class="prob-label">${d}</span>
                <div class="prob-bar">
                    <div class="prob-fill" style="width: ${prob * 100}%"></div>
                </div>
                <span class="prob-value">${(prob * 100).toFixed(1)}%</span>
            </div>
        `).join('')}
    `;

    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

document.addEventListener('DOMContentLoaded', () => {
    checkModelStatus();
    loadSymptoms();
});
