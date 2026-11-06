(() => {
  'use strict';
  const data = window.ATLAS;
  const boundaries = window.ATLAS_BOUNDARIES;
  if (!data || !boundaries) return;
  const $ = s => document.querySelector(s);
  const $$ = s => [...document.querySelectorAll(s)];
  const photos = new Map(data.photos.map(p => [p.id, p]));
  const imagePath = id => photos.get(id)?.url || `photos/${id}.webp`;
  const pad = n => String(n).padStart(2, '0');
  // Fallback is an explicitly approximate silhouette until GeoAtlas loads.
  boundaries.henan = {type:'Polygon',coordinates:[[[111.0,34.9],[111.6,35.7],[112.8,36.3],[114.3,36.5],[115.4,35.8],[116.5,35.0],[116.6,33.6],[115.8,32.2],[115.0,31.4],[113.8,31.4],[112.9,32.3],[111.2,33.4],[110.3,34.1],[111.0,34.9]]]};
  let currentTrip = 'gansu';
  let currentPlace = '';
  let currentGallery = 'gansu';
  let lightboxPhotos = [];
  let lightboxIndex = 0;
  let lastFocus = null;
  let lastTouch = null;

  function animate(el) {
    el.classList.remove('is-fading');
    void el.offsetWidth;
    el.classList.add('is-fading');
  }

  function allCoordinates(geometry) {
    const polygons = geometry.type === 'MultiPolygon' ? geometry.coordinates : [geometry.coordinates];
    return {polygons, flat:polygons.flat(2)};
  }

  function renderMap(tripId) {
    const trip = data.trips[tripId];
    const {polygons, flat} = allCoordinates(boundaries[tripId]);
    const xs = flat.map(p => p[0]), ys = flat.map(p => p[1]);
    const minLon = Math.min(...xs), maxLon = Math.max(...xs);
    const minLat = Math.min(...ys), maxLat = Math.max(...ys);
    const centerLat = (minLat + maxLat) / 2;
    const lonFactor = Math.cos(centerLat * Math.PI / 180);
    const width = 720, height = 465, margin = 44;
    const scale = Math.min((width - 2 * margin) / ((maxLon - minLon) * lonFactor), (height - 2 * margin) / (maxLat - minLat));
    const xOffset = (width - (maxLon - minLon) * lonFactor * scale) / 2;
    const yOffset = (height - (maxLat - minLat) * scale) / 2;
    const project = ([lon,lat]) => [xOffset + (lon - minLon) * lonFactor * scale, height - yOffset - (lat - minLat) * scale];
    const d = polygons.map(poly => poly.map(ring => ring.map((p,i) => `${i ? 'L' : 'M'}${project(p).map(v=>v.toFixed(2)).join(',')}`).join(' ') + 'Z').join(' ')).join(' ');
    let grid = '';
    const gridStep = tripId === 'gansu' ? 2 : 2;
    for (let lon = Math.ceil(minLon / gridStep) * gridStep; lon <= maxLon; lon += gridStep) {
      const x = project([lon,minLat])[0];
      grid += `<line class="map-grid" x1="${x}" x2="${x}" y1="24" y2="440"/><text class="map-grid-label" x="${x+4}" y="455">${lon}° E</text>`;
    }
    for (let lat = Math.ceil(minLat / gridStep) * gridStep; lat <= maxLat; lat += gridStep) {
      const y = project([minLon,lat])[1];
      grid += `<line class="map-grid" x1="22" x2="698" y1="${y}" y2="${y}"/><text class="map-grid-label" x="4" y="${y-5}">${lat}°</text>`;
    }
    const routeOrder = trip.indexLine || ['jinci','taiyuan','yungang','xuankong','yingxian','yanmen','wutai'];
    const route = routeOrder.map(id => project(trip.points.find(p => p.id === id).coord));
    const routePath = route.map((p,i) => `${i ? 'L' : 'M'}${p.join(',')}`).join(' ');
    const neighbors = trip.neighbors.map(p => { const [x,y] = project(p.coord); return `<text class="neighbor-label" x="${x}" y="${y}" text-anchor="middle">${p.name}</text>`; }).join('');
    const provinceLabel = project(trip.provinceLabel);
    const compact = window.matchMedia('(max-width:600px)').matches;
    const preferredOffsets = {
      gansu: {lanzhou:[28,20],wuwei:[26,-16],tiantishan:[35,18],wushaoling:[-28,22],zhangye:[-30,-18],pingshanhu:[30,-28],jiayuguan:[30,-18],mingshashan:[-34,22],dunhuang:[-30,-20],suoyang:[30,22]},
      shanxi: {taiyuan:[34,-14],yanqiu:[-34,-20],tianlongshan:[-48,4],jinci:[-30,34],wangjia:[-34,-18],yungang:[-36,-20],xuankong:[38,-8],yingxian:[-36,18],yanmen:[-40,34],wutai:[38,25]},
      henan: {longmen:[-34,-24],erlitou:[34,20],huanghe:[-38,-18],hulao:[36,-24],kaifeng:[36,22],yinxu:[34,-20],songyang:[-36,24],taihang:[38,-22],wangxiang:[-40,20],taohua:[42,34]}
    };
    const labelBoxes = [];
    const occupied = (box) => labelBoxes.some(b => !(box.right < b.left-5 || box.left > b.right+5 || box.bottom < b.top-5 || box.top > b.bottom+5));
    const placeLabel = (p, x, y) => {
      const preferred = preferredOffsets[tripId]?.[p.id] || p.label || [28,-18];
      const candidates = [preferred,[-preferred[0],preferred[1]],[preferred[0],-preferred[1]],[-preferred[0],-preferred[1]],[0,-34],[0,34],[54,0],[-54,0],[60,-30],[-60,30],[0,-50],[0,50]];
      const textWidth = Math.max(22, [...p.name].length * (compact ? 8.2 : 9.1));
      let chosen = null;
      for (const [dx,dy] of candidates) {
        const anchor = dx < -8 ? 'end' : dx > 8 ? 'start' : 'middle';
        const left = x+dx-(anchor==='end'?textWidth:anchor==='middle'?textWidth/2:0);
        const box = {left, right:left+textWidth, top:y+dy-8, bottom:y+dy+8};
        if (box.left>8 && box.right<712 && box.top>25 && box.bottom<440 && !occupied(box)) { chosen={dx,dy,anchor,box}; break; }
      }
      if (!chosen) {
        const [dx,dy]=preferred;
        const anchor=dx<0?'end':'start';
        const left=x+dx-(anchor==='end'?textWidth:0);
        chosen={dx,dy,anchor,box:{left,right:left+textWidth,top:y+dy-8,bottom:y+dy+8}};
      }
      labelBoxes.push(chosen.box);
      return chosen;
    };
    const markers = trip.points.map(p => {
      const [x,y] = project(p.coord);
      const label = placeLabel(p,x,y);
      const {dx,dy,anchor}=label;
      return `<g class="map-marker" role="button" tabindex="0" aria-label="查看${p.name}的照片与介绍" aria-pressed="false" data-place="${p.id}" transform="translate(${x},${y})"><circle class="map-hit" r="18"/><line class="marker-leader" x1="0" y1="0" x2="${dx*.78}" y2="${dy*.75}"/><circle class="marker-halo" r="11"/><circle class="marker-dot" r="4"/><text class="marker-label" x="${dx}" y="${dy}" dominant-baseline="middle" text-anchor="${anchor}">${p.name}</text></g>`;
    }).join('');
    const scaleKm = tripId === 'gansu' ? 200 : 100;
    const scalePixels = scaleKm / 111.2 * scale;
    $('#province-map').innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="group" aria-labelledby="province-title province-description"><title id="province-title">${trip.kicker}旅行地点地图</title><desc id="province-description">真实省界上的旅行影像地点。可用 Tab 选择地名，按回车或空格查看。连线只表示地点关系。</desc><defs><pattern id="map-hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><line x1="0" x2="0" y1="0" y2="9" stroke="#afbf9e" stroke-width="1"/></pattern></defs>${grid}${neighbors}<path class="province-shadow" d="${d}"/><path class="province-outline" d="${d}" fill-rule="evenodd"/><path class="province-hatch" d="${d}" fill-rule="evenodd"/><text class="province-title" x="${provinceLabel[0]}" y="${provinceLabel[1]}" text-anchor="middle">${tripId==='gansu'?'甘 肃':tripId==='shanxi'?'山 西':'河 南'}</text><path class="map-route" d="${routePath}"/>${markers}<g transform="translate(672,43)" aria-hidden="true"><text class="north-label" text-anchor="middle" y="-12">N</text><path class="north-line" d="M0 31V0M-5 9 0 0 5 9" fill="none"/></g><g transform="translate(39,424)" aria-hidden="true"><path class="scale-line" d="M0 -5V0H${scalePixels}V-5" fill="none"/><text class="scale-label" x="0" y="15">${scaleKm} km</text></g></svg>`;
    $('#province-map').setAttribute('aria-label', `${trip.kicker}旅行地点地图`);
    $('#map-kicker').textContent = trip.kicker;
    $('#map-scale').textContent = trip.year;
    $('.map-footnote').textContent = tripId==='henan' && !window.henanBoundaryVerified ? '河南省界加载中或不可用时显示概略轮廓；地点坐标仅供行前参考，不用于导航。' : '省域地理示意 · 连线用于定位地点，不代表实际道路或完整行程。';
    $$('#province-map [data-place]').forEach(marker => {
      marker.addEventListener('click', () => selectPlace(marker.dataset.place));
      marker.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault(); selectPlace(marker.dataset.place);
        }
      });
    });
  }

  function selectPlace(placeId, shouldAnimate = true) {
    const trip = data.trips[currentTrip];
    const placeIndex = trip.points.findIndex(p => p.id === placeId);
    if (placeIndex === -1) return;
    currentPlace = placeId;
    const p = trip.points[placeIndex];
    const photo = photos.get(p.photo);
    $('#place-counter').textContent = `PLACE ${pad(placeIndex+1)} / ${pad(trip.points.length)}`;
    $('#place-detail').innerHTML = `<div class="place-top"><span class="place-name">${p.name}</span><span class="place-english">${p.en}</span></div><button class="place-photo" type="button" data-open-photo="${photo.id}" aria-label="查看${photo.title}大图"><img src="${imagePath(photo.id)}" alt="${photo.alt}" width="${photo.width}" height="${photo.height}"></button><p class="place-tag">${p.tag}</p><h3 class="place-headline">${p.title}</h3><p class="place-body">${p.body}</p>${p.source?`<a class="place-source" href="${p.source}" target="_blank" rel="noopener noreferrer">${p.sourceLabel || '文化背景 · UNESCO'} ↗</a>`:''}`;
    $$('[data-place]').forEach(el => {
      const selected = el.dataset.place === placeId;
      el.classList.toggle('is-selected', selected);
      el.setAttribute('aria-pressed', String(selected));
    });
    if (shouldAnimate) animate($('#place-detail'));
  }

  function setTrip(tripId, updateGallery = true) {
    if (!data.trips[tripId]) return;
    currentTrip = tripId;
    const trip = data.trips[tripId];
    $$('[data-trip]').forEach(b => { const selected = b.dataset.trip === tripId; b.classList.toggle('is-active',selected); b.setAttribute('aria-pressed',String(selected)); });
    $('#place-switcher').innerHTML = trip.points.map(p => `<button type="button" data-place="${p.id}" aria-pressed="false">${p.name}</button>`).join('');
    $$('#place-switcher button').forEach(b => b.addEventListener('click', () => selectPlace(b.dataset.place)));
    renderMap(tripId);
    selectPlace(trip.defaultPlace, false);
    $('#geo-label').textContent = trip.geoLabel;
    $('#geography-copy').textContent = trip.geography;
    $('#geography-source').href = trip.source;
    if (updateGallery) setGallery(tripId);
  }

  function setGallery(tripId) {
    if (!data.trips[tripId]) return;
    currentGallery = tripId;
    const trip = data.trips[tripId];
    $$('[data-gallery]').forEach(b => b.setAttribute('aria-pressed',String(b.dataset.gallery === tripId)));
    $('#frames-heading').textContent = trip.title;
    $('#gallery-intro').textContent = trip.intro;
    $('#gallery-footnote').textContent = tripId==='henan'?'2027 为行前参考影像，非本人实拍；点击照片查看大图。摄影来源及授权请通过地点介绍中的链接核对。':'照片由我在旅途中拍摄。点击照片可查看大图，使用左右方向键切换。';
    const galleryPhotos = data.photos.filter(p => p.trip===tripId).sort((a,b) => tripId==='henan' ? (a.id==='HN_03'?-1:b.id==='HN_03'?1:0) : 0);
    $('#photo-grid').classList.toggle('is-henan', tripId==='henan');
    $('#frames-heading').textContent = tripId==='gansu'?'十帧河西，留住一个秋天。':tripId==='shanxi'?'十帧山西，走近古建与山河。':'十帧中原，从黄河走向太行。';
    $('#photo-grid').innerHTML = galleryPhotos.map((p,i) => `<figure class="frame${tripId==='henan'&&p.id==='HN_03'?' frame-feature':''}"><button type="button" data-open-photo="${p.id}" aria-label="查看${p.title}大图"><img src="${imagePath(p.id)}" alt="${p.alt}" width="${p.width}" height="${p.height}" loading="lazy" decoding="async"></button><figcaption><span class="frame-title">${p.title}</span><span class="frame-number">${pad(i+1)}</span></figcaption><span class="frame-subtitle">${p.subtitle}</span></figure>`).join('');
  }

  const lightbox = $('#lightbox');
  function openPhoto(photoId, opener) {
    const p = photos.get(photoId);
    if (!p) return;
    lightboxPhotos = data.photos.filter(photo => photo.trip === p.trip);
    lightboxIndex = lightboxPhotos.findIndex(photo => photo.id === p.id);
    lastFocus = opener || document.activeElement;
    updatePhoto();
    if (!lightbox.open) {
      lightbox.showModal();
      document.body.style.overflow = 'hidden';
      $('.lightbox-close').focus();
    }
  }
  function updatePhoto() {
    const p = lightboxPhotos[lightboxIndex];
    $('#lightbox-image').src = imagePath(p.id);
    $('#lightbox-image').alt = p.alt;
    $('#lightbox-caption').textContent = `${p.title} · ${data.trips[p.trip].year}`;
    $('#lightbox-count').textContent = `${pad(lightboxIndex+1)} / ${pad(lightboxPhotos.length)}`;
    $('#lightbox-title').textContent = p.trip==='gansu'?'甘肃 · 河西走廊':p.trip==='shanxi'?'山西 · 古建与山河':'河南 · 行前预览';
  }
  function stepPhoto(delta) {
    if (!lightboxPhotos.length) return;
    lightboxIndex = (lightboxIndex + delta + lightboxPhotos.length) % lightboxPhotos.length;
    updatePhoto();
  }
  document.addEventListener('click', e => {
    const opener = e.target.closest('[data-open-photo]');
    if (opener) openPhoto(opener.dataset.openPhoto, opener);
  });
  $('#photo-prev').addEventListener('click', () => stepPhoto(-1));
  $('#photo-next').addEventListener('click', () => stepPhoto(1));
  $('.lightbox-close').addEventListener('click', () => lightbox.close());
  lightbox.addEventListener('click', e => { if (e.target===lightbox || e.target.classList.contains('lightbox-stage')) lightbox.close(); });
  lightbox.addEventListener('close', () => {
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.isConnected) lastFocus.focus({preventScroll:true});
  });
  document.addEventListener('keydown', e => {
    if (!lightbox.open) return;
    if (e.key==='ArrowLeft') { e.preventDefault(); stepPhoto(-1); }
    if (e.key==='ArrowRight') { e.preventDefault(); stepPhoto(1); }
  });
  $('#lightbox-image').addEventListener('touchstart', e => { if(e.touches.length===1) lastTouch=e.touches[0].clientX; }, {passive:true});
  $('#lightbox-image').addEventListener('touchend', e => {
    if (lastTouch===null) return;
    const distance=e.changedTouches[0].clientX-lastTouch;
    if (Math.abs(distance)>55) stepPhoto(distance>0?-1:1);
    lastTouch=null;
  },{passive:true});
  $$('[data-trip]').forEach(b => b.addEventListener('click', () => setTrip(b.dataset.trip)));
  $$('[data-trip-link]').forEach(a => a.addEventListener('click', () => setTrip(a.dataset.tripLink)));
  $$('[data-gallery]').forEach(b => b.addEventListener('click', () => {
    // Keep the map and photo region consistent when switching via the album controls.
    setTrip(b.dataset.gallery);
  }));
  $$('[data-gallery-link]').forEach(a => a.addEventListener('click', () => setTrip(a.dataset.galleryLink)));
  window.matchMedia('(max-width:600px)').addEventListener('change', () => {
    renderMap(currentTrip);
    selectPlace(currentPlace, false);
  });
  // Load the real Henan province boundary when available, then redraw the active map.
  fetch('https://geo.datav.aliyun.com/areas_v3/bound/410000.json')
    .then(r => { if (!r.ok) throw Error('GeoAtlas unavailable'); return r.json(); })
    .then(geo => {
      const geometry = geo.features?.[0]?.geometry;
      if (geometry && ['Polygon','MultiPolygon'].includes(geometry.type)) {
        boundaries.henan = geometry;
        window.henanBoundaryVerified = true;
        if (currentTrip === 'henan') { renderMap('henan'); selectPlace(currentPlace,false); }
      }
    }).catch(() => { /* Approximate outline remains; never used for navigation. */ });
  setTrip(currentTrip);
})();
