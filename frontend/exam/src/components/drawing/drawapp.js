import { useState, useRef, useEffect, useCallback, forwardRef, useImperativeHandle } from "react";

// ─── Canvas constants ──────────────────────────────────────────────────────────
const A4_W = 794;
const A4_H = 1123;
const SCALE = 2;
const SHAPE_TOOLS = ["line","rectangle","circle","triangle","diamond","arrow","star","hexagon"];
const HANDLE_SIZE = 8;
const ROTATE_OFFSET = 28;

// ─── SVG tool icons ────────────────────────────────────────────────────────────
const ToolIcon = ({ id }) => {
  const p = { viewBox:"0 0 24 24", fill:"none", stroke:"currentColor", strokeWidth:"1.8",
               strokeLinecap:"round", strokeLinejoin:"round", width:17, height:17 };
  switch (id) {
    case "select":    return <svg {...p}><path d="M4 4l7 18 3-7 7-3z"/><line x1="14" y1="14" x2="20" y2="20"/></svg>;
    case "pen":       return <svg {...p}><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4z"/></svg>;
    case "eraser":    return <svg {...p}><path d="M20 20H7L3 16l13-13 6 6-2 11z"/><line x1="6" y1="17" x2="9" y2="14"/></svg>;
    case "line":      return <svg {...p}><line x1="5" y1="19" x2="19" y2="5"/></svg>;
    case "rectangle": return <svg {...p}><rect x="3" y="5" width="18" height="14" rx="1"/></svg>;
    case "circle":    return <svg {...p}><circle cx="12" cy="12" r="9"/></svg>;
    case "triangle":  return <svg {...p}><polygon points="12,3 22,21 2,21"/></svg>;
    case "diamond":   return <svg {...p}><polygon points="12,2 22,12 12,22 2,12"/></svg>;
    case "arrow":     return <svg {...p}><line x1="5" y1="12" x2="19" y2="12"/><polyline points="13,6 19,12 13,18"/></svg>;
    case "star":      return <svg {...p}><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>;
    case "hexagon":   return <svg {...p}><polygon points="12,3 20,8 20,16 12,21 4,16 4,8"/></svg>;
    case "text":      return <svg {...p}><polyline points="4,7 4,4 20,4 20,7"/><line x1="9" y1="20" x2="15" y2="20"/><line x1="12" y1="4" x2="12" y2="20"/></svg>;
    default:          return null;
  }
};

// ─── Unique ID ─────────────────────────────────────────────────────────────────
let _uid = 0;
const uid = () => `obj_${++_uid}`;

// ─── Bounding box helpers ──────────────────────────────────────────────────────
function getBBox(obj) {
  if (obj.type === "pen") {
    const xs = obj.points.map(p => p.x), ys = obj.points.map(p => p.y);
    return { x: Math.min(...xs), y: Math.min(...ys),
             w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) };
  }
  if (obj.type === "text") {
    return { x: obj.x, y: obj.y - obj.fontSize, w: obj.w || 120, h: obj.fontSize * 1.4 };
  }
  return {
    x: Math.min(obj.x1, obj.x2), y: Math.min(obj.y1, obj.y2),
    w: Math.abs(obj.x2 - obj.x1), h: Math.abs(obj.y2 - obj.y1),
  };
}

function getBBoxCenter(obj) {
  const b = getBBox(obj);
  return { cx: b.x + b.w / 2, cy: b.y + b.h / 2 };
}

function getGroupBBox(objs) {
  const all = objs.map(getBBox);
  const x = Math.min(...all.map(b => b.x));
  const y = Math.min(...all.map(b => b.y));
  const r = Math.max(...all.map(b => b.x + b.w));
  const bot = Math.max(...all.map(b => b.y + b.h));
  return { x, y, w: r - x, h: bot - y };
}

function getExportBounds(obj) {
  const base = getBBox(obj);
  const strokePad = Math.max(8, (obj.lineWidth || 2) * 4);

  if (!obj.rotation) {
    return {
      x: base.x - strokePad,
      y: base.y - strokePad,
      w: base.w + strokePad * 2,
      h: base.h + strokePad * 2,
    };
  }

  const { cx, cy } = getBBoxCenter(obj);
  const corners = [
    { x: base.x, y: base.y },
    { x: base.x + base.w, y: base.y },
    { x: base.x + base.w, y: base.y + base.h },
    { x: base.x, y: base.y + base.h },
  ].map(p => rotatePoint(p.x, p.y, cx, cy, obj.rotation));

  const minX = Math.min(...corners.map(p => p.x)) - strokePad;
  const minY = Math.min(...corners.map(p => p.y)) - strokePad;
  const maxX = Math.max(...corners.map(p => p.x)) + strokePad;
  const maxY = Math.max(...corners.map(p => p.y)) + strokePad;

  return {
    x: minX,
    y: minY,
    w: maxX - minX,
    h: maxY - minY,
  };
}

// ─── Rotate a point around a center ───────────────────────────────────────────
function rotatePoint(px, py, cx, cy, angle) {
  const cos = Math.cos(angle), sin = Math.sin(angle);
  const dx = px - cx, dy = py - cy;
  return { x: cx + dx * cos - dy * sin, y: cy + dx * sin + dy * cos };
}

// ─── Hit test: point in (possibly rotated) object ─────────────────────────────
function hitTest(obj, px, py) {
  const angle = -(obj.rotation || 0);
  const { cx, cy } = getBBoxCenter(obj);
  const { x: lx, y: ly } = rotatePoint(px, py, cx, cy, angle);
  const b = getBBox(obj);
  const pad = Math.max(8, (obj.lineWidth || 2) * 2);
  return lx >= b.x - pad && lx <= b.x + b.w + pad &&
         ly >= b.y - pad && ly <= b.y + b.h + pad;
}

// ─── Render a shape onto a canvas context (unchanged logic) ───────────────────
function renderShape(ctx, tool, x1, y1, x2, y2, doFill) {
  ctx.beginPath();
  switch (tool) {
    case "line":
      ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
      break;
    case "rectangle":
      ctx.rect(x1, y1, x2 - x1, y2 - y1);
      if (doFill) ctx.fill(); ctx.stroke();
      break;
    case "circle": {
      const rx = Math.abs(x2 - x1) / 2, ry = Math.abs(y2 - y1) / 2;
      ctx.ellipse(x1 + (x2-x1)/2, y1 + (y2-y1)/2, rx, ry, 0, 0, Math.PI*2);
      if (doFill) ctx.fill(); ctx.stroke();
      break;
    }
    case "triangle":
      ctx.moveTo((x1+x2)/2, y1); ctx.lineTo(x2, y2); ctx.lineTo(x1, y2); ctx.closePath();
      if (doFill) ctx.fill(); ctx.stroke();
      break;
    case "diamond": {
      const mx = (x1+x2)/2, my = (y1+y2)/2;
      ctx.moveTo(mx, y1); ctx.lineTo(x2, my); ctx.lineTo(mx, y2); ctx.lineTo(x1, my); ctx.closePath();
      if (doFill) ctx.fill(); ctx.stroke();
      break;
    }
    case "hexagon": {
      const cx = (x1+x2)/2, cy = (y1+y2)/2, r = Math.min(Math.abs(x2-x1), Math.abs(y2-y1)) / 2;
      for (let i = 0; i < 6; i++) {
        const a = (i * Math.PI) / 3 - Math.PI / 6;
        i === 0 ? ctx.moveTo(cx + r*Math.cos(a), cy + r*Math.sin(a))
                : ctx.lineTo(cx + r*Math.cos(a), cy + r*Math.sin(a));
      }
      ctx.closePath(); if (doFill) ctx.fill(); ctx.stroke();
      break;
    }
    case "arrow": {
      const dx = x2-x1, dy = y2-y1, ang = Math.atan2(dy, dx);
      const len = Math.hypot(dx, dy), hs = Math.max(10, Math.min(28, len * 0.28));
      ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(x2, y2);
      ctx.lineTo(x2 - hs*Math.cos(ang - Math.PI/7), y2 - hs*Math.sin(ang - Math.PI/7));
      ctx.lineTo(x2 - hs*Math.cos(ang + Math.PI/7), y2 - hs*Math.sin(ang + Math.PI/7));
      ctx.closePath(); ctx.fillStyle = ctx.strokeStyle; ctx.fill();
      break;
    }
    case "star": {
      const cx = (x1+x2)/2, cy = (y1+y2)/2;
      const or = Math.min(Math.abs(x2-x1), Math.abs(y2-y1)) / 2, ir = or * 0.42;
      for (let i = 0; i < 10; i++) {
        const r = i % 2 === 0 ? or : ir, a = (i * Math.PI) / 5 - Math.PI / 2;
        i === 0 ? ctx.moveTo(cx + r*Math.cos(a), cy + r*Math.sin(a))
                : ctx.lineTo(cx + r*Math.cos(a), cy + r*Math.sin(a));
      }
      ctx.closePath(); if (doFill) ctx.fill(); ctx.stroke();
      break;
    }
    default: break;
  }
}

