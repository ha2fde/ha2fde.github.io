#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐页测量幻灯片溢出。用法：python3 audit.py ch1.html [ch2.html ...]"""
import os, re, subprocess, sys, tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SIZES = [(1920, 1080), (1400, 900), (980, 660)]

PROBE = r"""
<div id="__AUDIT__" style="display:none"></div>
<script>
window.addEventListener('load', function(){
  setTimeout(function(){
    var out=[], slides=document.querySelectorAll('.slide');
    for(var i=0;i<slides.length;i++){
      for(var j=0;j<slides.length;j++){ slides[j].classList.remove('on'); }
      slides[i].classList.add('on');
      var b=slides[i].querySelector('.bd'), vo=0, ho=0, who='';
      if(b){
        vo=b.scrollHeight-b.clientHeight;
        var els=b.querySelectorAll('*');
        for(var k=0;k<els.length;k++){
          var el=els[k];
          if(el.closest('svg')) continue;
          var d=el.scrollWidth-el.clientWidth;
          if(d>ho){ ho=d; who=(typeof el.className==='string'?el.className:'')||el.tagName; }
        }
      }
      if(vo>1||ho>1){ out.push('P'+(i+1)+' V+'+vo+' H+'+ho+' <'+who+'>'); }
    }
    document.getElementById('__AUDIT__').textContent =
      'TOTAL='+slides.length+' '+(out.length ? 'OVERFLOW :: '+out.join(' :: ') : 'ALL-CLEAR');
  }, 250);
});
</script>
"""

RE_OUT = re.compile(r'id="__AUDIT__"[^>]*>(.*?)</div>', re.S)


def run(path, w, h):
    src = open(path, encoding="utf-8").read()
    if "</body>" not in src:
        return "NO </body>"
    probed = src.replace("</body>", PROBE + "</body>")
    fd, tmp = tempfile.mkstemp(suffix=".html", dir=os.path.dirname(os.path.abspath(path)))
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(probed)
    try:
        r = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--virtual-time-budget=5000", "--window-size=%d,%d" % (w, h),
             "--dump-dom", "file://" + tmp],
            capture_output=True, text=True, timeout=120)
        m = RE_OUT.search(r.stdout)
        return m.group(1).strip() if m else "NO-RESULT"
    finally:
        os.unlink(tmp)


def links(path):
    """检查有没有外部资源引用（正文 <a href> 不算）"""
    src = open(path, encoding="utf-8").read()
    bad = []
    for pat in [r'<script[^>]+src\s*=', r'<link[^>]+href\s*=', r'<img[^>]+src\s*=',
                r'@import', r'url\(\s*["\']?https?:']:
        for m in re.finditer(pat, src, re.I):
            seg = src[m.start():m.start() + 90].replace("\n", " ")
            bad.append(seg)
    return bad


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(
        f for f in os.listdir(".") if re.match(r"ch\d\.html$", f))
    fail = 0
    for f in files:
        print("=" * 68)
        print(f)
        for w, h in SIZES:
            res = run(f, w, h)
            flag = "OK " if "ALL-CLEAR" in res else "!! "
            if "ALL-CLEAR" not in res:
                fail += 1
            print("  %s%dx%-5d %s" % (flag, w, h, res))
        b = links(f)
        print("  %s外部资源引用：%s" % ("!! " if b else "OK ", b if b else "无"))
        if b:
            fail += 1
    print("=" * 68)
    print("FAIL" if fail else "ALL FILES CLEAR")
