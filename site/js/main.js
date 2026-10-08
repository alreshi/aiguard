/* AIGuard site — vanilla JS, deferred, no dependencies.
   Progressive enhancement only: every page is fully readable without JS. */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Theme toggle ---- */
  var toggle = document.querySelector(".theme-toggle");
  if (toggle) {
    var icons = {
      dark: toggle.querySelector(".icon-sun"),
      light: toggle.querySelector(".icon-moon")
    };
    function sync() {
      var t = document.documentElement.dataset.theme || "dark";
      if (icons.dark) icons.dark.hidden = t !== "dark";
      if (icons.light) icons.light.hidden = t !== "light";
      toggle.setAttribute("aria-label",
        t === "dark" ? "Switch to light theme" : "Switch to dark theme");
    }
    toggle.addEventListener("click", function () {
      var next = (document.documentElement.dataset.theme || "dark") === "dark"
        ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem("aiguard-theme", next); } catch (e) {}
      sync();
    });
    sync();
  }

  /* ---- Copy buttons ---- */
  function copyText(text, done) {
    if (navigator.clipboard && window.isSecureContext !== false) {
      navigator.clipboard.writeText(text).then(done, function () { legacy(); });
    } else { legacy(); }
    function legacy() {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); } catch (e) {}
      document.body.removeChild(ta);
      done();
    }
  }
  document.querySelectorAll(".codeblock").forEach(function (block) {
    var btn = block.querySelector(".copy");
    var pre = block.querySelector("pre");
    if (!btn || !pre) return;
    btn.addEventListener("click", function () {
      copyText(pre.textContent.replace(/ /g, " "), function () {
        btn.textContent = "copied";
        btn.classList.add("copied");
        setTimeout(function () {
          btn.textContent = "copy";
          btn.classList.remove("copied");
        }, 1600);
      });
    });
  });

  /* ---- Docs sidebar (mobile) ---- */
  var sideToggle = document.querySelector(".sidebar-toggle");
  var sidebar = document.querySelector(".docs-sidebar");
  if (sideToggle && sidebar) {
    sideToggle.addEventListener("click", function () {
      var open = sidebar.classList.toggle("open");
      sideToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---- Heading anchors in docs content ---- */
  document.querySelectorAll(".docs-content h2[id], .docs-content h3[id]")
    .forEach(function (h) {
      var a = document.createElement("a");
      a.className = "heading-anchor";
      a.href = "#" + h.id;
      a.setAttribute("aria-label", "Link to this section");
      a.textContent = "#";
      h.appendChild(a);
    });

  /* ---- Terminal demo ----
     Lines are fully present in HTML (no-JS / reduced-motion friendly).
     When playing, JS hides them and reveals in sequence; [data-type] lines
     get a typing effect. */
  var term = document.querySelector("[data-terminal]");
  if (term) {
    var body = term.querySelector(".terminal-body");
    var lines = Array.prototype.slice.call(body.querySelectorAll(".tl"));
    var replayBtn = term.querySelector(".terminal-replay");
    var timers = [];
    var started = false;

    function clearTimers() {
      timers.forEach(function (t) { clearTimeout(t); });
      timers = [];
    }

    function showAll() {
      clearTimers();
      term.classList.remove("playing");
      lines.forEach(function (l) {
        l.classList.add("shown");
        if (l.dataset.text) l.firstChild.nodeValue = l.dataset.text;
        l.classList.remove("t-caret");
      });
    }

    function play() {
      clearTimers();
      if (reduceMotion) { showAll(); return; }
      term.classList.add("playing");
      var delay = 350;
      lines.forEach(function (line) {
        if (line.dataset.type === "cmd") {
          var full = line.dataset.text;
          timers.push(setTimeout(function () {
            line.classList.add("shown", "t-caret");
            line.firstChild.nodeValue = "";
            for (var i = 1; i <= full.length; i++) {
              (function (n) {
                timers.push(setTimeout(function () {
                  line.firstChild.nodeValue = full.slice(0, n);
                  if (n === full.length) {
                    line.classList.remove("t-caret");
                  }
                }, n * 28));
              })(i);
            }
          }, delay));
          delay += full.length * 28 + 500;
        } else {
          timers.push(setTimeout(function () {
            line.classList.add("shown");
          }, delay));
          delay += line.dataset.pause ? parseInt(line.dataset.pause, 10) : 420;
        }
      });
    }

    if (replayBtn) {
      replayBtn.addEventListener("click", function () {
        lines.forEach(function (l) { l.classList.remove("shown"); });
        play();
      });
    }

    if (reduceMotion || !("IntersectionObserver" in window)) {
      showAll();
    } else {
      term.classList.add("playing");
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting && !started) {
            started = true;
            play();
            io.disconnect();
          }
        });
      }, { threshold: 0.3 });
      io.observe(term);
    }
  }
})();
