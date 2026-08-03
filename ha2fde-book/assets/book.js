
var BK = { meta: [{"n": "01", "t": "破冰", "s": 1, "ac": "#2563EB"}, {"n": "02", "t": "前传", "s": 26, "ac": "#0F766E"}, {"n": "03", "t": "机制", "s": 45, "ac": "#7C3AED"}, {"n": "04", "t": "开发", "s": 70, "ac": "#B45309"}, {"n": "05", "t": "工程化", "s": 90, "ac": "#0D9488"}, {"n": "06", "t": "收束", "s": 117, "ac": "#4F46E5"}, {"n": "07", "t": "深造", "s": 145, "ac": "#475569"}], total: 156 };

/* ================= 自适应缩放 ================= */
var BASE_W = 1280, BASE_H = 720;

/* 全局缩放：宽度 + 窗口高度双约束（原版只看宽度，窗口一矮整页就出屏） */
function bkFit(){
  var wrap = document.querySelector('.bk-wrap');
  if(!wrap) return;
  var byW = (wrap.clientWidth - 60) / BASE_W;
  var byH = (innerHeight - 46 - 36) / BASE_H;
  /* 下限只是防呆，不能高到让纸面撑破窗口 —— 一旦撑破就是横向滚动条，
     比字小更难受。窄窗先靠 bkResponsive 收侧栏腾地方。 */
  var s = Math.max(0.3, Math.min(1, byW, byH));
  document.documentElement.style.setProperty('--bk-scale', s.toFixed(4));
}

/* 逐页缩放：量内容真实高度，超过 720 的页单独缩回去 */
function bkFitPages(){
  var sheets = document.querySelectorAll('.bk-sheet');
  if(!sheets.length) return;

  /* 基准高度取纸面实测值，不写死 720，纸面尺寸真被改了也不会算偏 */
  var base = [];
  sheets.forEach(function(sh){
    var pp = sh.querySelector('.bk-paper');
    base.push(pp && pp.clientHeight ? pp.clientHeight : BASE_H);
  });

  document.body.classList.add('bk-measure');
  var nat = [];
  sheets.forEach(function(sh){
    var fit = sh.querySelector('.bk-fit');
    var sl  = sh.querySelector('section.slide, .bk-opener');
    /* 两个都量取大：第 4 讲的内容块是绝对定位的，只有 slide 自己的
       scrollHeight 才兜得住；.bk-fit 则兜住普通文档流里的外边距。 */
    nat.push(Math.max(fit ? fit.scrollHeight : 0, sl ? sl.scrollHeight : 0));
  });
  document.body.classList.remove('bk-measure');

  var over = [];
  sheets.forEach(function(sh, i){
    if(!sh.querySelector('.bk-fit')) return;
    var h = nat[i], b = base[i];
    if(h > b + 2){
      sh.style.setProperty('--fit', (b / h).toFixed(4));
      sh.setAttribute('data-fitted', h);
      over.push('p' + sh.dataset.page + ' 需 ' + h + 'px');
    } else {
      sh.style.setProperty('--fit', 1);
      sh.removeAttribute('data-fitted');
    }
  });
  if(over.length && /[?&]debug=fit/.test(location.search)){
    document.body.classList.add('bk-debug');
    console.log('[bk] 内容超过 720px、已自动缩放的页面 ' + over.length + ' 个：\n  ' + over.join('\n  '));
  }
}

/* 窄窗自动收起侧栏：1000px 以下侧栏挤掉的宽度已经让纸面缩得不成样子 */
function bkResponsive(){
  if(innerWidth < 1000 && !document.body.classList.contains('wide')){
    document.body.classList.add('wide');
    /* 收起有 260ms 过渡，此刻量宽度会量到动画中间值，等动完再量一次 */
    setTimeout(bkFit, 320);
  }
}

