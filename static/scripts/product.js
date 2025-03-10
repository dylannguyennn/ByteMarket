document.addEventListener('DOMContentLoaded', () => {
    const addToCartBtn = document.getElementById('add-to-cart');
    
    if (addToCartBtn) {
      addToCartBtn.addEventListener('click', addToCart);
    }
    
    // Function to add item to cart
    async function addToCart(event) {
      // Get product ID from data attribute
      const productId = event.target.getAttribute('data-product-id');
      
      try {
        const response = await fetch('/api/cart/add', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            product_id: productId,
            quantity: 1 // Default to 1, you could add a quantity selector
          })
        });
        
        // Check if response is a redirect to login page (status 401 or 403)
        if (response.status === 401 || response.status === 403) {
          showNotification('Please log in to add items to your cart', 'error');
          // Redirect to login page after a short delay
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
          return;
        }
        
        const data = await response.json();
        
        if (data.success) {
          // Show success message
          showNotification('Product added to cart!', 'success');
          
          // Could update cart icon count here if you have one
          updateCartCount();
        } else {
          showNotification('Error adding product to cart: ' + data.message, 'error');
        }
      } catch (error) {
        console.error('Error:', error);
        showNotification('An error occurred. Please try again.', 'error');
      }
    }
    
    // Function to display notification
    function showNotification(message, type) {
      // Create notification element
      const notification = document.createElement('div');
      notification.className = `notification ${type}`;
      notification.textContent = message;
      
      // Add to DOM
      document.body.appendChild(notification);
      
      // Remove after delay
      setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
          notification.remove();
        }, 500);
      }, 3000);
    }
    
    // Function to update cart count
    async function updateCartCount() {
      try {
        const response = await fetch('/api/cart');
        
        // Check if response is a redirect to login page (status 401 or 403)
        if (response.status === 401 || response.status === 403) {
          // User is not logged in, don't show error, just don't update cart count
          return;
        }
        
        const data = await response.json();
        
        // If you have a cart icon with a count badge, update it
        const cartItems = data.cart_items || [];
        const totalItems = cartItems.reduce((sum, item) => sum + item.quantity, 0);
        
        // Update any cart count displays
        const cartCountElements = document.querySelectorAll('.cart-count');
        cartCountElements.forEach(element => {
          element.textContent = totalItems;
        });
      } catch (error) {
        console.error('Error updating cart count:', error);
      }
    }
    
    // Initialize cart count on page load
    updateCartCount();
  });
