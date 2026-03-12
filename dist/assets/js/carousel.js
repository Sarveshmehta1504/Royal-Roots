/* =============================================
   CAROUSEL.JS — Product + Testimonial Carousels
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {
  initProductCarousel();
  initTestimonialCarousel();
});

/* === PRODUCT CAROUSEL === */
function initProductCarousel() {
  const carousel = document.getElementById('productsCarousel');
  const leftBtn = document.getElementById('carouselLeft');
  const rightBtn = document.getElementById('carouselRight');
  if (!carousel) return;

  const scrollAmount = 364;

  if (leftBtn) {
    leftBtn.addEventListener('click', () => {
      carousel.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    });
  }

  if (rightBtn) {
    rightBtn.addEventListener('click', () => {
      carousel.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    });
  }

  // Drag-to-scroll
  let isDown = false, startX, scrollLeft;

  carousel.addEventListener('mousedown', (e) => {
    isDown = true;
    startX = e.pageX - carousel.offsetLeft;
    scrollLeft = carousel.scrollLeft;
    carousel.style.cursor = 'grabbing';
  });

  carousel.addEventListener('mouseleave', () => { isDown = false; carousel.style.cursor = 'grab'; });
  carousel.addEventListener('mouseup', () => { isDown = false; carousel.style.cursor = 'grab'; });

  carousel.addEventListener('mousemove', (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - carousel.offsetLeft;
    carousel.scrollLeft = scrollLeft - (x - startX) * 1.5;
  });

  carousel.style.cursor = 'grab';
}

/* === TESTIMONIAL CAROUSEL (auto-rotate) === */
function initTestimonialCarousel() {
  const cards = document.querySelectorAll('.testimonial-card');
  if (cards.length < 2) return;

  // Only auto-rotate on desktop in single-view mode
  let current = 0;
  let interval;

  const showCard = (index) => {
    cards.forEach((card, i) => {
      card.style.opacity = i === index ? '1' : '0.4';
      card.style.transform = i === index ? 'scale(1)' : 'scale(0.96)';
    });
  };

  const startAutoRotate = () => {
    if (window.innerWidth > 768) return; // Only on mobile
    cards.forEach(c => { c.style.transition = 'opacity 0.5s ease, transform 0.5s ease'; });
    interval = setInterval(() => {
      current = (current + 1) % cards.length;
      showCard(current);
    }, 5000);
  };

  startAutoRotate();
  window.addEventListener('resize', () => {
    clearInterval(interval);
    if (window.innerWidth <= 768) startAutoRotate();
    else cards.forEach(c => { c.style.opacity = '1'; c.style.transform = 'none'; });
  });
}
