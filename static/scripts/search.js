document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('.search-container');
    const searchInput = searchForm.querySelector('input');
    const searchButton = searchForm.querySelector('.search-button');
    const mainContent = document.querySelector('main');
    const originalContent = mainContent.innerHTML; // Store original content
    
    function performSearch(query) {
        // Show loading state
        mainContent.innerHTML = '<div class="loading">Searching...</div>';
        
        // Fetch search results
        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displaySearchResults(data.results, query);
                } else {
                    mainContent.innerHTML = `<div class="search-error">${data.message}</div>`;
                }
            })
            .catch(error => {
                console.error('Search error:', error);
                mainContent.innerHTML = '<div class="search-error">An error occurred while searching. Please try again.</div>';
            });
    }
    
    // Display search results
    function displaySearchResults(results, query) {
        if (results.length === 0) {
            mainContent.innerHTML = `
                <section class="search-results">
                    <div class="products-container">
                        <h3>Search Results for "${query}"</h3>
                        <p>No products found matching your search.</p>
                        <button class="clear-search-btn">Back to Home</button>
                    </div>
                </section>
            `;
        } else {
            let resultsHTML = `
                <section class="search-results">
                    <div class="products-container">
                        <h3>Search Results for "${query}" (${results.length} items)</h3>
                        <button class="clear-search-btn">Back to Home</button>
                        <div class="placeholder-products">
            `;
            
            results.forEach(product => {
                resultsHTML += `
                    <a href="/product/${product.id}">
                        <div class="placeholder-product">
                            <img src="/static/${product.image_path}" alt="${product.name}">
                            <div class="product-info">
                                <h4>${product.name}</h4>
                                <p class="product-price">$${product.price.toFixed(2)}</p>
                                <p class="product-description">${product.description}</p>
                            </div>
                        </div>
                    </a>
                `;
            });
            
            resultsHTML += `
                        </div>
                    </div>
                </section>
            `;
            
            mainContent.innerHTML = resultsHTML;
        }
        
        // Back to Home button
        const clearSearchBtn = document.querySelector('.clear-search-btn');
        if (clearSearchBtn) {
            clearSearchBtn.addEventListener('click', function() {
                mainContent.innerHTML = originalContent;
                searchInput.value = '';
            });
        }
    }
    
    // Event listeners for search
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            performSearch(query);
        }
    });
    
    searchButton.addEventListener('click', function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            performSearch(query);
        }
    });
});