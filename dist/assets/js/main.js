/* =============================================
   MAIN.JS — Navbar, Scroll, Initialization
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initMobileMenu();
  initProductsDropdown();
  initSmoothScroll();
  initActiveNavTracking();
});

/* === STICKY NAVBAR === */
function initNavbar() {
  const navbar = document.getElementById('navbar');
  if (!navbar) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 80) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }, { passive: true });
}

/* === MOBILE MENU === */
function initMobileMenu() {
  const hamburger = document.getElementById('hamburger');
  const mobileNav = document.getElementById('mobileNav');
  if (!hamburger || !mobileNav) return;

  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    mobileNav.classList.toggle('open');
    document.body.style.overflow = mobileNav.classList.contains('open') ? 'hidden' : '';
  });

  // Close on link click
  mobileNav.querySelectorAll('a[href]').forEach(link => {
    link.addEventListener('click', () => {
      hamburger.classList.remove('active');
      mobileNav.classList.remove('open');
      document.body.style.overflow = '';
    });
  });

  // Close button click
  const closeBtn = document.getElementById('mobileNavClose');
  if (closeBtn) {
    console.log('Mobile nav close button found');
    closeBtn.addEventListener('click', () => {
      console.log('Mobile nav close clicked');
      hamburger.classList.remove('active');
      mobileNav.classList.remove('open');
      document.body.style.overflow = '';
    });
  } else {
    console.warn('Mobile nav close button NOT found');
  }

  // Mobile products accordion
  const accordionToggle = document.getElementById('mobileProductsToggle');
  const accordionSub = document.getElementById('mobileProductsSub');

  if (accordionToggle && accordionSub) {
    accordionToggle.addEventListener('click', () => {
      accordionToggle.classList.toggle('open');
      accordionSub.classList.toggle('open');
    });
  }
}

/* === PRODUCTS DROPDOWN === */
function initProductsDropdown() {
  const dropdown = document.getElementById('productsDropdown');
  const toggle = document.getElementById('productsToggle');
  if (!dropdown || !toggle) return;

  toggle.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropdown.classList.toggle('open');
  });

  document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target)) {
      dropdown.classList.remove('open');
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') dropdown.classList.remove('open');
  });
}

/* === SMOOTH SCROLL === */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href === '#') return;

      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        const navHeight = document.getElementById('navbar')?.offsetHeight || 0;
        const pos = target.getBoundingClientRect().top + window.scrollY - navHeight;
        window.scrollTo({ top: pos, behavior: 'smooth' });
      }
    });
  });
}

/* === ACTIVE NAV TRACKING === */
function initActiveNavTracking() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.navbar__links a');
  if (!sections.length || !navLinks.length) return;

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY + 120;
    sections.forEach(section => {
      const top = section.offsetTop - 120;
      const bottom = top + section.offsetHeight;
      const id = section.getAttribute('id');

      if (scrollY >= top && scrollY < bottom) {
        navLinks.forEach(link => {
          link.classList.remove('active');
          const href = link.getAttribute('href');
          if (href === '#' + id || (id === 'hero' && href === '#')) {
            link.classList.add('active');
          }
        });
      }
    });
  }, { passive: true });
}
