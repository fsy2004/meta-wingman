import React from 'react'

// 顶层错误边界:任何渲染异常都被兜住,显示可读错误 + 刷新按钮,而不是整页白屏。
export default class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { error: null } }
  static getDerivedStateFromError(error) { return { error } }
  componentDidCatch(error, info) { console.error('UI 渲染错误:', error, info) }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 32, fontFamily: 'system-ui, sans-serif', color: '#c62828' }}>
          <h2>😵 界面出错了</h2>
          <p style={{ color: '#555' }}>渲染时发生异常,已阻止整页白屏。可刷新重试;若反复出现,请把下面的信息反馈给开发者。</p>
          <pre style={{ background: '#faf0f0', padding: 12, borderRadius: 6, whiteSpace: 'pre-wrap', fontSize: 12.5 }}>
            {String(this.state.error?.stack || this.state.error)}
          </pre>
          <button onClick={() => location.reload()} style={{ padding: '8px 16px', fontSize: 14, cursor: 'pointer' }}>刷新页面</button>
        </div>
      )
    }
    return this.props.children
  }
}
