const API_BASE = 'http://localhost:5000';

const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const resultsDiv = document.getElementById('results');
const statsDiv = document.getElementById('stats');

// Load stats on page load
loadStats();

searchBtn.addEventListener('click', () => {
    const query = searchInput.value.trim();
    if (query) {
        searchConcepts(query);
    }
});

searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        searchBtn.click();
    }
});

async function searchConcepts(query) {
    resultsDiv.innerHTML = '<p>Searching...</p>';

    try {
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.error) {
            resultsDiv.innerHTML = `<p>Error: ${data.error}</p>`;
            return;
        }

        if (data.length === 0) {
            resultsDiv.innerHTML = '<p>No concepts found.</p>';
            return;
        }

        let html = '';
        data.forEach(concept => {
            const domains = concept.domains ? JSON.parse(concept.domains).join(', ') : '';
            html += `
                <div class="concept-card">
                    <h3>${concept.concept_name}</h3>
                    <div class="domains">${domains}</div>
                    <div class="definition">${concept.definition || ''}</div>
                    <div class="source">Published: ${concept.source_date || 'Unknown'}</div>
                </div>
            `;
        });
        resultsDiv.innerHTML = html;

    } catch (error) {
        resultsDiv.innerHTML = `<p>Error: ${error.message}</p>`;
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();
        statsDiv.innerHTML = `Total concepts indexed: <strong>${data.total_concepts || 0}</strong>`;
    } catch (error) {
        statsDiv.innerHTML = 'Stats unavailable.';
    }
}
