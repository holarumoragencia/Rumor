#!/usr/bin/env python3
"""Empaqueta artefacto/index.html (la checklist publicada) en artefacto.js con un reloj virtual inyectado,
para poder grabarlo cuadro por cuadro de forma exacta desde index.html."""
import json, os
D = os.path.dirname(os.path.abspath(__file__)) + '/..'
html = open(D + '/artefacto/index.html', encoding='utf-8').read()
SHIM = r'''<script>
(function(){
  /* Reloj virtual: setTimeout, requestAnimationFrame y performance.now avanzan solo cuando el reel lo pide */
  var VT = 0, q = [], tid = 1, raf = {}, rid = 1;
  window.__vt = {
    now: function(){ return VT; },
    hook: null,
    advanceTo: function(target){
      for(;;){
        q.sort(function(a,b){ return a.t - b.t || a.id - b.id; });
        var n = q[0]; if (!n || n.t > target) break;
        q.shift(); VT = n.t; try { n.fn(); } catch(e) { console.error(e); }
        if (window.__vt.hook) window.__vt.hook(VT);
      }
      VT = Math.max(VT, target);
      var r = raf; raf = {}; for (var k in r) { try { r[k](VT); } catch(e) { console.error(e); } }
    }
  };
  window.setTimeout = function(fn, ms){ var id = tid++; q.push({ id: id, t: VT + (+ms || 0), fn: fn }); return id; };
  window.clearTimeout = function(id){ q = q.filter(function(x){ return x.id !== id; }); };
  window.requestAnimationFrame = function(f){ var id = rid++; raf[id] = f; return id; };
  window.cancelAnimationFrame = function(id){ delete raf[id]; };
  performance.now = function(){ return VT; };
  Element.prototype.scrollTo = function(o){ if (o && typeof o === 'object') { if ('left' in o) this.scrollLeft = o.left; if ('top' in o) this.scrollTop = o.top; } };
  try { Object.defineProperty(window, 'localStorage', { value: { getItem: function(){ return null; }, setItem: function(){} } }); } catch(e) {}
  try { Object.defineProperty(navigator, 'vibrate', { value: function(){ return true; } }); } catch(e) {}
})();
</script>
<style>.toast{display:none!important} html,body{overflow:hidden!important}</style>
'''
out = html.replace('<head>', '<head>' + SHIM, 1)  # después del doctype, para no caer en modo quirks
open(D + '/artefacto.js', 'w', encoding='utf-8').write('// Generado por tools/build_artefacto.py\nwindow.ARTEFACTO_HTML = ' + json.dumps(out, ensure_ascii=False) + ';\n')
print('artefacto.js', len(out))
