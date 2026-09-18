// Velin theme — global scripts.

// Variant selection on the product page: match selected options to a
// variant and update the hidden id input, price, and button state.
(function () {
  const productJsonEl = document.querySelector('[data-product-json]');
  const form = document.getElementById('ProductForm');
  if (!productJsonEl || !form) return;

  const product = JSON.parse(productJsonEl.textContent);
  const selects = form.querySelectorAll('[data-option-index]');
  const variantInput = form.querySelector('[data-variant-id]');
  const priceEl = document.getElementById('ProductPrice');
  const submitBtn = form.querySelector('[type="submit"]');

  function formatMoney(cents) {
    return (cents / 100).toLocaleString(undefined, {
      style: 'currency',
      currency: window.Shopify && Shopify.currency ? Shopify.currency.active : 'USD',
    });
  }

  function onOptionChange() {
    const selected = Array.from(selects).map((s) => s.value);
    const variant = product.variants.find((v) =>
      selected.every((value, i) => v[`option${i + 1}`] === value)
    );

    if (!variant) {
      submitBtn.disabled = true;
      return;
    }

    variantInput.value = variant.id;
    submitBtn.disabled = !variant.available;
    if (priceEl) priceEl.textContent = formatMoney(variant.price);
  }

  selects.forEach((s) => s.addEventListener('change', onOptionChange));
})();

// Quick add-to-cart from product cards.
(function () {
  const buttons = document.querySelectorAll('[data-quick-add]');
  if (!buttons.length) return;

  buttons.forEach((btn) => {
    btn.addEventListener('click', async () => {
      btn.disabled = true;
      try {
        const res = await fetch('/cart/add.js', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: Number(btn.dataset.quickAdd), quantity: 1 }),
        });
        if (!res.ok) throw new Error('Add to cart failed');

        const cartRes = await fetch('/cart.js');
        const cart = await cartRes.json();

        if (window.VelinCartDrawer) {
          await window.VelinCartDrawer.refresh(cart);
          window.VelinCartDrawer.open();
        } else {
          document.querySelectorAll('[data-cart-count]').forEach((el) => {
            el.textContent = cart.item_count;
            el.classList.toggle('is-empty', cart.item_count === 0);
          });
        }
      } catch (e) {
        window.location.href = '/cart';
      } finally {
        btn.disabled = false;
      }
    });
  });
})();

// Video stories carousel dots.
(function () {
  const track = document.querySelector('[data-carousel]');
  const dotsWrap = document.querySelector('[data-carousel-dots]');
  if (!track || !dotsWrap) return;

  const cards = track.querySelectorAll('.story-card');
  if (cards.length < 2) return;

  cards.forEach((card, i) => {
    const dot = document.createElement('button');
    dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
    if (i === 0) dot.classList.add('is-active');
    dot.addEventListener('click', () => {
      card.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    });
    dotsWrap.appendChild(dot);
  });

  const dots = dotsWrap.querySelectorAll('button');

  track.addEventListener(
    'scroll',
    () => {
      const center = track.scrollLeft + track.clientWidth / 2;
      let closest = 0;
      let min = Infinity;
      cards.forEach((card, i) => {
        const cardCenter = card.offsetLeft + card.offsetWidth / 2;
        const dist = Math.abs(cardCenter - center);
        if (dist < min) {
          min = dist;
          closest = i;
        }
      });
      dots.forEach((d, i) => d.classList.toggle('is-active', i === closest));
    },
    { passive: true }
  );
})();
