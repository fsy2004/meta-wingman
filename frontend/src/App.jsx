import React, { useEffect, useState, useRef } from 'react'
import Form from '@rjsf/core'
import validator from '@rjsf/validator-ajv8'

const TIER = { T1: '#2e7d32', T2: '#f9a825', T3: '#c62828' }
const LIGHT = { green: ['🟢', '#2e7d32'], yellow: ['🟡', '#f9a825'], red: ['🔴', '#c62828'] }

// 开发态(vite 代理)用相对路径;Tauri 打包态由 .env.production 注入绝对后端地址
const API = import.meta.env.VITE_API_BASE || ''

async function j(url, opts) { const r = await fetch(url, opts); return r.json() }

// 稳健 CSV 解析(处理引号内逗号)
function parseCsv(text) {
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

function CsvTable({ url }) {
  const [rows, setRows] = useState(null)
  useEffect(() => { fetch(url).then(r => r.text()).then(t => setRows(parseCsv(t))).catch(() => setRows([])) }, [url])
  if (!rows) return <div className="tbl-loading">加载中…</div>
  if (!rows.length) return <div className="tbl-loading">（空表）</div>
  const [head, ...body] = rows
  const fmt = v => { const n = Number(v); return (v !== '' && !isNaN(n) && /\d/.test(v)) ? (Math.abs(n) >= 1e-4 && Math.abs(n) < 1e6 ? +n.toFixed(4) : v) : v }
  return <div className="tbl-wrap"><table className="tbl">
    <thead><tr>{head.map((h, i) => <th key={i}>{h}</th>)}</tr></thead>
    <tbody>{body.map((r, ri) => <tr key={ri}>{r.map((c, ci) => <td key={ci}>{fmt(c)}</td>)}</tr>)}</tbody>
  </table></div>
}

export default function App() {
  const [machine, setMachine] = useState(null)
  const [env, setEnv] = useState(null)
  const [envBusy, setEnvBusy] = useState(false)
  const [envLog, setEnvLog] = useState([])
  const [methods, setMethods] = useState([])
  const [sel, setSel] = useState(null)          // manifest
  const [profile, setProfile] = useState(null)  // {data_profile, estimate, redlight}
  const [formData, setFormData] = useState({})
  const [logs, setLogs] = useState([])
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)    // done event
  const logRef = useRef(null)
  const selTok = useRef(0)   // 选方法请求令牌:丢弃过期的 dataprofile 返回
  const runTok = useRef(0)   // 运行请求令牌:切换方法/重跑时丢弃旧流

  useEffect(() => {
    j(`${API}/api/machine`).then(setMachine)
    j(`${API}/api/methods`).then(setMethods)
    j(`${API}/api/envcheck`).then(setEnv).catch(() => {})
  }, [])

  async function installEnv() {
    setEnvBusy(true); setEnvLog([])
    const resp = await fetch(`${API}/api/envinstall`, { method: 'POST' })
    const reader = resp.body.getReader(); const dec = new TextDecoder(); let buf = ''
    while (true) {
      const { done, value } = await reader.read(); if (done) break
      buf += dec.decode(value, { stream: true }); let i
      while ((i = buf.indexOf('\n')) >= 0) {
        const line = buf.slice(0, i); buf = buf.slice(i + 1); if (!line.trim()) continue
        let ev; try { ev = JSON.parse(line) } catch { continue }
        if (ev.type === 'log') setEnvLog(l => [...l, ev.line])
      }
    }
    try { setEnv(await j(`${API}/api/envcheck`)) } catch {}
    setEnvBusy(false)
  }
  useEffect(() => { if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight }, [logs])

  async function pick(id) {
    const tok = ++selTok.current
    runTok.current++                      // 使任何在跑的旧流失效,避免旧结果串进新方法
    setResult(null); setLogs([]); setProfile(null); setRunning(false)
    try {
      const m = await j(`${API}/api/methods/${id}`)
      if (tok !== selTok.current) return   // 期间已切换到别的方法 → 丢弃
      setSel(m); setFormData({})
      const p = await j(`${API}/api/dataprofile`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ method_id: id }) })
      if (tok !== selTok.current) return
      setProfile(p)
    } catch (e) {
      if (tok === selTok.current) setProfile(null)
    }
  }

  async function run() {
    if (!sel) return
    const tok = ++runTok.current
    setRunning(true); setLogs([]); setResult(null)
    let reader
    try {
      const resp = await fetch(`${API}/api/run`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ method_id: sel.id, params: formData }) })
      if (!resp.body) throw new Error('服务器无响应体(后端是否在运行?)')
      reader = resp.body.getReader(); const dec = new TextDecoder(); let buf = ''
      while (true) {
        const { done, value } = await reader.read(); if (done) break
        if (tok !== runTok.current) { try { await reader.cancel() } catch {} return }  // 已切换/重跑 → 丢弃旧流
        buf += dec.decode(value, { stream: true }); let i
        while ((i = buf.indexOf('\n')) >= 0) {
          const line = buf.slice(0, i); buf = buf.slice(i + 1); if (!line.trim()) continue
          let ev; try { ev = JSON.parse(line) } catch { continue }
          if (tok !== runTok.current) continue
          if (ev.type === 'log') setLogs(l => [...l, ev.line])
          else if (ev.type === 'killed') setLogs(l => [...l, '⚠️ ' + ev.reason])
          else if (ev.type === 'error') setLogs(l => [...l, '✗ ' + ev.line])
          else if (ev.type === 'done') setResult({ ...ev, outputs: ev.outputs || [] })
        }
      }
    } catch (e) {
      if (tok === runTok.current) setLogs(l => [...l, '✗ 运行出错: ' + (e?.message || e)])
    } finally {
      if (tok === runTok.current) setRunning(false)
    }
  }

  const groups = methods.reduce((a, m) => { (a[m.family] ||= []).push(m); return a }, {})

  return (
    <div className="app">
      <header>
        <div className="brand">🪽 Meta Wingman <span className="sub">你的 Meta 分析副驾 · 准备数据 → 选方法 → 出图出表</span></div>
        {machine && <div className="machine">
          <span>🖥️ {machine.os}</span>
          <span>🧠 {machine.cpu_physical}核/{machine.cpu_logical}线程</span>
          <span>💾 {machine.mem_available_gb} / {machine.mem_total_gb} GB 可用</span>
        </div>}
      </header>
      {env && (
        <div className={'envbar ' + (env.ready ? 'ok' : 'warn')}>
          <span className="envstat">
            {env.ready ? '🟢 环境就绪' : '🟡 环境缺依赖'}
            {'  ·  '}R {env.r?.present ? (env.r.version_num || '✓') : '✗'}{env.r?.present && env.r?.version_ok === false && ' ⚠️建议≥4.0'}
            {'  ·  '}Python {env.python?.present ? (env.python.version || '✓') : '✗'}{env.python?.version_ok === false && ' ⚠️需≥3.9'}
            {'  ·  '}R 包 {Object.values(env.r?.packages || {}).filter(Boolean).length}/{Object.keys(env.r?.packages || {}).length}
            {!env.r?.present && '  ·  需先装 R 4.x'}
          </span>
          {!env.ready && (
            <button className="envinstall" disabled={envBusy} onClick={installEnv}>
              {envBusy ? '安装中…' : '⤓ 一键安装缺失依赖'}
            </button>
          )}
          {envLog.length > 0 && <pre className="envlog">{envLog.slice(-6).join('\n')}</pre>}
        </div>
      )}
      <div className="body">
        <aside>
          {Object.entries(groups).map(([fam, list]) => (
            <div key={fam} className="grp">
              <div className="grp-title">{fam}</div>
              {list.map(m => (
                <div key={m.id} className={'item' + (sel?.id === m.id ? ' active' : '')} onClick={() => pick(m.id)}>
                  <span className="tier" style={{ background: TIER[m.tier] }}>{m.tier}</span>
                  <span>{m.title}</span>
                  <span className="lang">{m.language}</span>
                </div>
              ))}
            </div>
          ))}
        </aside>
        <main>
          {!sel && <div className="empty">← 从左侧选一个方法</div>}
          {sel && <>
            <h2>{sel.title} <small>{sel.title_en}</small></h2>
            <p className="desc">{sel.description}</p>
            {profile?.data_profile?.path && (
              <a className="dl-example" download
                 href={`${API}/api/file?path=` + encodeURIComponent(profile.data_profile.path)}>
                ⤓ 下载示例数据(即所需 CSV 格式模板)
              </a>
            )}

            {profile && <div className="redlight" style={{ borderColor: (LIGHT[profile.redlight?.level] || LIGHT.green)[1] }}>
              <div className="rl-head" style={{ color: (LIGHT[profile.redlight?.level] || LIGHT.green)[1] }}>
                {(LIGHT[profile.redlight?.level] || LIGHT.green)[0]} 内存红绿灯 —— 预估峰值 ≈ {profile.estimate.predicted_peak_gb} GB / 可用 {profile.redlight.available_gb} GB
              </div>
              <div className="rl-body">
                <div>数据规模: {profile.data_profile.n_rows} × {profile.data_profile.n_cols} · {profile.data_profile.size_mb} MB</div>
                <div>内存杀手维度: {profile.estimate.killer_dim} · 模型 {profile.estimate.detail}</div>
                <div className="advice">{profile.redlight.advice}</div>
                <div className="disc">{profile.redlight.disclaimer}{profile.estimate.calibrated ? '' : ' (未校准)'}</div>
              </div>
            </div>}

            <div className="params">
              <h3>参数(schema 自动生成 · 加方法只写一份 JSON)</h3>
              <Form schema={sel.params_schema} validator={validator} formData={formData}
                onChange={e => setFormData(e.formData)} onSubmit={run} disabled={running}>
                <button type="submit" className="run" disabled={running}>{running ? '运行中…' : '▶ 运行(用示例数据)'}</button>
              </Form>
            </div>

            {(logs.length > 0 || running) && <div className="logs">
              <h3>运行日志 {running && <span className="spin">●</span>}</h3>
              <pre ref={logRef}>{logs.join('\n')}</pre>
            </div>}

            {result && (() => {
              const imgs = result.outputs.filter(o => /\.png$/i.test(o))
              const tbls = result.outputs.filter(o => /\.csv$/i.test(o))
              return <div className="result">
                <h3>结果 —— 返回码 {result.returncode} · 峰值内存 {result.peak_gb} GB · {imgs.length} 图 / {tbls.length} 表</h3>
                {imgs.length > 0 && <div className="imgs">
                  {imgs.map(o => (
                    <figure key={o}><img src={`${API}/api/file?path=` + encodeURIComponent(o)} alt="" />
                      <figcaption>{o.split(/[\\/]/).pop()}</figcaption></figure>
                  ))}
                </div>}
                {tbls.map(o => (
                  <div className="tblcard" key={o}>
                    <div className="tblname">📄 {o.split(/[\\/]/).pop()}</div>
                    <CsvTable url={`${API}/api/file?path=` + encodeURIComponent(o)} />
                  </div>
                ))}
              </div>
            })()}
          </>}
        </main>
      </div>
    </div>
  )
}
