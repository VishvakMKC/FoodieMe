function animateOnRefresh(s) {
  var rows = document.querySelectorAll(s);
  rows.forEach(function (rows) {
      rows.classList.add('appear');
  });
}
animateOnRefresh('.home-trans');
animateOnRefresh('.home-img');
window.addEventListener('load', animateOnRefresh);
