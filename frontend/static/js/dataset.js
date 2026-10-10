// Dataset Explorer - Table with search, filter, pagination

let currentPage = 1;
let totalPages = 1;
let searchTimeout = null;

async function loadFilters() {
    try {
        const data = await apiGet('/api/data/filters');
        if (data.error) return;

        const deptSelect = document.getElementById('deptFilter');
        data.departments.forEach(d => {
            const opt = document.createElement('option');
            opt.value = d;
            opt.textContent = d;
            deptSelect.appendChild(opt);
        });

        const sevSelect = document.getElementById('sevFilter');
        data.severities.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s;
            opt.textContent = s;
            sevSelect.appendChild(opt);
        });
    } catch (err) {
        console.error('Failed to load filters', err);
    }
}

async function loadRecords() {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '<tr><td colspan="15" class="loading-cell"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>';

    const search = document.getElementById('searchInput').value;
    const dept = document.getElementById('deptFilter').value;
    const sev = document.getElementById('sevFilter').value;
    const perPage = document.getElementById('perPage').value;

    try {
        const params = new URLSearchParams({
            page: currentPage,
            per_page: perPage,
            search: search,
            department: dept,
            severity: sev,
        });

        const data = await apiGet('/api/data/records?' + params.toString());
        if (data.error) {
            tbody.innerHTML = `<tr><td colspan="15" class="loading-cell error">${data.error}</td></tr>`;
            return;
        }

        totalPages = data.total_pages;

        if (data.records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="15" class="loading-cell">No records found</td></tr>';
            document.getElementById('pagination').innerHTML = '';
            return;
        }

        tbody.innerHTML = data.records.map(r => `
            <tr>
                <td>${r.patient_id}</td>
                <td>${r.age}</td>
                <td><span class="badge gender-${r.gender.toLowerCase()}">${r.gender}</span></td>
                <td>${r.symptoms}</td>
                <td>${r.temperature}°F</td>
                <td>${r.duration_days}d</td>
                <td>${r.bp_systolic}</td>
                <td>${r.bp_diastolic}</td>
                <td>${r.heart_rate}</td>
                <td>${r.oxygen_saturation}%</td>
                <td>${r.pain_level}/10</td>
                <td><span class="badge severity-${r.symptom_severity.toLowerCase()}">${r.symptom_severity}</span></td>
                <td><span class="badge ${r.chronic_condition === 'Yes' ? 'chronic-yes' : 'chronic-no'}">${r.chronic_condition}</span></td>
                <td>${r.department}</td>
            </tr>
        `).join('');

        renderPagination(data.page, data.total_pages, data.total);
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="15" class="loading-cell error">Failed to load data</td></tr>`;
        console.error(err);
    }
}

function renderPagination(page, pages, total) {
    const container = document.getElementById('pagination');
    let html = `<span class="page-info">Page ${page} of ${pages} (${formatNumber(total)} records)</span>`;

    html += '<div class="page-buttons">';
    if (page > 1) {
        html += `<button class="page-btn" onclick="goToPage(${page - 1})"><i class="fas fa-chevron-left"></i></button>`;
    }

    const start = Math.max(1, page - 3);
    const end = Math.min(pages, page + 3);

    for (let i = start; i <= end; i++) {
        html += `<button class="page-btn ${i === page ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
    }

    if (page < pages) {
        html += `<button class="page-btn" onclick="goToPage(${page + 1})"><i class="fas fa-chevron-right"></i></button>`;
    }
    html += '</div>';

    container.innerHTML = html;
}

function goToPage(page) {
    currentPage = page;
    loadRecords();
}

function debouncedSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        currentPage = 1;
        loadRecords();
    }, 300);
}

document.addEventListener('DOMContentLoaded', () => {
    loadFilters();
    loadRecords();
});
