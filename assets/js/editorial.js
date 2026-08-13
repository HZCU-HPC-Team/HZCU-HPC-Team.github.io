(() => {
  const reducedMotion = window.matchMedia
    ? window.matchMedia("(prefers-reduced-motion: reduce)")
    : { matches: false };
  const revealElements = document.querySelectorAll("[data-reveal]");

  const showAll = () => {
    revealElements.forEach((element) => element.classList.add("is-visible"));
  };

  if (reducedMotion.matches || !("IntersectionObserver" in window)) {
    showAll();
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: "0px 0px -8%", threshold: 0.12 },
  );

  revealElements.forEach((element, index) => {
    element.classList.add("is-reveal-ready");
    element.style.setProperty("--reveal-delay", `${Math.min(index % 3, 2) * 90}ms`);
    observer.observe(element);
  });
})();
