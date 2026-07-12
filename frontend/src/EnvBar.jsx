import React, { useEffect, useState } from 'react'
import { API, j, streamNdjson } from './lib'

// 环境操作中心:显示 R/Python/包状态,选镜像源,一键装缺失依赖,并对「版本过低/缺 R」给出升级指引。
// 原则:绝不自动改动系统 R/Python(只提示命令与镜像链接,由用户自行升级)。默认清华源。
export default function EnvBar({ env, onRefresh }) {
  const [sources, setSources] = useState(null)
  const [srcId, setSrcId] = useState('')
  const [busy, setBusy] = useState(false)
  const [log, setLog] = useState([])
  const [outcome, setOutcome] = useState(null)   // 'ok' | 'warn' | null

  useEffect(() => {
    j(`${API}/api/sources`).then(s => {
      setSources(s)
      setSrcId(s.pip_cran_default || (s.pip_cran?.[0]?.id) || '')
    }).catch(() => {})
  }, [])

  if (!env) return null
  const req = sources?.requirements || { python_min: '3.9', r_min: '4.0' }
  const chosen = sources?.pip_cran?.find(e => e.id === srcId) || {}
  const cranBase = (chosen.cran_repo || 'https://mirrors.tuna.tsinghua.edu.cn/CRAN') + '/bin/windows/base/'

  // 版本过低/缺失 → 需用户手动处理的项(不自动执行)
  const notices = []
  if (env.python?.present && env.python?.version_ok === false)
    notices.push({ what: `Python ${env.python.version} 偏低(需 ≥ ${req.python_min})`,
                   cmd: 'winget install Python.Python.3.12', link: 'https://www.python.org/downloads/', linkLabel: 'python.org 官网下载' })
  if (!env.r?.present)
    notices.push({ what: '未检测到 R,方法无法运行', cmd: 'winget install RProject.R', link: cranBase, linkLabel: '镜像下载 R for Windows' })
  else if (env.r?.version_ok === false)
    notices.push({ what: `R ${env.r.version_num || ''} 偏低(建议 ≥ ${req.r_min})`,
                   cmd: 'winget install RProject.R', link: cranBase, linkLabel: '镜像下载最新 R' })

  async function install() {
    setBusy(true); setLog([]); setOutcome(null)
    try {
      await streamNdjson(`${API}/api/envinstall`,
        { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ source: srcId }) },
        ev => { if (ev.type === 'log') setLog(l => [...l, ev.line]) })
      let fresh = null
      try { fresh = await j(`${API}/api/envcheck`) } catch {}
      setOutcome(fresh?.ready ? 'ok' : 'warn')
      if (fresh && onRefresh) onRefresh(fresh)
    } catch (e) {
      setLog(l => [...l, '✗ 安装出错: ' + (e?.message || e)]); setOutcome('warn')
    } finally {
      setBusy(false)                              // ★无论成败都复位,按钮不会卡在「安装中…」
    }
  }

  const rPkgTotal = Object.keys(env.r?.packages || {}).length
  const rPkgOk = Object.values(env.r?.packages || {}).filter(Boolean).length

  return (
    <div className={'envbar ' + (env.ready ? 'ok' : 'warn')}>
      <span className="envstat">
        {env.ready ? '🟢 环境就绪' : '🟡 环境缺依赖'}
        {'  ·  '}R {env.r?.present ? (env.r.version_num || '✓') : '✗'}{env.r?.present && env.r?.version_ok === false && ' ⚠️'}
        {'  ·  '}Python {env.python?.present ? (env.python.version || '✓') : '✗'}{env.python?.version_ok === false && ' ⚠️'}
        {'  ·  '}R 包 {rPkgOk}/{rPkgTotal}
      </span>

      {!env.ready && (
        <span className="envctl">
          <label className="srcpick" title="pip 与 CRAN 镜像源,默认清华">
            源
            <select value={srcId} disabled={busy} onChange={e => setSrcId(e.target.value)}>
              {(sources?.pip_cran || []).map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
            </select>
          </label>
          <button className="envinstall" disabled={busy} onClick={install}>
            {busy ? '安装中…' : '⤓ 一键安装缺失依赖'}
          </button>
        </span>
      )}

      {notices.length > 0 && (
        <div className="upgrade">
          {notices.map((n, i) => (
            <div className="upgrade-item" key={i}>
              <span>⚠️ {n.what} —— 需你手动升级(本软件不会改动系统 R/Python):</span>
              <code>{n.cmd}</code>
              <span className="or">或</span>
              <a href={n.link} target="_blank" rel="noreferrer">{n.linkLabel} ↗</a>
            </div>
          ))}
        </div>
      )}

      {outcome === 'ok' && <span className="toast ok">✅ 依赖已就绪</span>}
      {outcome === 'warn' && <span className="toast warn">🟡 仍有缺失,请看下方日志</span>}
      {log.length > 0 && <pre className="envlog">{log.slice(-8).join('\n')}</pre>}
    </div>
  )
}
