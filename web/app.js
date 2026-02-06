const API_URL = 'http://127.0.0.1:8000/api';
let authHeader = '';
let currentChart = null;
let currentDatasetId = null;

async function handleLogin() {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    
    if (!user || !pass) return;

    authHeader = 'Basic ' + btoa(user + ':' + pass);
    
    try {
        const response = await fetch(`${API_URL}/history/`, {
            headers: { 'Authorization': authHeader }
        });

        if (response.ok) {
            document.getElementById('login-screen').classList.add('hidden');
            document.getElementById('main-app').classList.remove('hidden');
            loadHistory();
        } else {
            document.getElementById('login-error').innerText = 'Invalid credentials';
        }
    } catch (err) {
        document.getElementById('login-error').innerText = 'Backend connection failed';
    }
}

async function loadHistory() {
    try {
        const response = await fetch(`${API_URL}/history/`, {
            headers: { 'Authorization': authHeader }
        });
        const data = await response.json();
        const list = document.getElementById('history-list');
        list.innerHTML = '';
        
        data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'history-item';
            div.innerHTML = `
                <div>
                    <div style="font-weight: 600;">${item.filename}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted)">${new Date(item.upload_date).toLocaleString()}</div>
                </div>
                <button onclick="viewDataset(${item.id})" class="btn" style="padding: 0.25rem 0.75rem; font-size: 0.7rem; background: rgba(255,255,255,0.1); color: white;">View</button>
            `;
            list.appendChild(div);
        });
    } catch (err) {
        console.error('History load failed', err);
    }
}

async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const label = document.getElementById('drop-area');
    label.innerHTML = '<span>Uploading...</span>';

    try {
        const response = await fetch(`${API_URL}/upload/`, {
            method: 'POST',
            headers: { 'Authorization': authHeader },
            body: formData
        });

        const data = await response.json();
        if (response.ok) {
            label.innerHTML = '<span>Success!</span>';
            setTimeout(() => label.innerHTML = '<span>Drop CSV or click to browse</span>', 2000);
            loadHistory();
            renderDashboard(data);
        } else {
            alert(data.error || 'Upload failed');
            label.innerHTML = '<span>Error! Try again.</span>';
        }
    } catch (err) {
        console.error('Upload failed', err);
        label.innerHTML = '<span>Connection error</span>';
    }
}

async function viewDataset(id) {
    try {
        // Find dataset in history if already loaded or fetch specific (we'll fetch history again to get full data for now, 
        // or we could add a "detail" endpoint. But Upload endpoint returns full data. 
        // History endpoint returns last 5 with items.
        const response = await fetch(`${API_URL}/history/`, {
            headers: { 'Authorization': authHeader }
        });
        const data = await response.json();
        const dataset = data.find(d => d.id === id);
        if (dataset) renderDashboard(dataset);
    } catch (err) {
        console.error('View failed', err);
    }
}

function renderDashboard(data) {
    currentDatasetId = data.id;
    document.getElementById('no-data').classList.add('hidden');
    document.getElementById('data-display').classList.remove('hidden');

    // Stats
    document.getElementById('stat-count').innerText = data.summary_stats.total_count;
    document.getElementById('stat-flow').innerText = data.summary_stats.avg_flowrate.toFixed(2);
    document.getElementById('stat-pressure').innerText = data.summary_stats.avg_pressure.toFixed(2);
    document.getElementById('stat-temp').innerText = data.summary_stats.avg_temperature.toFixed(2);

    // Table
    const tbody = document.querySelector('#data-table tbody');
    tbody.innerHTML = '';
    data.items.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.name}</td>
            <td>${item.equipment_type}</td>
            <td>${item.flowrate}</td>
            <td>${item.pressure}</td>
            <td>${item.temperature}</td>
        `;
        tbody.appendChild(tr);
    });

    // Chart
    const ctx = document.getElementById('typeChart').getContext('2d');
    if (currentChart) currentChart.destroy();
    
    currentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data.summary_stats.type_distribution),
            datasets: [{
                data: Object.values(data.summary_stats.type_distribution),
                backgroundColor: [
                    '#4f46e5', '#818cf8', '#c084fc', '#e879f9', '#f472b6', '#fb7185'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#f8fafc' }
                }
            }
        }
    });

    // PDF Export
    document.getElementById('download-pdf').onclick = () => {
        window.open(`${API_URL}/report/${data.id}/?auth=${btoa('admin:admin123')}`, '_blank');
        // Note: For simplicity in demo, I might just use a direct link if I can't pass headers easily to window.open
        // I'll adjust the view to allow token/auth in query for the PDF if needed, or just fetch and blob.
    };
}

// Adjust PDF download to handle auth better
document.getElementById('download-pdf').onclick = async () => {
    if (!currentDatasetId) return;
    try {
        const response = await fetch(`${API_URL}/report/${currentDatasetId}/`, {
            headers: { 'Authorization': authHeader }
        });
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${currentDatasetId}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
    } catch (err) {
        console.error('PDF download failed', err);
    }
};
