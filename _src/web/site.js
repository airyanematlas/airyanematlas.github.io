(function(){
var d=document;
/* mobile nav */
var b=d.querySelector('.burger'),n=d.getElementById('nav');
if(b)b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o)});
/* copy buttons */
d.addEventListener('click',function(e){
 var c=e.target.closest('.copybtn');
 if(c){var t=c.getAttribute('data-copy');var done=function(){var o=c.textContent;c.textContent=c.getAttribute('data-done');c.classList.add('ok');setTimeout(function(){c.textContent=o;c.classList.remove('ok')},1600)};
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(done,done)}else{var a=d.createElement('textarea');a.value=t;d.body.appendChild(a);a.select();try{d.execCommand('copy')}catch(x){}a.remove();done()}}
 var z=e.target.closest('.zoom');
 if(z){e.preventDefault();lb(z.getAttribute('data-full')||z.querySelector('img').src)}
});
/* lightbox */
function lb(src){var l=d.getElementById('lb');if(!l){l=d.createElement('div');l.id='lb';l.innerHTML='<img alt="">';l.addEventListener('click',function(){l.classList.remove('on')});d.body.appendChild(l)}
 l.firstChild.src=src;l.classList.add('on')}
d.addEventListener('keydown',function(e){if(e.key==='Escape'){var l=d.getElementById('lb');if(l)l.classList.remove('on')}});
/* infographic language tabs */
var seg=d.querySelector('.seg');
if(seg)seg.addEventListener('click',function(e){var bt=e.target.closest('button');if(!bt)return;var L=bt.getAttribute('data-l');
 seg.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x===bt)});
 d.querySelectorAll('.fig img').forEach(function(im){var s=im.getAttribute('data-src-'+L);if(s){im.src=s;im.parentNode.setAttribute('data-full',s);im.alt=im.getAttribute('data-alt-'+L)||im.alt}});
 var dl=d.querySelectorAll('.act .primary');dl.forEach(function(a){a.href=a.href.replace(/\/(en|fa)-(\d)-x\.jpg/,'/'+L+'-$2-x.jpg')})});
/* archive filters */
var A=d.getElementById('archive');
if(A){var cards=[].slice.call(A.querySelectorAll('.card')),q=d.getElementById('q'),cnt=d.getElementById('n'),F={series:'',topic:''};
 var fa=d.documentElement.lang==='fa';var dg=function(x){return fa?String(x).replace(/\d/g,function(c){return '۰۱۲۳۴۵۶۷۸۹'[c]}):x};
 function run(){var s=(q.value||'').toLowerCase().trim(),k=0;
  cards.forEach(function(c){var ok=(!F.series||c.dataset.series===F.series)&&(!F.topic||(' '+c.dataset.topics+' ').indexOf(' '+F.topic+' ')>-1)&&(!s||c.dataset.q.indexOf(s)>-1);c.hidden=!ok;if(ok)k++});cnt.textContent=dg(k)}
 d.querySelectorAll('.fgroup').forEach(function(g){g.addEventListener('click',function(e){var bt=e.target.closest('button');if(!bt)return;
  g.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x===bt)});F[g.dataset.key]=bt.dataset.v;run()})});
 q.addEventListener('input',run);
 var h=location.hash.replace('#','').split('&');h.forEach(function(p){var kv=p.split('=');if(kv[0] in F){F[kv[0]]=kv[1];var g=d.querySelector('.fgroup[data-key='+kv[0]+']');if(g)g.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x.dataset.v===kv[1])})}});run()}
})();
