# -*- coding: utf-8 -*-
"""
把单文件 book.html 拆成分章多文件版。

  book.html (490KB)
    → index.html            扉页 + 目录 + 版权页
    → ch01.html … ch07.html 每章 = 章扉页 + 该章内容页
    → appendix.html         17 个脚本源码
    → assets/book.css       公共样式（外壳 + 各讲作用域样式 + 自适应缩放）
    → assets/book.js        公共脚本（缩放 / 导航同步 / 键盘 / 搜索）

顺带修掉原版的排版裁切：原来每页 .slide 固定 720px 高且 overflow:hidden，
内容超出直接被切掉。这里给每页套一层 .bk-fit，由 book.js 量出内容真实高度后
设 --fit，让页面按需长高再等比缩回 720px —— 书页观感不变，内容不再丢。

用法：python3 split_book.py     （在 ha2fde-book/ 目录下执行）
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'book.html')
ASSETS = os.path.join(HERE, 'assets')

BASE_W, BASE_H = 1280, 720


# ============================================================
# 一、标签配对：从 <tag 开始扫到配对的 </tag>
# ============================================================
def match_block(s, start, tag):
    """start 为 '<tag' 的下标，返回配对 '</tag>' 之后的下标"""
    pat = re.compile(r'<(/?)%s\b' % tag, re.I)
    depth, i = 0, start
    while True:
        m = pat.search(s, i)
        if not m:
            raise ValueError('标签未配对：%s @ %d' % (tag, start))
        if m.group(1):
            depth -= 1
            if depth == 0:
                return s.index('>', m.end()) + 1
        else:
            depth += 1
        i = m.end()


def take(s, opener_re, tag):
    """按正则找到开标签，返回 (整块 HTML, 结束下标)"""
    m = re.search(opener_re, s)
    if not m:
        raise ValueError('找不到：%s' % opener_re)
    end = match_block(s, m.start(), tag)
    return s[m.start():end], end


# ============================================================
# 二、拆出各部件
# ============================================================
def parse(src):
    part = {}

    part['css'] = src[src.index('<style>') + 7: src.index('</style>')]
    part['js'] = src[src.index('<script>') + 8: src.index('</script>')]

    part['side'], _ = take(src, r'<aside id="bk-side">', 'aside')
    part['top'], _ = take(src, r'<div id="bk-top">', 'div')
    part['cover'], _ = take(src, r'<section class="bk-title-page"', 'section')
    part['toc'], _ = take(src, r'<section class="bk-toc"', 'section')
    part['apx'], _ = take(src, r'<section class="bk-apx"', 'section')
    part['colophon'], _ = take(src, r'<section class="bk-colophon"', 'section')

    # --- 156 个书页，按 data-ch 归章 ---
    sheets = {}
    for m in re.finditer(r'<div class="bk-sheet\b', src):
        end = match_block(src, m.start(), 'div')
        html = src[m.start():end]
        ch = int(re.search(r'data-ch="(\d+)"', html).group(1))
        sheets.setdefault(ch, []).append(wrap_fit(html))
    part['sheets'] = sheets
    return part


def wrap_fit(sheet):
    """给 .bk-paper 内部套一层 .bk-fit，作为整页等比缩放的载体"""
    m = re.search(r'<div class="bk-paper[^"]*">', sheet)
    if not m:
        return sheet
    inner_start = m.end()
    inner_end = match_block(sheet, m.start(), 'div') - len('</div>')
    return (sheet[:inner_start] + '<div class="bk-fit">'
            + sheet[inner_start:inner_end] + '</div>' + sheet[inner_end:])


# ============================================================
# 三、锚点重写：#pN → chNN.html#pN
# ============================================================
def page_to_file(sheets):
    """页号 → 文件名"""
    m = {}
    for ch, lst in sheets.items():
        for s in lst:
            p = int(re.search(r'data-page="(\d+)"', s).group(1))
            m[p] = 'ch%02d.html' % ch
    return m


def rewrite_links(html, p2f, self_file=None):
    """把全书内锚点改成跨文件链接；指向本文件的保持纯锚点"""
    def rep_page(m):
        p = int(m.group(1))
        f = p2f.get(p)
        if not f:
            return m.group(0)
        return 'href="#p%d"' % p if f == self_file else 'href="%s#p%d"' % (f, p)

    html = re.sub(r'href="#p(\d+)"', rep_page, html)
    html = html.replace('href="#bk-appendix"',
                        'href="#bk-appendix"' if self_file == 'appendix.html'
                        else 'href="appendix.html"')
    for anc in ('bk-cover', 'bk-toc'):
        html = html.replace('href="#%s"' % anc,
                            'href="#%s"' % anc if self_file == 'index.html'
                            else 'href="index.html#%s"' % anc)
    return html


# ============================================================
# 四、CSS / JS 附加片段
# ============================================================
FIT_CSS = r'''
/* ==================== 自适应：内容超高的页面按需长高再等比缩回 ==================== */
/* 原版 .slide 固定 720px + overflow:hidden，内容超出即被裁掉。
   现在由 book.js 量出真实高度写入 --fit，页面长到 720/--fit 再 scale(--fit) 缩回，
   渲染尺寸仍是 1280×720，但内容完整。 */
.bk-sheet{--fit:1}
/* 先把纸面尺寸夺回来。每讲原始 CSS 的 html,body{height:100%} 被作用域化成了
   .chN{height:100%}，而 .chN 恰好就挂在 .bk-paper 这个元素上，于是纸面高度被
   从 720px 劫持成外层容器高度（1280×720 的场景下只剩 630px），里面 720px 的
   .slide 底部约 90px 直接被 overflow:hidden 吃掉 —— 这才是「上下看不全」的根。 */
.bk-wrap .bk-paper{width:1280px !important;height:720px !important}

/* position:relative 是必需的：第 3~7 讲的 .slide 是 position:absolute，
   不给 .bk-fit 定位，它们的包含块就是 .bk-paper（死高），
   .bk-fit 长高时带不动它们，缩放对这 5 章等于没做。
   尺寸用百分比跟随纸面，不写死像素，免得纸面一变又对不上。 */
.bk-fit{position:relative;width:100%;height:calc(100% / var(--fit));
  transform:scale(var(--fit));transform-origin:top center}
.bk-wrap .bk-paper section.slide{height:100% !important}
.bk-wrap .bk-paper .bk-opener{height:100%}

/* 测量态：放开高度与裁切、把绝对定位的页拉回文档流，量完即摘 */
body.bk-measure .bk-fit{height:auto !important;transform:none !important}
body.bk-measure .bk-paper{overflow:visible !important}
body.bk-measure .bk-wrap .bk-paper section.slide,
body.bk-measure .bk-wrap .bk-paper .bk-opener{
  position:relative !important;inset:auto !important;transform:none !important;
  height:auto !important;min-height:0 !important;overflow:visible !important}

/* 调试：?debug=fit 给被缩过的页描红边 */
body.bk-debug .bk-sheet[data-fitted] .bk-paper{outline:2px solid #DC2626;outline-offset:2px}

/* 章末上下章导航 */
.bk-pager{display:flex;justify-content:space-between;gap:14px;margin:34px auto 0;max-width:1180px}
.bk-pager a{flex:1;max-width:340px;padding:14px 18px;background:#fff;border:1px solid var(--bk-line);
  border-radius:8px;text-decoration:none;color:var(--bk-ink);box-shadow:0 1px 3px rgba(15,23,42,.05)}
.bk-pager a:hover{border-color:var(--bk-blue);color:var(--bk-blue)}
.bk-pager a.next{text-align:right}
.bk-pager small{display:block;font-size:11px;color:var(--bk-faint);letter-spacing:.1em;margin-bottom:3px}
.bk-pager b{font-size:14.5px;font-weight:700}
.bk-pager .sp{flex:1;max-width:340px}

/* 窄窗自动收起侧栏后，正文不再被挤塌 */
@media (max-width:1000px){
  .bk-wrap{padding:18px 14px 60px}
}

/* 打印：--fit 仍需生效，否则导出 PDF 一样会裁切 */
@media print{
  .bk-wrap .bk-paper{width:960pt !important;height:540pt !important}
  .bk-fit{position:relative;width:100%;height:calc(100% / var(--fit));
    transform:scale(var(--fit)) !important;transform-origin:top center}
  .bk-wrap .bk-paper section.slide,.bk-wrap .bk-paper .bk-opener{
    width:100% !important;height:100% !important}
  .bk-pager{display:none !important}
}
'''

FIT_JS = r'''
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
'''


def build_js(js, chapter_files):
    """改写原 JS：换掉 bkFit、补跨文件翻页、去掉单文件才有的假设"""
    # 1. 摘掉原来的 bkFit + resize 绑定，换成新的
    #    注意用 lambda 传替换串：re.sub 会把替换串里的 \n 当转义序列处理，
    #    直接传字符串会把 JS 里的 '\n' 打成真换行，字符串字面量当场断掉。
    js, n = re.subn(
        r'/\* ---- 缩放：.*?window\.addEventListener\(\'resize\', bkFit\);',
        lambda m: FIT_JS.strip(), js, count=1, flags=re.S)
    if n != 1:
        raise ValueError('bkFit 替换未命中，book.html 的脚本可能已变')

    # 2. 键盘翻页：翻到本文件首/末页时跳相邻章文件
    #    （str.replace 不处理转义，这里可以直接传字符串）
    before = js
    js = js.replace(
        "if(e.key==='ArrowRight'||e.key==='PageDown'){\n"
        "    e.preventDefault(); var n=sheets[i+1]||sheets[0];\n"
        "    if(i<0) n=sheets[0]; scrollTo({top:n.offsetTop-58,behavior:'smooth'});\n"
        "  } else if(e.key==='ArrowLeft'||e.key==='PageUp'){\n"
        "    e.preventDefault();\n"
        "    if(i<=0){ scrollTo({top:0,behavior:'smooth'}); }\n"
        "    else scrollTo({top:sheets[i-1].offsetTop-58,behavior:'smooth'});\n"
        "  }",
        "if(e.key==='ArrowRight'||e.key==='PageDown'){\n"
        "    e.preventDefault();\n"
        "    if(i>=0 && i===sheets.length-1){ bkGo('next'); return; }\n"
        "    var n=sheets[i+1]||sheets[0];\n"
        "    if(i<0) n=sheets[0]; scrollTo({top:n.offsetTop-58,behavior:'smooth'});\n"
        "  } else if(e.key==='ArrowLeft'||e.key==='PageUp'){\n"
        "    e.preventDefault();\n"
        "    if(i===0){ bkGo('prev'); return; }\n"
        "    if(i<0){ scrollTo({top:0,behavior:'smooth'}); }\n"
        "    else scrollTo({top:sheets[i-1].offsetTop-58,behavior:'smooth'});\n"
        "  }")
    if js == before:
        raise ValueError('键盘翻页替换未命中，book.html 的脚本可能已变')

    # 3. 跨文件跳转 + 首屏定位（原来的 ?at= 调试钩子保留）
    js += r'''

/* ================= 跨文件翻页 ================= */
var BK_FILES = %s;
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
''' % chapter_files

    # 4. 侧栏当前章高亮：分章版靠本页 data-ch 直接点亮
    js += r'''
/* 当前文件所属章：直接点亮，不必等滚动 */
(function(){
  var s = document.querySelector('.bk-sheet');
  if(!s) return;
  var ci = +s.dataset.ch;
  document.querySelectorAll('.bk-nav-ch').forEach(function(n){
    n.classList.toggle('on', +n.dataset.ch === ci);
  });
})();
'''
    return js


# ============================================================
# 五、页面模板
# ============================================================
PAGE = u'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="assets/book.css">
</head>
<body>

{side}

{top}
<div id="bk-bar"><i></i></div>

<main id="bk-main"><div class="bk-wrap">
{body}
</div></main>

<button id="bk-up" onclick="scrollTo({{top:0,behavior:'smooth'}})" title="回到顶部">↑</button>

<script src="assets/book.js"></script>
</body>
</html>
'''

REDIRECT = u'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url=index.html">
<title>AI Agent 实战手册</title>
</head>
<body><p>全书已拆成分章版，正在跳转…… 若未自动跳转请点 <a href="index.html">这里</a>。</p></body>
</html>
'''


FRESHEN = [
    # 扉页：不再是单文件了
    (u'<div><b>1</b><span>个文件</span></div>',
     u'<div><b>9</b><span>个页面</span></div>'),
    (u'全书为单一 HTML 文件，离线可读，浏览器 <code>Ctrl</code>+<code>F</code> 可全书搜索。',
     u'全书按章拆分，每章单独一页，打开快、改起来也清爽；'
     u'浏览器 <code>Ctrl</code>+<code>F</code> 在当前章内搜索。'),
    # 版权页：清掉本仓库里并不存在的文件与作者机器上的本地路径
    (u'    原始文件保留于 <code>C:\\Users\\think\\WorkBuddy\\aippt2~7、aipp4</code>'
     u' 与 <code>D:\\文档\\aippt</code>，未做改动。<br>\n'
     u'    版本记录见 <code>VERSIONS.md</code>　｜　整合版 v2 · 2026-08-03',
     u'    每页原为 16:9 幻灯片；内容超过一页高度的，会自动等比缩放以保证不被裁切。<br>\n'
     u'    配套脚本见 <a href="appendix.html">附录</a>，源码同时放在 <code>scripts/</code> 目录下。'
     u'　｜　整合版 v2 · 分章版'),
]


def freshen(html):
    """改掉拆分后已经不成立的表述"""
    for old, new in FRESHEN:
        if old not in html:
            raise ValueError('待替换文本未命中，book.html 可能已变：%s' % old[:40])
        html = html.replace(old, new)
    return html


def pager(prev, nxt, names):
    """章末上下章导航"""
    out = ['<nav class="bk-pager">']
    if prev:
        out.append('<a class="prev" href="%s"><small>← 上一章</small><b>%s</b></a>'
                   % (prev, names[prev]))
    else:
        out.append('<span class="sp"></span>')
    if nxt:
        out.append('<a class="next" href="%s"><small>下一章 →</small><b>%s</b></a>'
                   % (nxt, names[nxt]))
    else:
        out.append('<span class="sp"></span>')
    out.append('</nav>')
    return '\n'.join(out)


# ============================================================
# 六、组装
# ============================================================
def main():
    src = io.open(SRC, encoding='utf-8').read()
    if 'bk-sheet' not in src:
        sys.exit('book.html 已是跳转页，不是可拆的全书。先从 git 取回原件：\n'
                 '  git show 3d94a69:ha2fde-book/book.html > ha2fde-book/book.html')
    part = parse(src)
    sheets = part['sheets']
    chs = sorted(sheets)
    p2f = page_to_file(sheets)

    # 各章标题（从章扉页里取）
    names = {'index.html': '扉页与目录', 'appendix.html': '附录 · 配套代码'}
    for ch in chs:
        opener = sheets[ch][0]
        t = re.search(r'<h1>(.*?)<small>(.*?)</small></h1>', opener)
        names['ch%02d.html' % ch] = ('第 %d 章 %s — %s' % (ch, t.group(1), t.group(2))
                                     if t else '第 %d 章' % ch)

    order = ['index.html'] + ['ch%02d.html' % c for c in chs] + ['appendix.html']

    if not os.path.isdir(ASSETS):
        os.makedirs(ASSETS)

    # --- assets ---
    io.open(os.path.join(ASSETS, 'book.css'), 'w', encoding='utf-8').write(
        part['css'].rstrip() + '\n' + FIT_CSS)
    io.open(os.path.join(ASSETS, 'book.js'), 'w', encoding='utf-8').write(
        build_js(part['js'], repr(order).replace("'", '"')))

    written = []

    def emit(fname, title, body):
        html = PAGE.format(title=title,
                           side=rewrite_links(part['side'], p2f, fname),
                           top=part['top'],
                           body=rewrite_links(body, p2f, fname))
        io.open(os.path.join(HERE, fname), 'w', encoding='utf-8').write(html)
        written.append((fname, len(html.encode('utf-8'))))

    # --- 目录页 ---
    emit('index.html', 'AI Agent 实战手册 · 目录',
         freshen(part['cover'] + '\n' + part['toc'] + '\n' + part['colophon']))

    # --- 七章 ---
    for ch in chs:
        f = 'ch%02d.html' % ch
        prev = order[order.index(f) - 1]
        nxt = order[order.index(f) + 1]
        body = '\n'.join(sheets[ch]) + '\n' + pager(prev, nxt, names)
        emit(f, '%s · AI Agent 实战手册' % names[f], body)

    # --- 附录 ---
    emit('appendix.html', '附录 · 配套代码 · AI Agent 实战手册',
         part['apx'] + '\n' + pager('ch%02d.html' % chs[-1], None, names))

    # --- 旧链接跳转 ---
    io.open(os.path.join(HERE, 'book.html'), 'w', encoding='utf-8').write(REDIRECT)

    print('拆分完成，共 %d 页 / %d 章：' % (len(p2f), len(chs)))
    for f, n in written:
        print('  %-16s %7.1f KB' % (f, n / 1024.0))
    for f in ('assets/book.css', 'assets/book.js'):
        print('  %-16s %7.1f KB' % (f, os.path.getsize(os.path.join(HERE, f)) / 1024.0))


if __name__ == '__main__':
    main()
