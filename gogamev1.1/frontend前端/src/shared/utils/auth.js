import axios from 'axios'
import { getCurrentCSRFToken } from './csrf'

const API_BASE = import.meta.env.VITE_API_BASE || '/backend'

export const api = axios.create({ baseURL: API_BASE })

// 确保发送 Cookie（用于 httpOnly 刷新 Token 流程）并附带 CSRF Token
api.defaults.withCredentials = true

api.interceptors.request.use((cfg) => {
  // 如果存在 access token，则附加 Authorization 请求头
  const token = localStorage.getItem('access')
  if (token) {
    cfg.headers.Authorization = `Bearer ${token}`
    console.log('API请求:', cfg.method?.toUpperCase(), cfg.url)
    console.log('Token有效:', token.length > 10)
  } else {
    console.warn('API请求:', cfg.method?.toUpperCase(), cfg.url, '- 没有Token')
  }

  // 双重提交CSRF：从Cookie读取token并在请求头中发送
  const csrftoken = getCurrentCSRFToken()
  if (csrftoken) {
    cfg.headers['X-CSRFToken'] = csrftoken
  }

  // 确保跨站请求携带 Cookie
  cfg.withCredentials = true
  return cfg
})

api.interceptors.response.use(null, async (error) => {
  const original = error.config
  if (!original) return Promise.reject(error)
  if (error.response?.status === 401 && !original._retry) {
    original._retry = true
    try {
      // 基于 Cookie 的刷新：无需请求体，服务端从 httpOnly Cookie 读取 refresh token
      const res = await axios.post(`${API_BASE}/token/refresh/`, null, { withCredentials: true })
      const { access } = res.data
      if (access) localStorage.setItem('access', access)
      original.headers.Authorization = `Bearer ${access}`
      return api(original)
    } catch (e) {
      localStorage.removeItem('access')
      return Promise.reject(error)
    }
  }
  return Promise.reject(error)
})

export async function login({ username, password }) {
  // 服务端会把 refresh token 写入 httpOnly Cookie；响应体返回 access token
  const res = await api.post('/token/', { username, password })
  if (res.data.access) {
    localStorage.setItem('access', res.data.access)
    // 同时存储用户名信息，供HistoryView使用
    console.log('登录成功，存储用户信息:', username)
    localStorage.setItem('userInfo', JSON.stringify({
      username: username,
      id: username // 由于API返回的是用户名，我们直接使用用户名作为ID
    }))
  }
  return res.data
}

export async function register({ username, email, password }) {
  const res = await api.post('/register/', { username, email, password })
  return res.data
}

export async function requestPasswordReset({ email }) {
  const res = await api.post('/password-reset/', { email })
  return res.data
}

export async function logout() {
  try {
    // 服务端会从 Cookie 读取 refresh 并将其加入黑名单
    await api.post('/logout/', null)
  } catch (e) {
    // 忽略错误
  }
  localStorage.removeItem('access')
  localStorage.removeItem('userInfo') // 清除用户信息
}

// 创建经过验证的落子
export async function createValidatedMove(gameId, row, col, color) {
  try {
    const res = await api.post('/datab/games/validated-move/', {
      game: gameId,
      row: row,
      col: col,
      color: color
    })
    return {
      success: true,
      data: res.data
    }
  } catch (error) {
    console.error('验证落子创建失败:', error)

    // 处理不同类型的错误
    let errorMessage = '落子失败，请重试'
    let errorType = 'unknown'

    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail || error.response.data?.message || '未知错误'

      if (status === 400) {
        errorType = 'validation'
        errorMessage = detail
      } else if (status === 403) {
        errorType = 'permission'
        errorMessage = '您无权在该游戏中落子'
      } else if (status === 429) {
        errorType = 'rate_limit'
        errorMessage = '落子过于频繁，请稍后再试'
        const minInterval = error.response.data?.min_interval
        if (minInterval) {
          errorMessage += `（${minInterval}秒后可再次落子）`
        }
      } else if (status === 401) {
        errorType = 'auth'
        errorMessage = '认证失败，请重新登录'
      }
    } else if (error.request) {
      errorType = 'network'
      errorMessage = '网络连接失败，请检查网络连接'
    }

    return {
      success: false,
      error: {
        type: errorType,
        message: errorMessage,
        details: error.response?.data
      }
    }
  }
}

