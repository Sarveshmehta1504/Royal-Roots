/* =============================================
   WHATSAPP.JS — Floating WhatsApp + Call Buttons
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {
  const buttons = document.querySelectorAll('.floating-btn');
  if (!buttons.length) return;

  const checkVisibility = () => {
    const show = window.scrollY > window.innerHeight * 0.4;
    buttons.forEach(btn => {
      if (show) {
        btn.classList.add('visible');
      } else {
        btn.classList.remove('visible');
      }
    });
  };

  window.addEventListener('scroll', checkVisibility, { passive: true });
  checkVisibility(); // Initial check

  // Form pill toggles (used on contact/lead forms)
  document.querySelectorAll('.pill-option').forEach(pill => {
    pill.addEventListener('click', () => {
      pill.classList.toggle('active');
    });
  });
});
