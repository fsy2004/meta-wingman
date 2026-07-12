import React, { useEffect, useState, useRef } from 'react'
import Form from '@rjsf/core'
import validator from '@rjsf/validator-ajv8'
import { API, j, streamNdjson, TIER, LIGHT } from './lib'
import CsvTable from './CsvTable'
import EnvBar from './EnvBar'

export default function App() {
  const [machine, setMachine] = useState(null)
  const [env, setEnv] = useState(null)
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
    let cancelled = false
    async function load(attempt = 0) {
      try {
        const ms = await j(`${API}/api/methods`)   // 门槛请求:后端未起会 throw → 重试(Tauri 启动中)
        if (cancelled) return
        setMethods(ms)
        j(`${API}/api/machine`).then(m => !cancelled && setMachine(m)).catch(() => {})
        j(`${API}/api/envcheck`).then(e => !cancelled && setEnv(e)).catch(() => {})
      } catch (e) {
        if (!cancelled && attempt < 40) setTimeout(() => load(attempt + 1), 800)
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

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
    try {
      await streamNdjson(`${API}/api/run`,
        { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ method_id: sel.id, params: formData }) },
        ev => {
          if (tok !== runTok.current) return false   // 已切换/重跑 → 取消旧流
          if (ev.type === 'log') setLogs(l => [...l, ev.line])
          else if (ev.type === 'killed') setLogs(l => [...l, '⚠️ ' + ev.reason])
          else if (ev.type === 'error') setLogs(l => [...l, '✗ ' + ev.line])
          else if (ev.type === 'done') setResult({ ...ev, outputs: ev.outputs || [] })
        })
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

      <EnvBar env={env} onRefresh={setEnv} />

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

            {profile?.data_profile && profile?.estimate && profile?.redlight && (
              <div className="redlight" style={{ borderColor: (LIGHT[profile.redlight.level] || LIGHT.green)[1] }}>
                <div className="rl-head" style={{ color: (LIGHT[profile.redlight.level] || LIGHT.green)[1] }}>
                  {(LIGHT[profile.redlight.level] || LIGHT.green)[0]} 内存红绿灯 —— 预估峰值 ≈ {profile.estimate.predicted_peak_gb} GB / 可用 {profile.redlight.available_gb} GB
                </div>
                <div className="rl-body">
                  <div>数据规模: {profile.data_profile.n_rows} × {profile.data_profile.n_cols} · {profile.data_profile.size_mb} MB</div>
                  <div>内存杀手维度: {profile.estimate.killer_dim} · 模型 {profile.estimate.detail}</div>
                  <div className="advice">{profile.redlight.advice}</div>
                  <div className="disc">{profile.redlight.disclaimer}{profile.estimate.calibrated ? '' : ' (未校准)'}</div>
                </div>
              </div>
            )}

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
