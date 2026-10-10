// Dashboard - Load and render all charts

const COLORS = {
    primary: '#6366f1',
    secondary: '#8b5cf6',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#06b6d4',
    pink: '#ec4899',
    teal: '#14b8a6',
    orange: '#f97316',
    palette: ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899', '#14b8a6', '#f97316', '#84cc16']
};

let charts = {};

async function loadDashboard() {
    try {
        const data = await apiGet('/api/data/summary');
        if (data.error) {
            showToast(data.error, 'error');
            return;
        }

        renderStats(data.totals);
        renderDeptChart(data.departments);
        renderSeverityChart(data.severity);
        renderGenderChart(data.gender);
        renderAgeChart(data.age_groups);
        renderVitalsChart(data.vitals_by_dept);
        renderChronicChart(data.chronic);
        renderRiskChart(data.risk_levels);
        renderSevDeptChart(data.severity_by_dept);
        renderSymptomsChart(data.top_symptoms);
        renderBpChart(data.bp_categories);
        renderFeverChart(data.fever);

    } catch (err) {
        showToast('Failed to load dashboard data', 'error');
        console.error(err);
    }
}

function renderStats(totals) {
    const row = document.getElementById('stats-row');
    row.innerHTML = `
        <div class="stat-box">
            <div class="stat-icon"><i class="fas fa-users"></i></div>
            <div class="stat-value">${formatNumber(totals.total_patients)}</div>
            <div class="stat-label">Total Patients</div>
        </div>
        <div class="stat-box">
            <div class="stat-icon"><i class="fas fa-user-md"></i></div>
            <div class="stat-value">${formatNumber(totals.chronic_count)}</div>
            <div class="stat-label">Chronic Cases</div>
        </div>
        <div class="stat-box">
            <div class="stat-icon"><i class="fas fa-thermometer-full"></i></div>
            <div class="stat-value">${formatNumber(totals.fever_count)}</div>
            <div class="stat-label">Fever Cases</div>
        </div>
        <div class="stat-box">
            <div class="stat-icon"><i class="fas fa-birthday-cake"></i></div>
            <div class="stat-value">${totals.avg_age}</div>
            <div class="stat-label">Avg Age</div>
        </div>
        <div class="stat-box">
            <div class="stat-icon"><i class="fas fa-heart"></i></div>
            <div class="stat-value">${totals.avg_hr}</div>
            <div class="stat-label">Avg Heart Rate</div>
        </div>
        <div class="stat-box">
            <div class="stat-icon"><i class="fas fa-lungs"></i></div>
            <div class="stat-value">${totals.avg_spo2}%</div>
            <div class="stat-label">Avg SpO2</div>
        </div>
    `;
}

function renderDeptChart(data) {
    const ctx = document.getElementById('deptChart').getContext('2d');
    charts.dept = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.department),
            datasets: [{
                label: 'Patients',
                data: data.map(d => d.count),
                backgroundColor: COLORS.palette,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } }
        }
    });
}

function renderSeverityChart(data) {
    const ctx = document.getElementById('severityChart').getContext('2d');
    charts.severity = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.symptom_severity),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } },
            cutout: '60%',
        }
    });
}

function renderGenderChart(data) {
    const ctx = document.getElementById('genderChart').getContext('2d');
    charts.gender = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(d => d.gender),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: ['#6366f1', '#ec4899'],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

function renderAgeChart(data) {
    const ctx = document.getElementById('ageChart').getContext('2d');
    charts.age = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.age_group),
            datasets: [{
                label: 'Patients',
                data: data.map(d => d.count),
                backgroundColor: COLORS.info,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } }
        }
    });
}

function renderVitalsChart(data) {
    const ctx = document.getElementById('vitalsChart').getContext('2d');
    charts.vitals = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.department),
            datasets: [
                { label: 'Avg Temp (F)', data: data.map(d => d.avg_temp), borderColor: COLORS.danger, backgroundColor: COLORS.danger + '20', fill: true, tension: 0.4 },
                { label: 'Avg Heart Rate', data: data.map(d => d.avg_hr), borderColor: COLORS.primary, backgroundColor: COLORS.primary + '20', fill: true, tension: 0.4 },
                { label: 'Avg SpO2', data: data.map(d => d.avg_spo2), borderColor: COLORS.success, backgroundColor: COLORS.success + '20', fill: true, tension: 0.4 },
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } }
        }
    });
}

function renderChronicChart(data) {
    const ctx = document.getElementById('chronicChart').getContext('2d');
    charts.chronic = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.chronic_condition),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: [COLORS.success, COLORS.danger],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } },
            cutout: '60%',
        }
    });
}

function renderRiskChart(data) {
    const ctx = document.getElementById('riskChart').getContext('2d');
    charts.risk = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.risk_level),
            datasets: [{
                label: 'Patients',
                data: data.map(d => d.count),
                backgroundColor: [COLORS.success, COLORS.warning, COLORS.orange, COLORS.danger],
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } }
        }
    });
}

function renderSevDeptChart(data) {
    const departments = [...new Set(data.map(d => d.department))];
    const severities = ['Mild', 'Moderate', 'Severe'];
    const colors = { 'Mild': COLORS.success, 'Moderate': COLORS.warning, 'Severe': COLORS.danger };

    const datasets = severities.map(sev => ({
        label: sev,
        data: departments.map(dept => {
            const item = data.find(d => d.department === dept && d.symptom_severity === sev);
            return item ? item.count : 0;
        }),
        backgroundColor: colors[sev],
        borderRadius: 4,
    }));

    const ctx = document.getElementById('sevDeptChart').getContext('2d');
    charts.sevDept = new Chart(ctx, {
        type: 'bar',
        data: { labels: departments, datasets },
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

function renderSymptomsChart(data) {
    const ctx = document.getElementById('symptomsChart').getContext('2d');
    charts.symptoms = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.symptoms),
            datasets: [{
                label: 'Cases',
                data: data.map(d => d.count),
                backgroundColor: COLORS.secondary,
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

function renderBpChart(data) {
    const ctx = document.getElementById('bpChart').getContext('2d');
    charts.bp = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.bp_category),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: [COLORS.success, COLORS.info, COLORS.warning, COLORS.danger],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } },
            cutout: '55%',
        }
    });
}

function renderFeverChart(data) {
    const ctx = document.getElementById('feverChart').getContext('2d');
    charts.fever = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(d => d.has_fever === 1 ? 'Has Fever' : 'No Fever'),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: [COLORS.danger, COLORS.success],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

// Load on page ready
document.addEventListener('DOMContentLoaded', loadDashboard);
