document.addEventListener("DOMContentLoaded", function () {
  let cart = JSON.parse(localStorage.getItem("cart")) || [];

  const cartItemsContainer = document.getElementById("cart-items");
  const cartCount = document.getElementById("cart-count");
  const checkoutButton = document.getElementById("checkout-button");

  // Function to render cart items
  function renderCart() {
    cartItemsContainer.innerHTML = "";
    if (cart.length === 0) {
      cartItemsContainer.innerHTML = "<p>Your cart is empty.</p>";
      checkoutButton.disabled = true;
      return;
    }

    cart.forEach((item, index) => {
      const cartItem = document.createElement("div");
      cartItem.classList.add("cart-item");

      cartItem.innerHTML = `
              <img src="${
                item.image
              }" alt="Product Image" class="cart-item-image" />
              <div class="cart-item-details">
                  <h3>${item.title}</h3>
                  <p>${item.description}</p>
              </div>
              <span class="cart-item-price">$${item.price.toFixed(2)}</span>
              <button class="remove-item-button" data-index="${index}">Remove</button>
          `;

      cartItemsContainer.appendChild(cartItem);
    });

    cartCount.textContent = cart.length;
    checkoutButton.disabled = false;

    // Attach event listeners to remove buttons
    document.querySelectorAll(".remove-item-button").forEach((btn) => {
      btn.addEventListener("click", function () {
        const index = this.dataset.index;
        removeFromCart(index);
      });
    });
  }

  // Function to remove item from cart
  function removeFromCart(index) {
    cart.splice(index, 1);
    localStorage.setItem("cart", JSON.stringify(cart));
    renderCart();
  }

  // Initial render
  renderCart();
});
