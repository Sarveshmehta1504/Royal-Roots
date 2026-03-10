/* =============================================
   COUNTER.JS — Animated Stat Counters
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {
  const counters = document.querySelectorAll('[data-count-target]');
  if (!counters.length) return;

  let animated = false;

  const animateCounter = (el) => {
    const target = parseFloat(el.dataset.countTarget);
    const suffix = el.dataset.countSuffix || '';
    const prefix = el.dataset.countPrefix || '';
    const isDecimal = el.dataset.countDecimal === 'true';
    const duration = 2200;
    const start = performance.now();

    const update = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      const value = ease * target;

      if (isDecimal) {
        el.textContent = prefix + value.toFixed(1) + suffix;
      } else {
        el.textContent = prefix + Math.floor(value).toLocaleString('en-IN') + suffix;
      }

      if (progress < 1) requestAnimationFrame(update);
    };

    requestAnimationFrame(update);
  };

  const section = document.getElementById('stats');
  if (!section) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !animated) {
        animated = true;
        counters.forEach(el => animateCounter(el));
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  observer.observe(section);
});
