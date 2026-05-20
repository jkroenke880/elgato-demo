function getCart() {
  return JSON.parse(localStorage.getItem('elgato_cart') || '[]');
}

function saveCart(cart) {
  localStorage.setItem('elgato_cart', JSON.stringify(cart));
}

function addToCart(product, quantity) {
  var cart = getCart();
  var existing = cart.find(function(item) { return item.product_id === product.product_id; });
  if (existing) {
    existing.quantity += quantity;
  } else {
    cart.push({
      product_id: product.product_id,
      name: product.name,
      price: product.price,
      category: product.category,
      brand: product.brand,
      sku: product.sku,
      quantity: quantity
    });
  }
  saveCart(cart);
  updateCartBadge();
}

function removeFromCart(product_id) {
  saveCart(getCart().filter(function(item) { return item.product_id !== product_id; }));
  updateCartBadge();
}

function clearCart() {
  localStorage.removeItem('elgato_cart');
  updateCartBadge();
}

function getCartTotal() {
  return getCart().reduce(function(sum, item) { return sum + item.price * item.quantity; }, 0);
}

function getCartCount() {
  return getCart().reduce(function(sum, item) { return sum + item.quantity; }, 0);
}

function updateCartBadge() {
  var el = document.getElementById('cart-count');
  if (el) {
    var count = getCartCount();
    el.textContent = count;
    el.style.display = count > 0 ? 'inline-block' : 'none';
  }
}

function generateId() {
  return Math.random().toString(36).substring(2, 10).toUpperCase();
}
