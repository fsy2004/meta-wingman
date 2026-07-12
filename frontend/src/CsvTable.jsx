import React, { useEffect, useState } from 'react'
import { parseCsv } from './lib'

// 把结果 CSV 渲染成表格:数值列适度保留小数,过大/过小走原文。
export default function CsvTable({ url }) {
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
