/* exocean — minimal progressive enhancement.
   Assembles e-mail addresses in the browser so they are not sitting in the
   markup for address harvesters, the same intent as the original site. */
(function () {
  "use strict";

  document.querySelectorAll(".eml").forEach(function (el) {
    var user = el.getAttribute("data-u");
    var domain = el.getAttribute("data-d");
    if (!user || !domain) return;
    var address = user + "@" + domain;
    var a = document.createElement("a");
    a.href = "mailto:" + address;
    a.textContent = address;
    el.replaceWith(a);
  });
})();