// 查询玩家角色
export async function getPlayerColor(gameId) {
  try {
    const res = await api.get(`/datab/games/${gameId}/player-color/`)
    return {
      success: true,
      data: res.data.color
    }
  } catch (error) {
    console.error('查询玩家角色失败:', error)

    let errorMessage = '查询玩家角色失败'
    let errorType = 'unknown'

    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail || error.response.data?.message || '未知错误'

      if (status === 403) {
        errorType = 'permission'
        errorMessage = '您无权查看该游戏信息'
      } else if (status === 404) {
        errorType = 'not_found'
        errorMessage = '游戏不存在'
      } else if (status === 401) {
        errorType = 'auth'
        errorMessage = '认证失败，请重新登录'
      } else {
        errorType = 'api_error'
        errorMessage = detail
      }
    } else if (error.request) {
      errorType = 'network'
      errorMessage = '网络连接失败，请检查网络连接'
    }

    return {
      success: false,
      error: {
        type: errorType,
        message: errorMessage,
        details: error.response?.data
      }
    }
  }
}

// 查询最新落子颜色
export async function getLatestMoveColor(gameId) {
  try {
    const res = await api.get(`/datab/games/${gameId}/latest-move/`)
    return {
      success: true,
      data: res.data.color
    }
  } catch (error) {
    console.error('查询最新落子颜色失败:', error)

    let errorMessage = '查询最新落子颜色失败'
    let errorType = 'unknown'

    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail || error.response.data?.message || '未知错误'

      if (status === 403) {
        errorType = 'permission'
        errorMessage = '您无权查看该游戏信息'
      } else if (status === 404) {
        errorType = 'not_found'
        errorMessage = '游戏不存在'
      } else if (status === 401) {
        errorType = 'auth'
        errorMessage = '认证失败，请重新登录'
      } else {
        errorType = 'api_error'
        errorMessage = detail
      }
    } else if (error.request) {
      errorType = 'network'
      errorMessage = '网络连接失败，请检查网络连接'
    }

    return {
      success: false,
      error: {
        type: errorType,
        message: errorMessage,
        details: error.response?.data
      }
    }
  }
}

// 结束对局
export async function endGame(gameId, winner) {
  try {
    const res = await api.put(`/datab/games/${gameId}/end-game/`, {
      winner: winner
    })
    return {
      success: true,
      data: res.data
    }
  } catch (error) {
    console.error('结束对局失败:', error)

    let errorMessage = '结束对局失败'
    let errorType = 'unknown'

    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail || error.response.data?.message || '未知错误'

      if (status === 400) {
        errorType = 'validation'
        errorMessage = detail
      } else if (status === 403) {
        errorType = 'permission'
        errorMessage = '您无权结束该游戏'
      } else if (status === 404) {
        errorType = 'not_found'
        errorMessage = '游戏不存在'
      } else if (status === 401) {
        errorType = 'auth'
        errorMessage = '认证失败，请重新登录'
      } else {
        errorType = 'api_error'
        errorMessage = detail
      }
    } else if (error.request) {
      errorType = 'network'
      errorMessage = '网络连接失败，请检查网络连接'
    }

    return {
      success: false,
      error: {
        type: errorType,
        message: errorMessage,
        details: error.response?.data
      }
    }
  }
}

// 删除邀请
export async function deleteInvitation(invitationId) {
  try {
    console.log(`正在删除邀请: ${invitationId}`)
    const res = await api.delete(`/invitation/delete/${invitationId}/`)

    return {
      success: true,
      data: res.data,
      message: '邀请已自动删除'
    }
  } catch (error) {
    console.error('删除邀请失败:', error)

    let errorMessage = '删除邀请失败'
    let errorType = 'unknown'

    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail || error.response.data?.message || '未知错误'

      if (status === 404) {
        errorType = 'not_found'
        errorMessage = '邀请不存在或已被删除'
      } else if (status === 403) {
        errorType = 'permission'
        errorMessage = '您无权删除此邀请'
      } else if (status === 401) {
        errorType = 'auth'
        errorMessage = '认证失败，请重新登录'
      } else {
        errorType = 'api_error'
        errorMessage = detail
      }
    } else if (error.request) {
      errorType = 'network'
      errorMessage = '网络连接失败，请检查网络连接'
    }

    return {
      success: false,
      error: {
        type: errorType,
        message: errorMessage,
        details: error.response?.data
      }
    }
  }
}

export default api

