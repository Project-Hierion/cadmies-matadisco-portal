/**
 * CADMIES-Matadisco Portal — Frontend Application
 *
 * This module handles the user interface for searching and displaying
 * CADMIES concept records from the Matadisco network.
 *
 * Functions:
 *   searchConcepts(query)  - Queries the API for concepts matching a search term.
 *   loadStats()            - Fetches and displays the total number of indexed concepts.
 *
 * Dependencies:
 *   None (vanilla JavaScript)
 */

const API_BASE = 'http://localhost:5000';

const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const resultsDiv = document.getElementById('results');
const statsDiv = document.getElementById('stats');

// Load statistics on initial page load
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

/**
 * Search for concepts matching a query string.
 *
 * Sends a GET request to the /search endpoint and renders the results
 * as a list of concept cards in the results section.
 *
 * @param {string} query - The search term to query the API with.
 */
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

/**
 * Load and display statistics about the index.
 *
 * Fetches the total concept count from the /stats endpoint and updates
 * the stats section of the page.
 */
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();
        statsDiv.innerHTML = `Total concepts indexed: <strong>${data.total_concepts || 0}</strong>`;
    } catch (error) {
        statsDiv.innerHTML = 'Stats unavailable.';
    }
}
