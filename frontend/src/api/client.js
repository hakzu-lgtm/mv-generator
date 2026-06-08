import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 모든 요청에 저장된 Project ID를 헤더로 자동 포함 (서버 재시작 후 자동 복구)
api.interceptors.request.use((config) => {
  try {
    const stored = localStorage.getItem('mv-generator-project')
    if (stored) {
      const { state } = JSON.parse(stored)
      const keys = state?.apiKeys
      if (keys?.projectId) config.headers['X-Project-Id'] = keys.projectId
    }
  } catch { /* ignore */ }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || err.message || '오류가 발생했습니다'
    return Promise.reject(new Error(msg))
  }
)

export default api

// SSE fetch 요청에도 키 헤더를 포함시키는 헬퍼
function getAuthHeaders() {
  const extra = {}
  try {
    const stored = localStorage.getItem('mv-generator-project')
    if (stored) {
      const { state } = JSON.parse(stored)
      const keys = state?.apiKeys
      if (keys?.projectId) extra['X-Project-Id'] = keys.projectId
    }
  } catch { /* ignore */ }
  return extra
}

export async function postSSE(url, body, onMessage, onError, onComplete) {
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(err.detail || response.statusText)
    }

    const reader  = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer    = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'complete') { onComplete?.(data); return }
            else if (data.type === 'error') { onError?.(new Error(data.message), data); return }
            else { onMessage?.(data) }
          } catch { /* ignore */ }
        }
      }
    }
  } catch (e) {
    onError?.(e)
  }
}
