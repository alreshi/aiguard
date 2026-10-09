/* Set theme before first paint to avoid flash. Stored choice > system > dark.
   Must be loaded WITHOUT defer/async so it runs before the stylesheet paints. */
(function(){try{var t=localStorage.getItem("aiguard-theme");if(!t){t=matchMedia("(prefers-color-scheme: light)").matches?"light":"dark";}document.documentElement.dataset.theme=t;}catch(e){}})();
