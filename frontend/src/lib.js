// 通用工具:常量 / 取 JSON / CSV 解析 / NDJSON 流读取。UI 组件共用,避免各处重复。
export const TIER = { T1: '#2e7d32', T2: '#f9a825', T3: '#c62828' }
export const LIGHT = { green: ['🟢', '#2e7d32'], yellow: ['🟡', '#f9a825'], red: ['🔴', '#c62828'] }

// Tauri 桌面壳内:webview 加载打包 dist,需绝对地址连本地后端;
// 网页托管态(后端同端口服务 dist)与 vite dev 用相对(同源)。
export const API = (typeof window !== 'undefined' && window.__TAURI__)
  ? 'http://127.0.0.1:8000'
  : (import.meta.env.VITE_API_BASE || '')

export async function j(url, opts) { const r = await fetch(url, opts); return r.json() }

// 稳健 CSV 解析(处理引号内逗号)
export function parseCsv(text) {
  const rows = []; let row = [], field = '', inQ = false
  for (let i = 0; i < text.length; i++) {
    const c = text[i]
    if (inQ) { if (c === '"') { if (text[i + 1] === '"') { field += '"'; i++ } else inQ = false } else field += c }
    else if (c === '"') inQ = true
    else if (c === ',') { row.push(field); field = '' }
    else if (c === '\n') { row.push(field); rows.push(row); row = []; field = '' }
    else if (c !== '\r') field += c
  }
  if (field.length || row.length) { row.push(field); rows.push(row) }
  return rows.filter(r => r.length > 1 || (r[0] || '').length)
}

// 统一的 NDJSON 流读取:对每个事件调用 onEvent(ev)。onEvent 返回 false → 取消流(用于令牌失效)。
// 后端 /api/run 与 /api/envinstall 走同一行分隔 JSON 协议。
export async function streamNdjson(url, opts, onEvent) {
  const resp = await fetch(url, opts)
  if (!resp.body) throw new Error('服务器无响应体(后端是否在运行?)')
  const reader = resp.body.getReader(); const dec = new TextDecoder(); let buf = ''
  while (true) {
    const { done, value } = await reader.read(); if (done) break
    buf += dec.decode(value, { stream: true }); let i
    while ((i = buf.indexOf('\n')) >= 0) {
      const line = buf.slice(0, i); buf = buf.slice(i + 1); if (!line.trim()) continue
      let ev; try { ev = JSON.parse(line) } catch { continue }
      if (onEvent(ev) === false) { try { await reader.cancel() } catch {} return }
    }
  }
}