function bkRefit(){ bkResponsive(); bkFit(); bkFitPages(); }
addEventListener('resize', function(){ bkResponsive(); bkFit(); });
if(document.fonts && document.fonts.ready) document.fonts.ready.then(bkRefit);
/* load 时字体常常还没落定，量出来会虚高几像素、把不该缩的页也缩了；
   稍后再量一次，bkFitPages 每次都从测量态重算，不会叠加。 */
addEventListener('load', function(){ bkRefit(); setTimeout(bkFitPages, 700); });

/* ---- 代码展开 ---- */
function bkToggle(el){ el.parentNode.classList.toggle('open'); }
function bkAll(on){
  document.querySelectorAll('.bk-code-card').forEach(function(c){ c.classList.toggle('open', !!on); });
}
document.querySelectorAll('.bk-code-link').forEach(function(a){
  a.addEventListener('click', function(){
    var c = document.querySelector(a.getAttribute('href'));
    if(c) c.classList.add('open');
  });
});

/* ---- 打印 ---- */
function bkPrint(){ bkAll(0); window.print(); }

/* ---- 侧栏折叠 ---- */
document.getElementById('bk-burger').onclick = function(){
  document.body.classList.toggle('wide'); setTimeout(bkFit, 260);
};

/* ---- 滚动同步：当前章 / 页码 / 进度 ---- */
var sheets = [].slice.call(document.querySelectorAll('.bk-sheet'));
var navChs = [].slice.call(document.querySelectorAll('.bk-nav-ch'));
var crumb = document.getElementById('bk-crumb');
var pageno = document.getElementById('bk-pageno');
var bar = document.querySelector('#bk-bar i');
var up = document.getElementById('bk-up');
var cur = -1;

function bkSync(){
  var mid = window.scrollY + innerHeight*0.36, best = null;
  for(var i=0;i<sheets.length;i++){
    if(sheets[i].offsetTop <= mid) best = sheets[i]; else break;
  }
  var doc = document.documentElement;
  bar.style.width = (window.scrollY/(doc.scrollHeight-innerHeight)*100).toFixed(2)+'%';
  up.classList.toggle('on', window.scrollY > 600);

  if(!best){
    if(cur!==0){ crumb.innerHTML='<b>扉页与目录</b>'; pageno.innerHTML='<b>—</b> / '+BK.total;
      navChs.forEach(function(n){n.classList.remove('on');}); cur=0; }
    return;
  }
  var p = +best.dataset.page, ci = +best.dataset.ch;
  if(p===cur) return;
  cur = p;
  var m = BK.meta[ci-1];
  var t = best.dataset.title || '';
  crumb.innerHTML = '<b>第 '+m.n+' 章　'+m.t+'</b>' + (t ? '<i>›</i>'+t : '');
  pageno.innerHTML = '<b>'+p+'</b> / '+BK.total;
  navChs.forEach(function(n){ n.classList.toggle('on', +n.dataset.ch===ci); });
  var on = document.querySelector('.bk-nav-ch.on');
  if(on){
    var links = [].slice.call(on.querySelectorAll('li a')), pick=null;
    links.forEach(function(a){ if(+a.getAttribute('href').slice(2) <= p) pick=a; });
    links.forEach(function(a){ a.classList.toggle('cur', a===pick); });
  }
}
addEventListener('scroll', bkSync, {passive:true});

/* ---- 键盘：←→ 逐页 ---- */
addEventListener('keydown', function(e){
  if(/input|textarea/i.test(e.target.tagName)) return;
  if(e.ctrlKey||e.metaKey||e.altKey) return;
  var i = sheets.findIndex(function(s){ return +s.dataset.page === cur; });
  if(e.key==='ArrowRight'||e.key==='PageDown'){
    e.preventDefault();
    if(i>=0 && i===sheets.length-1){ bkGo('next'); return; }
    var n=sheets[i+1]||sheets[0];
    if(i<0) n=sheets[0]; scrollTo({top:n.offsetTop-58,behavior:'smooth'});
  } else if(e.key==='ArrowLeft'||e.key==='PageUp'){
    e.preventDefault();
    if(i===0){ bkGo('prev'); return; }
    if(i<0){ scrollTo({top:0,behavior:'smooth'}); }
    else scrollTo({top:sheets[i-1].offsetTop-58,behavior:'smooth'});
  } else if(e.key==='Home'){ e.preventDefault(); scrollTo({top:0,behavior:'smooth'}); }
  else if(e.key==='End'){ e.preventDefault();
    scrollTo({top:sheets[sheets.length-1].offsetTop-58,behavior:'smooth'}); }
  else if(e.key==='p'||e.key==='P'){ e.preventDefault(); bkPrint(); }
});

