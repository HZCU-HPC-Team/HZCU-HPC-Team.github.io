/* Terminal hero typing animation.
   Progressive enhancement: all lines render visible in HTML. Only when JS
   runs (and the user allows motion) do we hide them via `.is-animated`
   (visibility, keeping layout) and type them back one by one. */
(() => {
  const screen = document.querySelector("[data-terminal]");
  if (!screen) return;
  const reducedMotion = window.matchMedia
    ? window.matchMedia("(prefers-reduced-motion: reduce)")
    : { matches: false };
  if (reducedMotion.matches) return;

  const steps = Array.from(
    screen.querySelectorAll("[data-terminal-type], [data-terminal-out], [data-terminal-idle]"),
  );
  if (!steps.length) return;

  const TYPE_MS = 42;
  const LINE_PAUSE_MS = 260;
  const OUT_PAUSE_MS = 420;

  // Detach the blinking cursor so it can trail whatever is being typed.
  const idleLine = screen.querySelector("[data-terminal-idle]");
  const cursor = screen.querySelector(".hero-terminal__cursor");
  if (!cursor) return;

  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  const typeLine = async (line) => {
    const cmd = line.querySelector(".hero-terminal__cmd");
    line.classList.add("is-typed");
    if (!cmd) return;
    const text = cmd.textContent;
    cmd.textContent = "";
    cmd.appendChild(cursor);
    for (const ch of text) {
      cursor.before(document.createTextNode(ch));
      await wait(TYPE_MS);
    }
  };

  const run = async () => {
    screen.classList.add("is-animated");
    await wait(OUT_PAUSE_MS);
    for (const step of steps) {
      if (step.hasAttribute("data-terminal-type")) {
        await typeLine(step);
        await wait(LINE_PAUSE_MS);
      } else if (step.hasAttribute("data-terminal-out")) {
        step.classList.add("is-typed");
        await wait(OUT_PAUSE_MS);
      } else {
        // Idle prompt: park the cursor here and stop.
        step.classList.add("is-typed");
        if (idleLine) idleLine.appendChild(cursor);
      }
    }
  };

  run();
})();

/* Scroll-down buttons: smooth-scroll on click. A button with a
   data-scroll-target scrolls that element into view (landing exactly on the
   target, which compensates for the sticky header via CSS scroll-margin-top);
   otherwise it falls back to travelling data-scroll-factor viewports
   (default 1.2). Independent of the typing animation above so it keeps
   working for prefers-reduced-motion users (instant jump). */
(() => {
  const buttons = document.querySelectorAll("[data-scroll-down]");
  if (!buttons.length) return;
  const reducedMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  buttons.forEach((button) => {
    const target = button.dataset.scrollTarget
      ? document.querySelector(button.dataset.scrollTarget)
      : null;
    const factor = parseFloat(button.dataset.scrollFactor) || 1.2;
    button.addEventListener("click", () => {
      if (target) {
        target.scrollIntoView({
          behavior: reducedMotion ? "auto" : "smooth",
          block: "start",
        });
        return;
      }
      window.scrollBy({
        top: window.innerHeight * factor,
        behavior: reducedMotion ? "auto" : "smooth",
      });
    });
  });
})();
