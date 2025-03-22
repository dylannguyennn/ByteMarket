document.addEventListener('DOMContentLoaded', function() {
    const categoryLinks = document.querySelectorAll('.categories .category-item a');

    categoryLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const category = this.getAttribute('href').split('/').pop();
            const mainContent = document.querySelector('main');
            const originalContent = mainContent.innerHTML;

            fetch(`/category/${category}`)
                .then(response => response.text())
                .then(data => {
                    const productsSection = document.querySelector('.products');
                    productsSection.innerHTML = data;
                    const categoryHeader = document.getElementById('category-header');
                    let categoryName = category.charAt(0).toUpperCase() + category.slice(1);
                    
                    switch (category) {
                        case "pdfs":
                            categoryName = "PDFs";
                            break;
                        case "ebooks":
                            categoryName = "eBooks";
                            break;
                        case "egiftcards":
                            categoryName = "eGiftcards";
                            break;
                    }
                    
                    categoryHeader.textContent = categoryName;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    });
});
