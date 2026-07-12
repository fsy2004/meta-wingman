import React, { useEffect, useState, useRef } from 'react'
import Form from '@rjsf/core'
import validator from '@rjsf/validator-ajv8'

const TIER = { T1: '#2e7d32', T2: '#f9a825', T3: '#c62828' }
const LIGHT = { green: ['🟢', '#2e7d32'], yellow: ['🟡', '#f9a825'], red: ['🔴', '#c62828'] }

// 开发态(vite 代理)用相对路径;Tauri 打包态由 .env.production 注入绝对后端地址
const API = import.meta.env.VITE_API_BASE || ''

async function j(url, opts) { const r = await fetch(url, opts); return r.json() }

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
    setResult(null); setLogs([]); setProfile(null)
    const m = await j(`${API}/api/methods/${id}`); setSel(m); setFormData({})
    const p = await j(`${API}/api/dataprofile`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ method_id: id }) })
    setProfile(p)
  }

  async function run() {
    setRunning(true); setLogs([]); setResult(null)
    const resp = await fetch(`${API}/api/run`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ method_id: sel.id, params: formData }) })
    const reader = resp.body.getReader(); const dec = new TextDecoder(); let buf = ''
    while (true) {
      const { done, value } = await reader.read(); if (done) break
      buf += dec.decode(value, { stream: true }); let i
      while ((i = buf.indexOf('\n')) >= 0) {
        const line = buf.slice(0, i); buf = buf.slice(i + 1); if (!line.trim()) continue
        let ev; try { ev = JSON.parse(line) } catch { continue }
        if (ev.type === 'log') setLogs(l => [...l, ev.line])
        else if (ev.type === 'killed') setLogs(l => [...l, '⚠️ ' + ev.reason])
        else if (ev.type === 'done') setResult(ev)
      }
    }
    setRunning(false)
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
            {'  ·  '}R {env.r.present ? '✓' : '✗'}
            {'  ·  '}Python {env.python.present ? '✓' : '✗'}
            {'  ·  '}R 包 {Object.values(env.r.packages).filter(Boolean).length}/{Object.keys(env.r.packages).length}
            {!env.r.present && '  ·  需先装 R 4.x'}
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

            {profile && <div className="redlight" style={{ borderColor: LIGHT[profile.redlight.level][1] }}>
              <div className="rl-head" style={{ color: LIGHT[profile.redlight.level][1] }}>
                {LIGHT[profile.redlight.level][0]} 内存红绿灯 —— 预估峰值 ≈ {profile.estimate.predicted_peak_gb} GB / 可用 {profile.redlight.available_gb} GB
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

            {result && <div className="result">
              <h3>结果 —— 返回码 {result.returncode} · 峰值内存 {result.peak_gb} GB · {result.outputs.length} 张图</h3>
              <div className="imgs">
                {result.outputs.map(o => (
                  <figure key={o}><img src={`${API}/api/file?path=` + encodeURIComponent(o)} alt="" />
                    <figcaption>{o.split(/[\\/]/).pop()}</figcaption></figure>
                ))}
              </div>
            </div>}
          </>}
        </main>
      </div>
    </div>
  )
}