/* ---- 侧栏搜索筛选 ---- */
document.getElementById('bk-q').addEventListener('input', function(e){
  var q = e.target.value.trim().toLowerCase();
  navChs.forEach(function(n){
    var hitCh = n.querySelector('.bk-nav-ch-t span').textContent.toLowerCase().indexOf(q)>=0;
    var any = hitCh;
    n.querySelectorAll('li').forEach(function(li){
      var hit = !q || li.textContent.toLowerCase().indexOf(q)>=0;
      li.classList.toggle('dim', !(hit||hitCh));
      if(hit) any = true;
    });
    n.classList.toggle('dim', !!q && !any);
    if(q && any) n.classList.add('on');
  });
});

/* ---- 点击章标题展开/收起 ---- */
document.querySelectorAll('.bk-nav-ch-t').forEach(function(a){
  a.addEventListener('click', function(){
    setTimeout(function(){
      navChs.forEach(function(n){ n.classList.remove('on'); });
      a.parentNode.classList.add('on');
    }, 30);
  });
});

bkFit(); bkSync();

/* ---- 调试参数：?at=code1 立即定位 ---- */
(function(){
  try{
    var at = new URL(location.href).searchParams.get('at');
    if(!at) return;
    var id = /^\d+$/.test(at) ? 'p' + at : at;
    var el = document.getElementById(id);
    if(!el) return;
    document.documentElement.style.scrollBehavior = 'auto';
    document.documentElement.scrollTop = el.offsetTop - 58;
    cur = -1; bkSync();
  }catch(e){
    document.title = 'JERR:' + e.message;
  }
})();
addEventListener('beforeprint', function(){ document.body.classList.add('printing'); });


/* ================= 跨文件翻页 ================= */
var BK_FILES = ["index.html", "ch01.html", "ch02.html", "ch03.html", "ch04.html", "ch05.html", "ch06.html", "ch07.html", "appendix.html"];
function bkGo(dir){
  var here = location.pathname.split('/').pop() || 'index.html';
  var i = BK_FILES.indexOf(here);
  if(i < 0) return;
  var t = BK_FILES[dir === 'next' ? i + 1 : i - 1];
  if(!t) return;
  location.href = dir === 'next' ? t : t + '#bk-last';
}

/* 从上一章按 ← 进来时，直接落到本章最后一页 */
if(location.hash === '#bk-last'){
  try{ history.replaceState(null, '', location.pathname); }catch(e){}
  addEventListener('load', function(){
    var all = document.querySelectorAll('.bk-sheet');
    var last = all[all.length - 1];
    if(last){ document.documentElement.style.scrollBehavior='auto';
      scrollTo(0, last.offsetTop - 58); cur=-1; bkSync(); }
  });
}

/* 非附录页上「展开全部代码」直接跳附录 */
(function(){
  var _all = bkAll;
  bkAll = function(on){
    if(!document.querySelector('.bk-code-card')){ location.href = 'appendix.html'; return; }
    _all(on);
  };
})();

/* 当前文件所属章：直接点亮，不必等滚动 */
(function(){
  var s = document.querySelector('.bk-sheet');
  if(!s) return;
  var ci = +s.dataset.ch;
  document.querySelectorAll('.bk-nav-ch').forEach(function(n){
    n.classList.toggle('on', +n.dataset.ch === ci);
  });
})();
