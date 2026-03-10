/* =============================================
   HERO SLIDER — Auto-rotating background crossfade
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {
  const slides = document.querySelectorAll('.hero__slide');
  const dots = document.querySelectorAll('.hero__dot');
  if (!slides.length) return;

  let current = 0;
  const total = slides.length;
  const interval = 5000; /* 5 seconds per slide */
  let timer;

  function goToSlide(index) {
    slides[current].classList.remove('active');
    dots[current] && dots[current].classList.remove('active');

    current = index % total;

    slides[current].classList.add('active');
    dots[current] && dots[current].classList.add('active');
  }

  function nextSlide() {
    goToSlide(current + 1);
  }

  function startAutoPlay() {
    timer = setInterval(nextSlide, interval);
  }

  function resetAutoPlay() {
    clearInterval(timer);
    startAutoPlay();
  }

  /* Dot click handlers */
  dots.forEach(dot => {
    dot.addEventListener('click', () => {
      const target = parseInt(dot.getAttribute('data-slide'), 10);
      if (target !== current) {
        goToSlide(target);
        resetAutoPlay();
      }
    });
  });

  /* Pause on hover, resume on leave */
  const hero = document.querySelector('.hero');
  if (hero) {
    hero.addEventListener('mouseenter', () => clearInterval(timer));
    hero.addEventListener('mouseleave', startAutoPlay);
  }

  startAutoPlay();
});