// ─── Draw a single object to a context ────────────────────────────────────────
function drawObject(ctx, obj, alpha = 1) {
  ctx.save();
  const { cx, cy } = getBBoxCenter(obj);
  if (obj.rotation) {
    ctx.translate(cx, cy);
    ctx.rotate(obj.rotation);
    ctx.translate(-cx, -cy);
  }
  ctx.globalAlpha = (obj.opacity / 100) * alpha;
  ctx.strokeStyle = obj.strokeColor;
  ctx.fillStyle   = obj.fillColor || "rgba(0,0,0,0)";
  ctx.lineWidth   = obj.lineWidth;
  ctx.lineCap     = "round";
  ctx.lineJoin    = "round";
  const w = obj.lineWidth;
  ctx.setLineDash(
    obj.lineStyle === "dashed" ? [w*5, w*3] :
    obj.lineStyle === "dotted" ? [w*1, w*3] : []
  );

  if (obj.type === "pen") {
    ctx.beginPath();
    obj.points.forEach((p, i) => i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y));
    ctx.stroke();
  } else if (obj.type === "eraser") {
    ctx.globalCompositeOperation = "destination-out";
    ctx.strokeStyle = "rgba(0,0,0,1)";
    ctx.lineWidth   = obj.lineWidth * 8;
    ctx.setLineDash([]);
    ctx.beginPath();
    obj.points.forEach((p, i) => i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y));
    ctx.stroke();
    ctx.globalCompositeOperation = "source-over";
  } else if (obj.type === "text") {
    ctx.fillStyle = obj.strokeColor;
    ctx.font = `${obj.fontBold ? "bold " : ""}${obj.fontSize}px system-ui, sans-serif`;
    ctx.setLineDash([]);
    ctx.fillText(obj.text, obj.x, obj.y);
  } else if (SHAPE_TOOLS.includes(obj.type)) {
    renderShape(ctx, obj.type, obj.x1, obj.y1, obj.x2, obj.y2, obj.fillOn);
  }
  ctx.restore();
}

// ─── Render all objects sorted by zIndex ──────────────────────────────────────
function renderAll(ctx, objects) {
  ctx.clearRect(0, 0, A4_W, A4_H);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, A4_W, A4_H);
  const sorted = [...objects].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0));
  sorted.forEach(obj => drawObject(ctx, obj));
}

// ─── Selection handle positions ───────────────────────────────────────────────
function getHandles(bbox, rotation = 0) {
  const { x, y, w, h } = bbox;
  const cx = x + w / 2, cy = y + h / 2;
  const corners = [
    { id: "tl", x: x,     y: y },
    { id: "tr", x: x + w, y: y },
    { id: "br", x: x + w, y: y + h },
    { id: "bl", x: x,     y: y + h },
    { id: "tm", x: cx,    y: y },
    { id: "bm", x: cx,    y: y + h },
    { id: "lm", x: x,     y: cy },
    { id: "rm", x: x + w, y: cy },
  ];
  const rotHandle = { id: "rot", x: cx, y: y - ROTATE_OFFSET };
  const rotated = [...corners, rotHandle].map(h => {
    const rp = rotatePoint(h.x, h.y, cx, cy, rotation);
    return { ...h, x: rp.x, y: rp.y };
  });
  return rotated;
}

