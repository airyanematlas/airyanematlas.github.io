(function(){
var v=document.getElementById('viewer'); if(!v) return;
var base=v.dataset.base, n=+v.dataset.n, titles=JSON.parse(v.dataset.titles), name=v.dataset.name;
var img=document.getElementById('vimg'), tt=document.getElementById('vt'), cc=document.getElementById('vc');
var prev=document.getElementById('vprev'), next=document.getElementById('vnext'), full=document.getElementById('vfull'), stage=document.getElementById('vstage');
var tgs=[].slice.call(document.querySelectorAll('.tg'));
var cur=1;
function pad(i){return (i<10?'0':'')+i}
function go(i,scroll){
  if(i<1||i>n) return; cur=i;
  img.src=base+'s/'+pad(i)+'.webp'; img.alt=name+', slide '+i+': '+titles[i-1];
  tt.textContent=titles[i-1]; cc.textContent=i+' / '+n;
  prev.disabled=i===1; next.disabled=i===n;
  tgs.forEach(function(t,k){t.classList.toggle('on',k===i-1)});
  if(history.replaceState) history.replaceState(null,'','#'+i);
  if(i<n){var p=new Image(); p.src=base+'s/'+pad(i+1)+'.webp'}
  if(scroll){var r=v.getBoundingClientRect(); if(r.top<0||r.top>innerHeight*0.5) v.scrollIntoView({behavior:'smooth',block:'start'})}
}
prev.onclick=function(){go(cur-1)}; next.onclick=function(){go(cur+1)};
tgs.forEach(function(t,k){t.onclick=function(){go(k+1,true)}});
document.querySelectorAll('[data-go]').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();go(+a.dataset.go,true)})});
full.onclick=function(){if(document.fullscreenElement){document.exitFullscreen()}else if(stage.requestFullscreen){stage.requestFullscreen()}};
document.addEventListener('keydown',function(e){
  if(e.target.matches&&e.target.matches('input,textarea')) return;
  if(e.key==='ArrowRight'||e.key==='PageDown') go(cur+(document.documentElement.dir==='rtl'?-1:1));
  else if(e.key==='ArrowLeft'||e.key==='PageUp') go(cur-(document.documentElement.dir==='rtl'?-1:1));
  else if(e.key==='Home') go(1); else if(e.key==='End') go(n);
});
var x0=null; stage.addEventListener('touchstart',function(e){x0=e.touches[0].clientX},{passive:true});
stage.addEventListener('touchend',function(e){if(x0===null)return;var dx=e.changedTouches[0].clientX-x0; if(Math.abs(dx)>50) go(cur+(dx<0?1:-1)); x0=null});
stage.addEventListener('click',function(e){var r=stage.getBoundingClientRect(); go(cur+((e.clientX-r.left)>r.width/2?1:-1))});
var h=parseInt((location.hash||'').slice(1),10); go(h>=1&&h<=n?h:1);
})();
