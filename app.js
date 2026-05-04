// === TRANSCODE — Landing Page v2 ===

document.addEventListener('DOMContentLoaded', () => {

  // --- Nav scroll ---
  const nav = document.getElementById('nav');
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });

  // --- Counter animation ---
  const statNums = document.querySelectorAll('.stat-num');
  const heroObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        statNums.forEach(el => animateCounter(el));
        heroObserver.disconnect();
      }
    });
  }, { threshold: 0.5 });

  const heroStats = document.querySelector('.hero-stats');
  if (heroStats) heroObserver.observe(heroStats);

  function animateCounter(el) {
    const target = parseInt(el.dataset.target);
    const duration = 1400;
    const startTime = performance.now();
    function update(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target).toLocaleString();
      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        el.textContent = target.toLocaleString();
      }
    }
    requestAnimationFrame(update);
  }

  // --- Typewriter terminal ---
  const jsonResponse = `{
  "date": "2026-05-04",
  "nikkei225": { "close": 36847, "change": "+1.24%" },
  "usdjpy": 157.03,
  "disclosures_today": 47,
  "high_impact": [
    "Toyota: earnings revision +18%",
    "SoftBank: ¥200B buyback announced"
  ],
  "foreign_investors": {
    "net_mln_jpy": 827,
    "trend": "accumulating"
  },
  "tankan_di": 14,
  "coverage": "3,889 TSE-listed companies"
}`;

  const typewriterTarget = document.getElementById('typewriter-target');
  let typewriterStarted = false;

  function syntaxHighlight(json) {
    return json
      .replace(/"([^"]+)"(?=\s*:)/g, '<span class="jk">"$1"</span>')
      .replace(/:\s*"([^"]+)"/g, ': <span class="js">"$1"</span>')
      .replace(/:\s*(\d+\.?\d*)/g, ': <span class="jn">$1</span>')
      .replace(/[{}[\]]/g, '<span class="jb">$&</span>');
  }

  function typewrite(el, text, speed) {
    let i = 0;
    const highlighted = syntaxHighlight(text);
    // Build character-by-character by inserting into a hidden div and revealing
    el.innerHTML = '';
    const chars = text.split('');
    const output = [];

    function addChar() {
      if (i >= chars.length) return;
      output.push(chars[i]);
      el.innerHTML = syntaxHighlight(output.join('')) + '<span class="terminal-cursor"></span>';
      i++;
      const delay = chars[i - 1] === '\n' ? speed * 3 : 
                    chars[i - 1] === ' ' ? speed * 0.3 : speed;
      setTimeout(addChar, delay);
    }
    addChar();
  }

  const demoObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !typewriterStarted) {
        typewriterStarted = true;
        setTimeout(() => typewrite(typewriterTarget, jsonResponse, 18), 400);
        demoObserver.disconnect();
      }
    });
  }, { threshold: 0.3 });

  const terminalEl = document.querySelector('.terminal');
  if (terminalEl) demoObserver.observe(terminalEl);

  // --- Tab switching ---
  const tabs = document.querySelectorAll('.tab');
  const panels = document.querySelectorAll('.code-panel');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      tabs.forEach(t => t.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(`panel-${target}`).classList.add('active');
    });
  });

  // --- Copy buttons ---
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const code = document.getElementById(btn.dataset.target).textContent;
      navigator.clipboard.writeText(code).then(() => {
        const orig = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => { btn.textContent = orig; }, 1500);
      });
    });
  });

  // --- Scroll fade-in ---
  const fadeEls = document.querySelectorAll('.fade-in');
  const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        fadeObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });
  fadeEls.forEach(el => fadeObserver.observe(el));

});