// ─── Main Component ────────────────────────────────────────────────────────────
const DrawingApp = forwardRef(function DrawingAppImpl(props, ref) {
  const mainRef    = useRef(null);
  const overlayRef = useRef(null);
  const uiCanvasRef = useRef(null);
  const textRef    = useRef(null);
  const inited     = useRef(false);
  const drawing    = useRef(false);
  const startP     = useRef({ x: 0, y: 0 });
  const lastP      = useRef({ x: 0, y: 0 });
  const hist       = useRef([]);
  const hIdx       = useRef(-1);

  // Object model
  const [objects, setObjects]       = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [groups, setGroups]         = useState({}); // groupId -> [objectIds]

  // Drag/rotate/resize interaction state
  const interactRef = useRef(null); // { type: "move"|"rotate"|"resize", startPos, startObjs, handle? }

  // ── UI state ──
  const [tool, setTool]           = useState("select");
  const [strokeColor, setStroke]  = useState("#1e1e1e");
  const [fillColor, setFill]      = useState("#3b82f6");
  const [fillOn, setFillOn]       = useState(false);
  const [lineWidth, setLW]        = useState(2);
  const [opacity, setOpacity]     = useState(100);
  const [lineStyle, setLS]        = useState("solid");
  const [zoom, setZoom]           = useState(0.85);
  const [grid, setGrid]           = useState(false);
  const [textPos, setTextPos]     = useState(null);
  const [textVal, setTextVal]     = useState("");
  const [fontSize, setFontSize]   = useState(18);
  const [fontBold, setFontBold]   = useState(false);
  const [curPos, setCurPos]       = useState({ x: 0, y: 0 });
  const [, forceRender]           = useState(0);

  // Refs for stale-closure-safe event handlers
  const rTool     = useRef(tool);     useEffect(() => { rTool.current = tool; }, [tool]);
  const rSC       = useRef(strokeColor); useEffect(() => { rSC.current = strokeColor; }, [strokeColor]);
  const rFC       = useRef(fillColor);   useEffect(() => { rFC.current = fillColor; }, [fillColor]);
  const rFillOn   = useRef(fillOn);      useEffect(() => { rFillOn.current = fillOn; }, [fillOn]);
  const rLW       = useRef(lineWidth);   useEffect(() => { rLW.current = lineWidth; }, [lineWidth]);
  const rOp       = useRef(opacity);     useEffect(() => { rOp.current = opacity; }, [opacity]);
  const rLS       = useRef(lineStyle);   useEffect(() => { rLS.current = lineStyle; }, [lineStyle]);
  const rFS       = useRef(fontSize);    useEffect(() => { rFS.current = fontSize; }, [fontSize]);
  const rBold     = useRef(fontBold);    useEffect(() => { rBold.current = fontBold; }, [fontBold]);
  const rObjects  = useRef(objects);     useEffect(() => { rObjects.current = objects; }, [objects]);
  const rSelected = useRef(selectedIds); useEffect(() => { rSelected.current = selectedIds; }, [selectedIds]);
  const rGroups   = useRef(groups);      useEffect(() => { rGroups.current = groups; }, [groups]);

  // ── Canvas init ──
  useEffect(() => {
    if (inited.current) return;
    inited.current = true;
    [mainRef, overlayRef, uiCanvasRef].forEach(r => {
      if (!r.current) return;
      r.current.width  = A4_W * SCALE;
      r.current.height = A4_H * SCALE;
      r.current.style.width  = A4_W + "px";
      r.current.style.height = A4_H + "px";
      r.current.getContext("2d").scale(SCALE, SCALE);
    });
    const mc = mainRef.current.getContext("2d");
    mc.fillStyle = "#ffffff"; mc.fillRect(0, 0, A4_W, A4_H);
    pushSnap([]);
  }, []);

  // ── Expose export method via imperative handle ──
  useImperativeHandle(ref, () => ({
    exportImage: () => {
      if (!mainRef.current) {
        return null;
      }

      if (!objects.length) {
        return {
          dataUrl: mainRef.current.toDataURL('image/png'),
          width: A4_W,
          height: A4_H,
        };
      }

      const exportPadding = 12;
      const bounds = objects
        .map(getExportBounds)
        .reduce((acc, box) => {
          if (!acc) return box;
          return {
            x: Math.min(acc.x, box.x),
            y: Math.min(acc.y, box.y),
            w: Math.max(acc.x + acc.w, box.x + box.w) - Math.min(acc.x, box.x),
            h: Math.max(acc.y + acc.h, box.y + box.h) - Math.min(acc.y, box.y),
          };
        }, null);

      if (!bounds) {
        return {
          dataUrl: mainRef.current.toDataURL('image/png'),
          width: A4_W,
          height: A4_H,
        };
      }

      const x = Math.max(0, Math.floor(bounds.x - exportPadding));
      const y = Math.max(0, Math.floor(bounds.y - exportPadding));
      const w = Math.min(A4_W - x, Math.ceil(bounds.w + exportPadding * 2));
      const h = Math.min(A4_H - y, Math.ceil(bounds.h + exportPadding * 2));

      const cropCanvas = document.createElement('canvas');
      cropCanvas.width = Math.max(1, Math.round(w * SCALE));
      cropCanvas.height = Math.max(1, Math.round(h * SCALE));

      const ctx = cropCanvas.getContext('2d');
      ctx.scale(SCALE, SCALE);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, w, h);
      ctx.translate(-x, -y);

      [...objects]
        .sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0))
        .forEach(obj => drawObject(ctx, obj));

      return {
        dataUrl: cropCanvas.toDataURL('image/png'),
        width: Math.max(1, Math.round(w)),
        height: Math.max(1, Math.round(h)),
      };
    },
    getCanvasData: () => ({
      width: A4_W,
      height: A4_H,
      objects: objects,
    }),
  }), [objects]);

  // ── Re-render main canvas when objects change ──
  useEffect(() => {
    const mc = mainRef.current?.getContext("2d");
    if (!mc) return;
    renderAll(mc, objects);
    drawSelectionUI();
  }, [objects, selectedIds]);

  // ── Draw selection handles on uiCanvas ────────────────────────────────────
  const drawSelectionUI = useCallback(() => {
    const uc = uiCanvasRef.current?.getContext("2d");
    if (!uc) return;
    uc.clearRect(0, 0, A4_W, A4_H);
    const sel = rSelected.current;
    if (!sel.length) return;
    const objs = rObjects.current.filter(o => sel.includes(o.id));
    if (!objs.length) return;

    const isMulti = objs.length > 1;
    const bbox = isMulti ? getGroupBBox(objs) : getBBox(objs[0]);
    const rotation = (!isMulti && objs[0].rotation) ? objs[0].rotation : 0;
    const cx = bbox.x + bbox.w / 2, cy = bbox.y + bbox.h / 2;

    uc.save();
    uc.translate(cx, cy);
    uc.rotate(rotation);
    uc.translate(-cx, -cy);

    // Dashed selection rect
    uc.strokeStyle = "#3b82f6";
    uc.lineWidth   = 1.5;
    uc.setLineDash([5, 3]);
    uc.strokeRect(bbox.x - 4, bbox.y - 4, bbox.w + 8, bbox.h + 8);
    uc.setLineDash([]);

    // Rotation line
    uc.strokeStyle = "#60a5fa";
    uc.lineWidth   = 1;
    uc.beginPath();
    uc.moveTo(bbox.x + bbox.w / 2, bbox.y - 4);
    uc.lineTo(bbox.x + bbox.w / 2, bbox.y - ROTATE_OFFSET + HANDLE_SIZE / 2);
    uc.stroke();

    // Handles
    const handles = getHandles(bbox, 0); // drawn in rotated space
    handles.forEach(h => {
      uc.fillStyle = h.id === "rot" ? "#facc15" : "#ffffff";
      uc.strokeStyle = h.id === "rot" ? "#ca8a04" : "#3b82f6";
      uc.lineWidth = 1.5;
      if (h.id === "rot") {
        uc.beginPath();
        uc.arc(h.x, h.y, HANDLE_SIZE / 2 + 1, 0, Math.PI * 2);
        uc.fill(); uc.stroke();
        // rotation icon
        uc.strokeStyle = "#92400e";
        uc.lineWidth = 1.5;
        uc.beginPath();
        uc.arc(h.x, h.y, 4, -Math.PI * 0.7, Math.PI * 0.7);
        uc.stroke();
      } else {
        uc.fillRect(h.x - HANDLE_SIZE/2, h.y - HANDLE_SIZE/2, HANDLE_SIZE, HANDLE_SIZE);
        uc.strokeRect(h.x - HANDLE_SIZE/2, h.y - HANDLE_SIZE/2, HANDLE_SIZE, HANDLE_SIZE);
      }
    });
    uc.restore();
  }, []);

  useEffect(() => { drawSelectionUI(); }, [selectedIds, objects]);

  // ── History ──
  const pushSnap = (objs) => {
    const snapshot = JSON.parse(JSON.stringify(objs));
    hist.current = hist.current.slice(0, hIdx.current + 1);
    hist.current.push(snapshot);
    if (hist.current.length > 60) hist.current.shift(); else hIdx.current++;
    forceRender(n => n + 1);
  };

  const undo = () => {
    if (hIdx.current <= 0) return;
    const prev = hist.current[--hIdx.current];
    setObjects(prev);
    setSelectedIds([]);
    forceRender(n => n + 1);
  };
  const redo = () => {
    if (hIdx.current >= hist.current.length - 1) return;
    const next = hist.current[++hIdx.current];
    setObjects(next);
    setSelectedIds([]);
    forceRender(n => n + 1);
  };

  // ── Coordinates ──
  const getPos = (e) => {
    const rect = overlayRef.current.getBoundingClientRect();
    const src  = e.touches ? e.touches[0] : e;
    return {
      x: (src.clientX - rect.left)  * (A4_W / rect.width),
      y: (src.clientY - rect.top)   * (A4_H / rect.height),
    };
  };

  // ── Find handle at position (in screen space, accounting for rotation) ────
  const findHandle = (px, py) => {
    const sel = rSelected.current;
    if (!sel.length) return null;
    const objs = rObjects.current.filter(o => sel.includes(o.id));
    if (!objs.length) return null;
    const isMulti = objs.length > 1;
    const bbox = isMulti ? getGroupBBox(objs) : getBBox(objs[0]);
    const rotation = (!isMulti && objs[0].rotation) ? objs[0].rotation : 0;
    const cx = bbox.x + bbox.w / 2, cy = bbox.y + bbox.h / 2;

    // Rotate test point into bbox's local space
    const local = rotatePoint(px, py, cx, cy, -rotation);
    const handles = getHandles(bbox, 0);
    for (const h of handles) {
      const dist = Math.hypot(h.x - local.x, h.y - local.y);
      if (dist <= HANDLE_SIZE + 3) return h.id;
    }
    return null;
  };

  // ── Find topmost object at position ──────────────────────────────────────
  const findObjectAt = (px, py) => {
    const objs = [...rObjects.current].sort((a,b) => (b.zIndex||0)-(a.zIndex||0));
    return objs.find(o => hitTest(o, px, py)) || null;
  };

  // ── Active drawing object (for pen/eraser strokes in progress) ────────────
  const activeObjRef = useRef(null);

  // ── Events ──
  const onDown = (e) => {
    e.preventDefault();
    const p = getPos(e);

    if (rTool.current === "text") {
      setTextPos(p); setTextVal("");
      setTimeout(() => textRef.current?.focus(), 10);
      return;
    }

    if (rTool.current === "select") {
      // Check handles first
      const handle = findHandle(p.x, p.y);
      if (handle) {
        const sel = rSelected.current;
        const objs = rObjects.current.filter(o => sel.includes(o.id));
        const isMulti = objs.length > 1;
        const bbox = isMulti ? getGroupBBox(objs) : getBBox(objs[0]);
        const cx = bbox.x + bbox.w / 2, cy = bbox.y + bbox.h / 2;
        const startObjs = JSON.parse(JSON.stringify(objs));
        if (handle === "rot") {
          interactRef.current = { type: "rotate", startPos: p, startObjs, cx, cy,
            startAngle: Math.atan2(p.y - cy, p.x - cx),
            initRotation: (!isMulti && objs[0].rotation) ? objs[0].rotation : 0 };
        } else {
          interactRef.current = { type: "resize", handle, startPos: p, startObjs, bbox };
        }
        return;
      }

      // Check if clicking on a selected object → move
      const clickedObj = findObjectAt(p.x, p.y);
      if (clickedObj && rSelected.current.includes(clickedObj.id)) {
        const objs = rObjects.current.filter(o => rSelected.current.includes(o.id));
        interactRef.current = { type: "move", startPos: p,
          startObjs: JSON.parse(JSON.stringify(objs)) };
        return;
      }

      // Click on unselected object
      if (clickedObj) {
        // Expand to group if it's grouped
        const grp = rGroups.current;
        let toSelect = [clickedObj.id];
        for (const [, members] of Object.entries(grp)) {
          if (members.includes(clickedObj.id)) { toSelect = [...members]; break; }
        }
        if (e.shiftKey) {
          setSelectedIds(prev => {
            const union = [...new Set([...prev, ...toSelect])];
            return union;
          });
        } else {
          setSelectedIds(toSelect);
        }
      } else {
        // Clicked empty space
        setSelectedIds([]);
      }
      return;
    }

    // Drawing tools
    drawing.current = true;
    startP.current  = p;
    lastP.current   = p;

    if (rTool.current === "pen" || rTool.current === "eraser") {
      activeObjRef.current = {
        id: uid(), type: rTool.current,
        points: [p],
        strokeColor: rSC.current,
        fillColor: rFillOn.current ? rFC.current : "rgba(0,0,0,0)",
        fillOn: rFillOn.current,
        lineWidth: rLW.current,
        opacity: rOp.current,
        lineStyle: rLS.current,
        rotation: 0,
        zIndex: rObjects.current.length,
      };
    }
  };

  const onMove = (e) => {
    e.preventDefault();
    const p = getPos(e);
    setCurPos({ x: Math.round(p.x), y: Math.round(p.y) });
    lastP.current = p;

    // Select mode interactions
    if (rTool.current === "select" && interactRef.current) {
      const iv = interactRef.current;

      if (iv.type === "move") {
        const dx = p.x - iv.startPos.x, dy = p.y - iv.startPos.y;
        const sel = rSelected.current;
        setObjects(prev => prev.map(o => {
          if (!sel.includes(o.id)) return o;
          const so = iv.startObjs.find(s => s.id === o.id);
          if (!so) return o;
          if (o.type === "pen" || o.type === "eraser") {
            return { ...o, points: so.points.map(pt => ({ x: pt.x+dx, y: pt.y+dy })) };
          }
          if (o.type === "text") return { ...o, x: so.x+dx, y: so.y+dy };
          return { ...o, x1: so.x1+dx, y1: so.y1+dy, x2: so.x2+dx, y2: so.y2+dy };
        }));
        return;
      }

      if (iv.type === "rotate") {
        const currentAngle = Math.atan2(p.y - iv.cy, p.x - iv.cx);
        const delta = currentAngle - iv.startAngle;
        const newRotation = iv.initRotation + delta;
        const sel = rSelected.current;
        setObjects(prev => prev.map(o =>
          sel.includes(o.id) ? { ...o, rotation: newRotation } : o
        ));
        return;
      }

      if (iv.type === "resize") {
        const { handle, startPos, startObjs, bbox } = iv;
        const dx = p.x - startPos.x, dy = p.y - startPos.y;
        const sel = rSelected.current;
        setObjects(prev => prev.map(o => {
          if (!sel.includes(o.id)) return o;
          const so = startObjs.find(s => s.id === o.id);
          if (!so || o.type === "pen" || o.type === "eraser" || o.type === "text") return o;
          let { x1, y1, x2, y2 } = so;
          if (handle.includes("r")) x2 = so.x2 + dx;
          if (handle.includes("l")) x1 = so.x1 + dx;
          if (handle.includes("b")) y2 = so.y2 + dy;
          if (handle.includes("t")) y1 = so.y1 + dy;
          if (handle === "rm") x2 = so.x2 + dx;
          if (handle === "lm") x1 = so.x1 + dx;
          if (handle === "bm") y2 = so.y2 + dy;
          if (handle === "tm") y1 = so.y1 + dy;
          return { ...o, x1, y1, x2, y2 };
        }));
        return;
      }
    }

    if (!drawing.current) return;
    const t = rTool.current;

    if ((t === "pen" || t === "eraser") && activeObjRef.current) {
      activeObjRef.current = {
        ...activeObjRef.current,
        points: [...activeObjRef.current.points, p],
      };
      // Live preview on main canvas
      const mc = mainRef.current.getContext("2d");
      renderAll(mc, [...rObjects.current, activeObjRef.current]);
      return;
    }

    if (SHAPE_TOOLS.includes(t)) {
      const oc = overlayRef.current.getContext("2d");
      oc.clearRect(0, 0, A4_W, A4_H);
      oc.save();
      oc.globalAlpha  = Math.min(rOp.current / 100, 0.72);
      oc.strokeStyle  = rSC.current;
      oc.fillStyle    = rFillOn.current ? rFC.current : "rgba(0,0,0,0)";
      oc.lineWidth    = rLW.current;
      oc.lineCap      = "round"; oc.lineJoin = "round";
      const w = rLW.current;
      oc.setLineDash(
        rLS.current === "dashed" ? [w*5, w*3] :
        rLS.current === "dotted" ? [w*1, w*3] : []
      );
      renderShape(oc, t, startP.current.x, startP.current.y, p.x, p.y, rFillOn.current);
      oc.restore();
    }
  };

  const onUp = (e) => {
    if (rTool.current === "select") {
      if (interactRef.current) {
        const type = interactRef.current.type;
        interactRef.current = null;
        if (type === "move" || type === "rotate" || type === "resize") {
          pushSnap(rObjects.current);
        }
      }
      return;
    }

    if (!drawing.current) return;
    drawing.current = false;
    const p = e.type === "mouseleave" ? lastP.current : getPos(e);
    const t = rTool.current;

    overlayRef.current.getContext("2d").clearRect(0, 0, A4_W, A4_H);

    let newObj = null;

    if ((t === "pen" || t === "eraser") && activeObjRef.current) {
      newObj = activeObjRef.current;
      activeObjRef.current = null;
    } else if (SHAPE_TOOLS.includes(t)) {
      newObj = {
        id: uid(), type: t,
        x1: startP.current.x, y1: startP.current.y, x2: p.x, y2: p.y,
        strokeColor: rSC.current,
        fillColor: rFillOn.current ? rFC.current : "rgba(0,0,0,0)",
        fillOn: rFillOn.current,
        lineWidth: rLW.current,
        opacity: rOp.current,
        lineStyle: rLS.current,
        rotation: 0,
        zIndex: rObjects.current.length,
      };
    }

    if (newObj) {
      const updated = [...rObjects.current, newObj];
      setObjects(updated);
      pushSnap(updated);
    }
  };

  const commitText = () => {
    if (!textPos) return;
    const v = textVal.trim();
    if (v) {
      // Measure text width
      const mc = mainRef.current.getContext("2d");
      mc.font = `${rBold.current ? "bold " : ""}${rFS.current}px system-ui, sans-serif`;
      const w = mc.measureText(v).width;
      const newObj = {
        id: uid(), type: "text",
        text: v, x: textPos.x, y: textPos.y,
        w, fontSize: rFS.current, fontBold: rBold.current,
        strokeColor: rSC.current,
        opacity: rOp.current,
        lineWidth: 1,
        lineStyle: "solid",
        rotation: 0,
        zIndex: rObjects.current.length,
        fillColor: "rgba(0,0,0,0)", fillOn: false,
      };
      const updated = [...rObjects.current, newObj];
      setObjects(updated);
      pushSnap(updated);
    }
    setTextPos(null); setTextVal("");
  };

  const clearCanvas = () => {
    setObjects([]);
    setSelectedIds([]);
    pushSnap([]);
  };

  const exportPNG = () => {
    const a = document.createElement("a");
    a.download = "drawing.png";
    a.href = mainRef.current.toDataURL("image/png");
    a.click();
  };

  // ── Z-Index controls ──────────────────────────────────────────────────────
  const bringForward = () => {
    if (!selectedIds.length) return;
    setObjects(prev => {
      const updated = prev.map(o =>
        selectedIds.includes(o.id) ? { ...o, zIndex: (o.zIndex || 0) + 1.5 } : o
      );
      const reindexed = reindex(updated);
      pushSnap(reindexed);
      return reindexed;
    });
  };
  const sendBackward = () => {
    if (!selectedIds.length) return;
    setObjects(prev => {
      const updated = prev.map(o =>
        selectedIds.includes(o.id) ? { ...o, zIndex: (o.zIndex || 0) - 1.5 } : o
      );
      const reindexed = reindex(updated);
      pushSnap(reindexed);
      return reindexed;
    });
  };
  const bringToFront = () => {
    if (!selectedIds.length) return;
    setObjects(prev => {
      const maxZ = Math.max(...prev.map(o => o.zIndex || 0));
      const updated = prev.map(o =>
        selectedIds.includes(o.id) ? { ...o, zIndex: maxZ + 1 } : o
      );
      const reindexed = reindex(updated);
      pushSnap(reindexed);
      return reindexed;
    });
  };
  const sendToBack = () => {
    if (!selectedIds.length) return;
    setObjects(prev => {
      const updated = prev.map(o =>
        selectedIds.includes(o.id) ? { ...o, zIndex: -1 } : o
      );
      const reindexed = reindex(updated);
      pushSnap(reindexed);
      return reindexed;
    });
  };

  const reindex = (objs) => {
    const sorted = [...objs].sort((a,b) => (a.zIndex||0)-(b.zIndex||0));
    return sorted.map((o, i) => ({ ...o, zIndex: i }));
  };

  // ── Group / Ungroup ───────────────────────────────────────────────────────
  const groupSelected = () => {
    if (selectedIds.length < 2) return;
    const gid = uid();
    setGroups(prev => ({ ...prev, [gid]: [...selectedIds] }));
  };

  const ungroupSelected = () => {
    const sel = selectedIds;
    setGroups(prev => {
      const next = { ...prev };
      for (const gid of Object.keys(next)) {
        if (next[gid].some(id => sel.includes(id))) {
          delete next[gid];
        }
      }
      return next;
    });
  };

  const getGroupForSelection = () => {
    for (const [gid, members] of Object.entries(groups)) {
      if (selectedIds.every(id => members.includes(id)) &&
          members.every(id => selectedIds.includes(id))) return gid;
    }
    return null;
  };

  // ── Delete selected ───────────────────────────────────────────────────────
  const deleteSelected = () => {
    if (!selectedIds.length) return;
    const updated = objects.filter(o => !selectedIds.includes(o.id));
    setObjects(reindex(updated));
    setSelectedIds([]);
    pushSnap(reindex(updated));
  };

  // ── Duplicate selected ────────────────────────────────────────────────────
  const duplicateSelected = () => {
    if (!selectedIds.length) return;
    const toDup = objects.filter(o => selectedIds.includes(o.id));
    const duped = toDup.map(o => ({
      ...JSON.parse(JSON.stringify(o)),
      id: uid(),
      zIndex: objects.length + toDup.indexOf(o),
      ...(o.type === "pen" || o.type === "eraser"
        ? { points: o.points.map(p => ({ x: p.x + 20, y: p.y + 20 })) }
        : o.type === "text"
        ? { x: o.x + 20, y: o.y + 20 }
        : { x1: o.x1 + 20, y1: o.y1 + 20, x2: o.x2 + 20, y2: o.y2 + 20 }),
    }));
    const updated = reindex([...objects, ...duped]);
    setObjects(updated);
    setSelectedIds(duped.map(o => o.id));
    pushSnap(updated);
  };

  // ── Keyboard shortcuts ──
  useEffect(() => {
    const h = (e) => {
      if (document.activeElement?.tagName === "INPUT") return;
      const ctrl = e.ctrlKey || e.metaKey;
      if (ctrl && e.key === "z" && !e.shiftKey) { e.preventDefault(); undo(); return; }
      if (ctrl && (e.key === "y" || (e.key === "z" && e.shiftKey))) { e.preventDefault(); redo(); return; }
      if (ctrl && e.key === "g") { e.preventDefault(); groupSelected(); return; }
      if (ctrl && e.key === "d") { e.preventDefault(); duplicateSelected(); return; }
      if (e.key === "Delete" || e.key === "Backspace") { deleteSelected(); return; }
      if (e.key === "Escape") { setSelectedIds([]); return; }
      const map = { v:"select", p:"pen", e:"eraser", l:"line", r:"rectangle", c:"circle", t:"text", a:"arrow" };
      if (!ctrl && map[e.key]) setTool(map[e.key]);
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [selectedIds, objects, groups]);

  // ─── Design tokens ─────────────────────────────────────────────────────────
  const bg    = "#0d1117";
  const panel = "#161b22";
  const card  = "#1c2128";
  const bdr   = "#30363d";
  const acc   = "#3b82f6";
  const accDim = "rgba(59,130,246,0.18)";
  const txt   = "#cdd5de";
  const muted = "#7d8590";

  const propLabel = {
    fontSize: 10, fontWeight: 600, textTransform: "uppercase",
    letterSpacing: "0.07em", color: "#4b5563", marginBottom: 5,
  };

  const toolBtn = (active) => ({
    display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
    gap: 2, width: 48, height: 48, borderRadius: 9,
    border: `1.5px solid ${active ? acc : bdr}`,
    background: active ? accDim : "transparent",
    color: active ? "#93c5fd" : "#6b7280",
    cursor: "pointer", transition: "all 0.12s",
    flexShrink: 0,
  });

  const iconBtn = (label, onClick, danger, disabled) => (
    <button key={label} onClick={onClick} disabled={disabled}
      style={{ padding: "4px 10px", border: `1px solid ${bdr}`, borderRadius: 6,
               background: "transparent",
               color: disabled ? "#374151" : danger ? "#f87171" : muted,
               cursor: disabled ? "default" : "pointer", fontSize: 12,
               display: "flex", alignItems: "center", gap: 4,
               transition: "background 0.1s" }}>
      {label}
    </button>
  );

  const swatches = [
    "#1e1e1e","#ffffff","#ef4444","#f97316","#facc15",
    "#22c55e","#3b82f6","#8b5cf6","#ec4899","#78716c",
  ];

  const toolGroups = [
    { title: "Select",   items: ["select"] },
    { title: "Freehand", items: ["pen","eraser"] },
    { title: "Shapes",   items: ["line","rectangle","circle","triangle","diamond","arrow","star","hexagon"] },
    { title: "Insert",   items: ["text"] },
  ];

  const canUndo = hIdx.current > 0;
  const canRedo = hIdx.current < hist.current.length - 1;
  const hasSel  = selectedIds.length > 0;
  const canGroup = selectedIds.length >= 2;
  const inGroup  = !!getGroupForSelection();

  // ── Rotation display (degrees) for selected single object
  const selObj = selectedIds.length === 1 ? objects.find(o => o.id === selectedIds[0]) : null;
  const rotDeg = selObj ? Math.round(((selObj.rotation || 0) * 180 / Math.PI) % 360) : 0;

  return (
    <div style={{ display:"flex", flexDirection:"column", height:"100vh", background:bg,
                  fontFamily:"system-ui, -apple-system, sans-serif", color:txt,
                  userSelect:"none", overflow:"hidden" }}>

      {/* ── TOP BAR ── */}
      <div style={{ height:46, minHeight:46, background:panel, borderBottom:`1px solid ${bdr}`,
                    display:"flex", alignItems:"center", gap:6, padding:"0 14px", flexShrink:0, flexWrap:"wrap" }}>
        <span style={{ fontSize:15, fontWeight:700, color:"#58a6ff", letterSpacing:"-0.04em", marginRight:6 }}>drawpad</span>
        <div style={{ width:1, height:20, background:bdr }} />

        {/* Undo/Redo */}
        <button onClick={undo} disabled={!canUndo} title="Undo (Ctrl+Z)"
          style={{ padding:"4px 10px", border:`1px solid ${bdr}`, borderRadius:6,
                   background:"transparent", color:canUndo?"#9ca3af":"#374151",
                   cursor:canUndo?"pointer":"default", fontSize:13, display:"flex", alignItems:"center", gap:5 }}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} width={13} height={13}>
            <path d="M3 7v6h6"/><path d="M3 13C5.2 6.5 12 4 18 7a9 9 0 010 14"/>
          </svg>
          Undo
        </button>
        <button onClick={redo} disabled={!canRedo} title="Redo (Ctrl+Y)"
          style={{ padding:"4px 10px", border:`1px solid ${bdr}`, borderRadius:6,
                   background:"transparent", color:canRedo?"#9ca3af":"#374151",
                   cursor:canRedo?"pointer":"default", fontSize:13, display:"flex", alignItems:"center", gap:5 }}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} width={13} height={13}>
            <path d="M21 7v6h-6"/><path d="M21 13C18.8 6.5 12 4 6 7a9 9 0 000 14"/>
          </svg>
          Redo
        </button>

        <div style={{ width:1, height:20, background:bdr }} />

        {/* Object ops */}
        {iconBtn("Clear", clearCanvas, true)}
        {iconBtn("Delete", deleteSelected, true, !hasSel)}
        {iconBtn("Duplicate", duplicateSelected, false, !hasSel)}

        <div style={{ width:1, height:20, background:bdr }} />

        {/* Z-order */}
        <span style={{ fontSize:10, color:muted }}>Z-Order:</span>
        {iconBtn("↑↑ Front", bringToFront, false, !hasSel)}
        {iconBtn("↑ Fwd", bringForward, false, !hasSel)}
        {iconBtn("↓ Back", sendBackward, false, !hasSel)}
        {iconBtn("↓↓ Bottom", sendToBack, false, !hasSel)}

        <div style={{ width:1, height:20, background:bdr }} />

        {/* Group */}
        {iconBtn(inGroup ? "Ungroup" : "Group", inGroup ? ungroupSelected : groupSelected, false, inGroup ? false : !canGroup)}

        <div style={{ flex:1 }} />

        {/* Zoom */}
        <span style={{ fontSize:11, color:muted }}>Zoom</span>
        <input type="range" min={40} max={150} step={5} value={Math.round(zoom*100)}
          onChange={e => setZoom(+e.target.value / 100)} style={{ width:90 }} />
        <span style={{ fontSize:11, minWidth:34, textAlign:"right", color:muted }}>{Math.round(zoom*100)}%</span>

        <div style={{ width:1, height:20, background:bdr }} />
        <button onClick={exportPNG}
          style={{ padding:"5px 14px", border:`1px solid ${acc}`, borderRadius:6,
                   background:"rgba(59,130,246,0.12)", color:"#93c5fd", cursor:"pointer",
                   fontSize:12, fontWeight:600 }}>
          Export PNG
        </button>
      </div>

      <div style={{ display:"flex", flex:1, overflow:"hidden", minHeight:0 }}>

        {/* ── LEFT TOOL PANEL ── */}
        <div style={{ width:64, background:panel, borderRight:`1px solid ${bdr}`,
                      display:"flex", flexDirection:"column", padding:"10px 8px",
                      gap:14, overflowY:"auto", flexShrink:0 }}>
          {toolGroups.map(g => (
            <div key={g.title}>
              <div style={{ ...propLabel, textAlign:"center", marginBottom:6 }}>{g.title}</div>
              <div style={{ display:"flex", flexDirection:"column", gap:4, alignItems:"center" }}>
                {g.items.map(id => (
                  <button key={id} onClick={() => setTool(id)}
                    title={`${id} ${id==="select"?"(V)":id==="pen"?"(P)":id==="eraser"?"(E)":id==="line"?"(L)":id==="rectangle"?"(R)":id==="circle"?"(C)":id==="text"?"(T)":id==="arrow"?"(A)":""}`}
                    style={toolBtn(tool === id)}>
                    <ToolIcon id={id} />
                    <span style={{ fontSize:9, lineHeight:1, marginTop:1 }}>{id}</span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* ── CANVAS AREA ── */}
        <div style={{ flex:1, overflow:"auto", display:"flex", alignItems:"flex-start",
                      justifyContent:"center", padding:28, background:"#090d14", minHeight:0 }}>
          <div style={{ width: A4_W * zoom, height: A4_H * zoom, position:"relative", flexShrink:0 }}>
            <div style={{ position:"absolute", top:0, left:0,
                          transform:`scale(${zoom})`, transformOrigin:"top left",
                          width:A4_W, height:A4_H,
                          boxShadow:"0 0 0 1px rgba(255,255,255,0.06), 0 12px 60px rgba(0,0,0,0.8)",
                          borderRadius:1 }}>

              {/* Main canvas (permanent drawing) */}
              <canvas ref={mainRef}
                style={{ display:"block", position:"absolute", top:0, left:0 }} />

              {/* Overlay canvas (live preview) */}
              <canvas ref={overlayRef}
                style={{ display:"block", position:"absolute", top:0, left:0, pointerEvents:"none" }} />

              {/* UI canvas (selection handles) */}
              <canvas ref={uiCanvasRef}
                style={{ display:"block", position:"absolute", top:0, left:0, pointerEvents:"none" }} />

              {/* Invisible event-capture canvas on top */}
              <canvas
                width={A4_W * SCALE} height={A4_H * SCALE}
                style={{
                  display:"block", position:"absolute", top:0, left:0,
                  width:A4_W, height:A4_H, opacity:0,
                  cursor: tool==="select"
                    ? (interactRef.current?.type === "rotate" ? "crosshair"
                       : interactRef.current?.type === "move" ? "move" : "default")
                    : tool==="eraser" ? "cell"
                    : tool==="text"   ? "text"
                    : "crosshair"
                }}
                onMouseDown={onDown} onMouseMove={onMove} onMouseUp={onUp} onMouseLeave={onUp}
                onTouchStart={onDown} onTouchMove={onMove} onTouchEnd={onUp}
              />

              {/* Grid overlay */}
              {grid && (
                <div style={{ position:"absolute", top:0, left:0, width:A4_W, height:A4_H,
                              pointerEvents:"none", zIndex:10,
                              backgroundImage:[
                                "linear-gradient(rgba(99,130,220,0.14) 1px,transparent 1px)",
                                "linear-gradient(90deg,rgba(99,130,220,0.14) 1px,transparent 1px)",
                                "linear-gradient(rgba(99,130,220,0.05) 1px,transparent 1px)",
                                "linear-gradient(90deg,rgba(99,130,220,0.05) 1px,transparent 1px)",
                              ].join(","),
                              backgroundSize:"37.8px 37.8px,37.8px 37.8px,7.56px 7.56px,7.56px 7.56px" }} />
              )}

              {/* Text input */}
              {textPos && (
                <input ref={textRef} value={textVal}
                  onChange={e => setTextVal(e.target.value)}
                  onKeyDown={e => { if(e.key==="Enter") commitText(); if(e.key==="Escape") setTextPos(null); }}
                  onBlur={commitText}
                  style={{ position:"absolute", left:textPos.x, top:textPos.y - fontSize,
                           background:"rgba(59,130,246,0.06)", border:"1.5px dashed #3b82f6",
                           outline:"none", color:strokeColor, fontSize, zIndex:20, minWidth:100,
                           padding:"2px 5px", fontFamily:"system-ui",
                           fontWeight: fontBold ? "bold" : "normal" }} />
              )}
            </div>
          </div>
        </div>

        {/* ── RIGHT PROPERTIES PANEL ── */}
        <div style={{ width:204, background:panel, borderLeft:`1px solid ${bdr}`,
                      padding:"12px 12px", display:"flex", flexDirection:"column",
                      gap:15, overflowY:"auto", flexShrink:0, fontSize:12 }}>

          {/* ── Selection info ── */}
          {hasSel && (
            <div style={{ background:card, borderRadius:8, padding:10, border:`1px solid ${bdr}` }}>
              <div style={{ ...propLabel, color:"#34d399", marginBottom:6 }}>Selection</div>
              <div style={{ color:muted, fontSize:11 }}>{selectedIds.length} object{selectedIds.length>1?"s":""} selected</div>
              {selObj && (
                <>
                  <div style={{ marginTop:6, color:muted, fontSize:11 }}>
                    Rotation: <span style={{ color:txt }}>{rotDeg}°</span>
                  </div>
                  <div style={{ marginTop:4, color:muted, fontSize:11 }}>
                    Z-Index: <span style={{ color:txt }}>{selObj.zIndex ?? 0}</span>
                  </div>
                  {/* Manual rotation slider */}
                  <div style={{ marginTop:8 }}>
                    <div style={{ ...propLabel, color:"#a78bfa" }}>Rotate</div>
                    <input type="range" min={-180} max={180} step={1}
                      value={Math.round((selObj.rotation || 0) * 180 / Math.PI)}
                      onChange={e => {
                        const rad = +e.target.value * Math.PI / 180;
                        setObjects(prev => prev.map(o =>
                          o.id === selObj.id ? { ...o, rotation: rad } : o
                        ));
                      }}
                      style={{ width:"100%" }} />
                    <div style={{ display:"flex", gap:4, marginTop:4 }}>
                      <button onClick={() => setObjects(prev => prev.map(o => selectedIds.includes(o.id) ? { ...o, rotation:0 } : o))}
                        style={{ flex:1, padding:"3px 0", background:"transparent", border:`1px solid ${bdr}`, borderRadius:4, color:muted, cursor:"pointer", fontSize:10 }}>
                        Reset
                      </button>
                      {[90, 180, 270].map(deg => (
                        <button key={deg} onClick={() => {
                          const rad = deg * Math.PI / 180;
                          setObjects(prev => prev.map(o => selectedIds.includes(o.id) ? { ...o, rotation: rad } : o));
                        }}
                          style={{ flex:1, padding:"3px 0", background:"transparent", border:`1px solid ${bdr}`, borderRadius:4, color:muted, cursor:"pointer", fontSize:10 }}>
                          {deg}°
                        </button>
                      ))}
                    </div>
                  </div>
                </>
              )}
              {/* Group indicator */}
              {inGroup && (
                <div style={{ marginTop:8, padding:"4px 8px", background:"rgba(251,191,36,0.1)",
                              borderRadius:4, border:"1px solid rgba(251,191,36,0.3)", fontSize:10, color:"#fbbf24" }}>
                  Grouped ({selectedIds.length} objects)
                </div>
              )}
            </div>
          )}

          {/* ── Layers list ── */}
          <div>
            <div style={propLabel}>Layers ({objects.length})</div>
            <div style={{ display:"flex", flexDirection:"column", gap:2, maxHeight:120, overflowY:"auto" }}>
              {[...objects].sort((a,b)=>(b.zIndex||0)-(a.zIndex||0)).map(o => (
                <div key={o.id} onClick={() => setSelectedIds([o.id])}
                  style={{ display:"flex", alignItems:"center", gap:6, padding:"3px 6px",
                           borderRadius:4, cursor:"pointer",
                           background: selectedIds.includes(o.id) ? accDim : "transparent",
                           border: selectedIds.includes(o.id) ? `1px solid ${acc}` : "1px solid transparent" }}>
                  <span style={{ fontSize:9, color:muted, minWidth:14 }}>{o.zIndex}</span>
                  <span style={{ fontSize:10, color:selectedIds.includes(o.id)?"#93c5fd":muted, flex:1, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                    {o.type}{o.type==="text"?" "+o.text.slice(0,10):""}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* ── Stroke Color ── */}
          <div>
            <div style={propLabel}>Stroke Color</div>
            <div style={{ display:"flex", gap:8, alignItems:"center", marginBottom:8 }}>
              <input type="color" value={strokeColor} onChange={e => setStroke(e.target.value)}
                style={{ width:32, height:28, border:`1px solid ${bdr}`, borderRadius:5,
                         cursor:"pointer", background:"none", padding:0, flexShrink:0 }} />
              <span style={{ fontFamily:"monospace", color:muted, fontSize:11 }}>{strokeColor}</span>
            </div>
            <div style={{ display:"flex", gap:4, flexWrap:"wrap" }}>
              {swatches.map(c => (
                <div key={c} onClick={() => setStroke(c)}
                  style={{ width:20, height:20, borderRadius:4, background:c, cursor:"pointer",
                           border: strokeColor===c ? `2px solid ${acc}` : c==="#ffffff" ? `1px solid ${bdr}` : "1.5px solid transparent",
                           boxSizing:"border-box", flexShrink:0, transition:"border 0.1s" }} />
              ))}
            </div>
          </div>

          {/* ── Fill ── */}
          <div>
            <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:6 }}>
              <div style={propLabel}>Fill</div>
              <label style={{ display:"flex", alignItems:"center", gap:5, cursor:"pointer", fontSize:11, color:muted }}>
                <input type="checkbox" checked={fillOn} onChange={e => setFillOn(e.target.checked)}
                  style={{ cursor:"pointer" }} />
                Enable
              </label>
            </div>
            {fillOn && (
              <>
                <div style={{ display:"flex", gap:8, alignItems:"center", marginBottom:8 }}>
                  <input type="color" value={fillColor} onChange={e => setFill(e.target.value)}
                    style={{ width:32, height:28, border:`1px solid ${bdr}`, borderRadius:5,
                             cursor:"pointer", background:"none", padding:0, flexShrink:0 }} />
                  <span style={{ fontFamily:"monospace", color:muted, fontSize:11 }}>{fillColor}</span>
                </div>
                <div style={{ display:"flex", gap:4, flexWrap:"wrap" }}>
                  {swatches.map(c => (
                    <div key={c} onClick={() => setFill(c)}
                      style={{ width:20, height:20, borderRadius:4, background:c, cursor:"pointer",
                               border: fillColor===c ? `2px solid ${acc}` : c==="#ffffff" ? `1px solid ${bdr}` : "1.5px solid transparent",
                               boxSizing:"border-box", flexShrink:0 }} />
                  ))}
                </div>
              </>
            )}
          </div>

          {/* ── Stroke Width ── */}
          <div>
            <div style={{ display:"flex", justifyContent:"space-between" }}>
              <div style={propLabel}>Width</div>
              <span style={{ fontSize:10, color:muted, marginBottom:5 }}>{lineWidth}px</span>
            </div>
            <input type="range" min={1} max={40} step={1} value={lineWidth}
              onChange={e => setLW(+e.target.value)} style={{ width:"100%", marginBottom:6 }} />
            <div style={{ display:"flex", gap:3 }}>
              {[1, 2, 4, 8, 16].map(w => (
                <button key={w} onClick={() => setLW(w)}
                  style={{ flex:1, padding:"3px 0", background:lineWidth===w?accDim:"transparent",
                           border:`1px solid ${lineWidth===w?acc:bdr}`, borderRadius:4,
                           color:lineWidth===w?"#93c5fd":muted, cursor:"pointer", fontSize:10 }}>
                  {w}
                </button>
              ))}
            </div>
          </div>

          {/* ── Opacity ── */}
          <div>
            <div style={{ display:"flex", justifyContent:"space-between" }}>
              <div style={propLabel}>Opacity</div>
              <span style={{ fontSize:10, color:muted, marginBottom:5 }}>{opacity}%</span>
            </div>
            <input type="range" min={5} max={100} step={5} value={opacity}
              onChange={e => setOpacity(+e.target.value)} style={{ width:"100%" }} />
            <div style={{ marginTop:6, height:6, borderRadius:3,
                          background:`linear-gradient(to right, transparent, ${strokeColor})`,
                          opacity: opacity / 100 }} />
          </div>

          {/* ── Line Style ── */}
          <div>
            <div style={propLabel}>Line Style</div>
            <div style={{ display:"flex", gap:4 }}>
              {[["solid","—"],["dashed","╌╌"],["dotted","···"]].map(([s, icon]) => (
                <button key={s} onClick={() => setLS(s)}
                  style={{ flex:1, padding:"5px 0", background:lineStyle===s?accDim:"transparent",
                           border:`1px solid ${lineStyle===s?acc:bdr}`, borderRadius:5,
                           color:lineStyle===s?"#93c5fd":muted, cursor:"pointer", fontSize:14 }}>
                  {icon}
                </button>
              ))}
            </div>
          </div>

          {/* ── Text Options (only when text tool) ── */}
          {tool === "text" && (
            <div style={{ background:card, borderRadius:8, padding:10, border:`1px solid ${bdr}` }}>
              <div style={{ ...propLabel, color:"#60a5fa", marginBottom:8 }}>Text Options</div>
              <div>
                <div style={{ display:"flex", justifyContent:"space-between" }}>
                  <div style={propLabel}>Font Size</div>
                  <span style={{ fontSize:10, color:muted }}>{fontSize}px</span>
                </div>
                <input type="range" min={8} max={96} step={2} value={fontSize}
                  onChange={e => setFontSize(+e.target.value)} style={{ width:"100%" }} />
              </div>
              <label style={{ display:"flex", alignItems:"center", gap:6, marginTop:8,
                              cursor:"pointer", fontSize:12, color:muted }}>
                <input type="checkbox" checked={fontBold} onChange={e => setFontBold(e.target.checked)} />
                Bold
              </label>
              <div style={{ marginTop:8, fontSize:12, color:muted }}>
                Preview: <span style={{ color:strokeColor, fontSize:14, fontWeight:fontBold?"bold":"normal" }}>Aa</span>
              </div>
            </div>
          )}

          {/* ── Grid ── */}
          <div>
            <div style={propLabel}>Canvas</div>
            <label style={{ display:"flex", gap:6, alignItems:"center", cursor:"pointer", color:muted }}>
              <input type="checkbox" checked={grid} onChange={e => setGrid(e.target.checked)} />
              Grid overlay
            </label>
          </div>

          {/* ── Keyboard shortcuts ── */}
          <div style={{ marginTop:"auto", borderTop:`1px solid ${bdr}`, paddingTop:12 }}>
            <div style={propLabel}>Shortcuts</div>
            <div style={{ display:"flex", flexDirection:"column", gap:4 }}>
              {[
                ["Ctrl+Z", "Undo"],
                ["Ctrl+Y", "Redo"],
                ["Ctrl+G", "Group"],
                ["Ctrl+D", "Duplicate"],
                ["Del", "Delete"],
                ["Esc", "Deselect"],
                ["V", "Select"],
                ["P", "Pen"],
                ["E", "Eraser"],
                ["R", "Rectangle"],
                ["C", "Circle"],
                ["A", "Arrow"],
                ["T", "Text"],
              ].map(([k, v]) => (
                <div key={k} style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                  <code style={{ background:"rgba(59,130,246,0.1)", color:"#60a5fa",
                                 padding:"1px 5px", borderRadius:3, fontSize:10, flexShrink:0 }}>{k}</code>
                  <span style={{ fontSize:11, color:muted }}>{v}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── STATUS BAR ── */}
      <div style={{ height:22, minHeight:22, background:"#090d14", borderTop:`1px solid ${bdr}`,
                    display:"flex", alignItems:"center", padding:"0 14px", gap:20, flexShrink:0 }}>
        <Stat label="Tool" value={tool} />
        <Stat label="X" value={curPos.x} />
        <Stat label="Y" value={curPos.y} />
        <Stat label="Canvas" value={`A4 · ${A4_W}x${A4_H}px`} />
        <Stat label="Objects" value={objects.length} />
        <Stat label="Selected" value={selectedIds.length} />
        {selObj && <Stat label="Rotation" value={`${rotDeg}°`} />}
        <Stat label="History" value={`${hIdx.current + 1} / ${hist.current.length}`} />
      </div>
    </div>
  );
});


function Stat({ label, value }) {
  return (
    <span style={{ fontSize:10, color:"#374151" }}>
      {label}: <span style={{ color:"#6b7280" }}>{value}</span>
    </span>
  );
}

export default DrawingApp;