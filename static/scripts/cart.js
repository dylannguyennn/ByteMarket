document.addEventListener('DOMContentLoaded', () => {
  const cartItemsContainer = document.getElementById('cart-items');
  const checkoutButton = document.getElementById('checkout-button');
  
  // Fetch and display cart items
  async function loadCartItems() {
    try {
      const response = await fetch('/api/cart');
      
      // Check if response is a redirect to login page (status 401 or 403)
      if (response.status === 401 || response.status === 403) {
        cartItemsContainer.innerHTML = '<p>Please <a href="/login">log in</a> to view your cart.</p>';
        if (checkoutButton) {
          checkoutButton.disabled = true;
        }
        return;
      }
      
      const data = await response.json();
      
      if (data.success) {
        renderCartItems(data.cart_items);
        updateCheckoutButton(data.cart_items);
      } else {
        cartItemsContainer.innerHTML = '<p>Error loading cart items.</p>';
      }
    } catch (error) {
      console.error('Error:', error);
      cartItemsContainer.innerHTML = '<p>Error loading cart items. Please try again.</p>';
    }
  }
  
  // Render cart items to the page
  function renderCartItems(items) {
    if (!items || items.length === 0) {
      cartItemsContainer.innerHTML = '<p>Your cart is empty.</p>';
      return;
    }
    
    let totalPrice = 0;
    let cartHTML = '';
    
    items.forEach(item => {
      totalPrice += item.total;
      
      cartHTML += `
        <div class="cart-item" data-item-id="${item.id}">
          <div class="cart-item-image">
            <img src="${item.image_url || 'https://via.placeholder.com/100x100'}" alt="${item.name}">
          </div>
          <div class="cart-item-info">
            <h3>${item.name}</h3>
            <p>$${item.price.toFixed(2)}</p>
          </div>
          <div class="cart-item-quantity">
            <button class="quantity-btn decrease">-</button>
            <span class="quantity">${item.quantity}</span>
            <button class="quantity-btn increase">+</button>
          </div>
          <div class="cart-item-total">
            $${item.total.toFixed(2)}
          </div>
          <button class="remove-item-btn">✕</button>
        </div>
      `;
    });
    
    // Add cart summary
    cartHTML += `
      <div class="cart-summary">
        <div class="cart-summary-row">
          <span>Subtotal:</span>
          <span>$${totalPrice.toFixed(2)}</span>
        </div>
        <div class="cart-summary-row">
          <span>Total:</span>
          <span>$${totalPrice.toFixed(2)}</span>
        </div>
      </div>
    `;
    
    cartItemsContainer.innerHTML = cartHTML;
    
    // Add event listeners for quantity buttons and remove buttons
    addCartItemEventListeners();
  }
  
  // Update checkout button state
  function updateCheckoutButton(items) {
    if (!items || items.length === 0) {
      checkoutButton.disabled = true;
    } else {
      checkoutButton.disabled = false;
    }
  }
  
  // Add event listeners to cart item buttons
  function addCartItemEventListeners() {
    // Implementation for quantity buttons and remove buttons
    // (This would be additional code to handle these actions)
  }
  
  // Load cart items when page loads
  if (cartItemsContainer) {
    loadCartItems();
  }
});
