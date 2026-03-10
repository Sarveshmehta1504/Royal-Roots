/* =============================================
   FORM.JS — AJAX Submit + Local Storage Backup
   Stays on the same page after submission.
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('leadForm');
  if (!form) return;

  const pills = form.querySelectorAll('.pill-option');
  const hiddenInput = document.getElementById('interestedIn');
  const submitBtn = document.getElementById('submitBtn');
  const selectedProducts = new Set();

  /* === PILL SELECTION === */
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      const val = pill.getAttribute('data-value');
      if (selectedProducts.has(val)) {
        selectedProducts.delete(val);
        pill.classList.remove('active');
      } else {
        selectedProducts.add(val);
        pill.classList.add('active');
      }
      if (hiddenInput) {
        hiddenInput.value = Array.from(selectedProducts).join(', ');
      }
    });
  });

  /* === AJAX FORM SUBMISSION (stays on same page) === */
  form.addEventListener('submit', (e) => {
    e.preventDefault(); /* Prevent page navigation */

    const name = form.querySelector('[name="name"]');
    const phone = form.querySelector('[name="phone"]');

    /* Basic validation */
    if (!name.value.trim() || !phone.value.trim()) {
      alert('Please fill in Name and Phone number.');
      return;
    }

    /* Collect form data */
    const formData = new FormData(form);

    /* Store in localStorage as backup */
    try {
      const entry = {
        name: name.value.trim(),
        phone: phone.value.trim(),
        email: (form.querySelector('[name="email"]').value || '').trim(),
        city: (form.querySelector('[name="city"]').value || '').trim(),
        interested_in: hiddenInput ? hiddenInput.value : '',
        message: (form.querySelector('[name="message"]').value || '').trim(),
        submitted_at: new Date().toISOString()
      };
      const leads = JSON.parse(localStorage.getItem('rr_leads') || '[]');
      leads.push(entry);
      localStorage.setItem('rr_leads', JSON.stringify(leads));
    } catch (err) { /* continue */ }

    /* Update button */
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Sending...';
    submitBtn.disabled = true;

    /* Send via AJAX */
    fetch(form.action, {
      method: 'POST',
      body: formData,
      headers: { 'Accept': 'application/json' }
    })
    .then(response => {
      if (response.ok) {
        /* Success — show inline message */
        form.innerHTML =
          '<div class="form-success">' +
            '<svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/></svg>' +
            '<h3>Thank You!</h3>' +
            '<p>Your request has been received. We will call you back within 2 hours.</p>' +
          '</div>';
      } else {
        throw new Error('Server error');
      }
    })
    .catch(() => {
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
      alert('Something went wrong. Please try again or call us at 99748 59974.');
    });
  });
});
