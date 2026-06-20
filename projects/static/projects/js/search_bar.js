document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('searchInput');
  const searchResults = document.getElementById('searchResults');
  
  // We retrieve the Django URLs injected into the HTML data attributes.
  const searchUrl = searchInput.dataset.searchUrl;
  const dashboardBaseUrl = searchInput.dataset.dashboardUrl;

  // Event listener that executes every time a character is typed.
  searchInput.addEventListener('input', function() {
    const query = this.value.trim();

    // If the input is empty, hide the list and stop.
    if (query.length === 0) {
      searchResults.style.display = 'none';
      searchResults.innerHTML = '';
      return;
    }

    // Background fetch request in Django.
    fetch(`${searchUrl}?query=${encodeURIComponent(query)}`) // Request
      .then(response => response.json()) // Response
      .then(data => { // List generation
        searchResults.innerHTML = ''; // We clear the previous results.

        if (data.results.length > 0) {
          data.results.forEach(project => {
            const a = document.createElement('a');
            a.href = `${dashboardBaseUrl}${project.id}/`; // Link that leads to the project.
            a.className = 'list-group-item list-group-item-action p-3 border-bottom';
            
            // We insert metadata to disambiguate projects with identical titles.
            a.innerHTML = `
              <div class="d-flex w-100 justify-content-between align-items-center">
                <h6 class="mb-1 fw-bold text-primary">${project.title}</h6>
                <span class="badge bg-light text-muted border">ID: ${project.id}</span>
              </div>
              <p class="mb-1 small text-dark"><span class="text-muted">Directory:</span> 📁 ${project.directory}</p>
              <small class="text-muted fw-bold">👤 Owner: ${project.owner}</small>
            `;
            searchResults.appendChild(a);
          });
        } else {
          // No projects found.
          searchResults.innerHTML = '<div class="list-group-item p-4 text-center text-muted">No public projects found for this query.</div>';
        }
        searchResults.style.display = 'block'; // We make the list visible.
      })
      .catch(error => console.error('Error fetching search results:', error));
  });

  // We hide the dropdown if the user clicks anywhere outside the bar.
  document.addEventListener('click', function(event) {
    if (!searchInput.contains(event.target) && !searchResults.contains(event.target)) {
      searchResults.style.display = 'none';
    }
  });
});