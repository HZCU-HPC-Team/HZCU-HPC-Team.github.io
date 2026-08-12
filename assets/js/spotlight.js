(() => {
  const reveal = document.querySelector("[data-spotlight-reveal]");
  if (!reveal) return;
  const reducedMotion = window.matchMedia
    ? window.matchMedia("(prefers-reduced-motion: reduce)")
    : { matches: false };
  const finePointer = window.matchMedia
    ? window.matchMedia("(pointer: fine)")
    : { matches: false };
  if (reducedMotion.matches || !finePointer.matches) return;
  const canvas = document.querySelector("[data-spotlight-canvas]");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const SPOTLIGHT_R = 260;
  const mouse = { x: 0, y: 0 };
  const smooth = { x: -999, y: -999 };
  let rafId = 0;
  let applied = false;

  const resize = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };
  resize();
  window.addEventListener("resize", resize);

  window.addEventListener(
    "mousemove",
    (event) => {
      mouse.x = event.clientX;
      mouse.y = event.clientY;
    },
    { passive: true },
  );

  const tick = () => {
    smooth.x += (mouse.x - smooth.x) * 0.1;
    smooth.y += (mouse.y - smooth.y) * 0.1;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const gradient = ctx.createRadialGradient(
      smooth.x,
      smooth.y,
      0,
      smooth.x,
      smooth.y,
      SPOTLIGHT_R,
    );
    gradient.addColorStop(0, "rgba(255,255,255,1)");
    gradient.addColorStop(0.4, "rgba(255,255,255,1)");
    gradient.addColorStop(0.6, "rgba(255,255,255,0.75)");
    gradient.addColorStop(0.75, "rgba(255,255,255,0.4)");
    gradient.addColorStop(0.88, "rgba(255,255,255,0.12)");
    gradient.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const mask = canvas.toDataURL();
    reveal.style.maskImage = `url(${mask})`;
    reveal.style.webkitMaskImage = `url(${mask})`;
    reveal.style.maskSize = "100% 100%";
    reveal.style.webkitMaskSize = "100% 100%";

    if (!applied) {
      applied = true;
      reveal.classList.add("is-visible");
    }
    rafId = window.requestAnimationFrame(tick);
  };
  rafId = window.requestAnimationFrame(tick);

  window.addEventListener("unload", () => {
    window.cancelAnimationFrame(rafId);
  });
})();
