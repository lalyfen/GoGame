import { defineStore } from 'pinia'
import api, { createValidatedMove, getPlayerColor, getLatestMoveColor, endGame } from '../shared/utils/auth'

export const useGameStore = defineStore('game', {
  state: () => ({
    incompleteGames: [],
    completedGames: [],
    loading: false,
    error: null,
    lastLoaded: null,
    completedGamesLastLoaded: null,
    selectedGameId: null,
    currentGameBoard: null,
    currentGameInfo: null,
    loadingGame: false,
    // 新增：游戏信息缓存和刷新状态
    gameInfoCache: new Map(), // 缓存玩家角色和最新落子颜色
    lastRefreshTimes: new Map(), // 缓存最后刷新时间
    refreshingGames: new Set(), // 正在刷新的游戏ID集合
    // 新增：邀请ID映射管理
    gameInvitationMap: new Map(), // 游戏ID -> 邀请ID 的映射
  }),

  getters: {
    getIncompleteGames: (state) => state.incompleteGames,
    getCompletedGames: (state) => state.completedGames,
    getGameCount: (state) => state.incompleteGames.length,
    getCompletedGameCount: (state) => state.completedGames.length,
    isDataFresh: (state) => {
      if (!state.lastLoaded) return false
      const now = new Date()
      const diffMs = now - state.lastLoaded
      // 30分钟内认为是新鲜数据
      return diffMs < 30 * 60 * 1000
    },
    isCompletedDataFresh: (state) => {
      if (!state.completedGamesLastLoaded) return false
      const now = new Date()
      const diffMs = now - state.completedGamesLastLoaded
      // 30分钟内认为是新鲜数据
      return diffMs < 30 * 60 * 1000
    },
    getSelectedGame: (state) => {
      return state.incompleteGames.find(game => game.id === state.selectedGameId)
    },
    getCurrentGameBoard: (state) => state.currentGameBoard,
    getCurrentGameInfo: (state) => state.currentGameInfo,
    isLoadingGame: (state) => state.loadingGame,
    // 新增getter
    getGameInfoCache: (state) => (gameId) => state.gameInfoCache.get(gameId) || null,
    getLastRefreshTime: (state) => (gameId) => state.lastRefreshTimes.get(gameId) || null,
    isRefreshing: (state) => (gameId) => state.refreshingGames.has(gameId),
    getIsMyTurn: (state) => (gameId) => {
      const gameInfo = state.gameInfoCache.get(gameId)
      if (!gameInfo || !gameInfo.playerColor || !gameInfo.latestMoveColor) {
        return null // 未知状态
      }
      return gameInfo.playerColor !== gameInfo.latestMoveColor
    },
  },

  actions: {
    // 加载未完成对局到内存
    async loadIncompleteGames() {
      // 如果数据在30分钟内加载过，直接使用缓存
      if (this.isDataFresh) {
        console.log('使用缓存的游戏数据')
        return this.incompleteGames
      }

      this.loading = true
      this.error = null

      try {
        console.log('正在加载未完成对局到内存...')
        console.log('API地址:', '/datab/games/incomplete/')

        const response = await api.get('/datab/games/incomplete/')
        this.incompleteGames = response.data
        this.lastLoaded = new Date()

        console.log(`成功加载 ${response.data.length} 个未完成对局到内存`)
        console.log('游戏数据:', response.data)

        return response.data
      } catch (error) {
        this.error = error
        console.error('加载未完成对局失败:', error)
        console.error('错误详情:', error.response?.data)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 加载已完成对局到内存
    async loadCompletedGames() {
      // 如果数据在30分钟内加载过，直接使用缓存
      if (this.isCompletedDataFresh) {
        console.log('使用缓存的已完成对局数据')
        return this.completedGames
      }

      this.loading = true
      this.error = null

      try {
        console.log('正在加载已完成对局到内存...')
        console.log('API地址:', '/datab/games/completed/')

        const response = await api.get('/datab/games/completed/')
        this.completedGames = response.data
        this.completedGamesLastLoaded = new Date()

        console.log(`成功加载 ${response.data.length} 个已完成对局到内存`)
        console.log('已完成对局数据:', response.data)

        return response.data
      } catch (error) {
        this.error = error
        console.error('加载已完成对局失败:', error)
        console.error('错误详情:', error.response?.data)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 选择对局
    selectGame(gameId) {
      this.selectedGameId = gameId
      console.log(`选择对局: ${gameId}`)
    },

    // 加载选中棋局的详细数据
    async loadSelectedGame(gameId) {
      if (!gameId) {
        console.warn('未提供棋局ID')
        return
      }

      this.loadingGame = true
      this.error = null

      try {
        console.log(`正在加载棋局 ${gameId} 的详细数据...`)

        // 获取棋局详情
        const gameResponse = await api.get(`/datab/games/${gameId}/`)
        const gameData = gameResponse.data

        // 获取棋局的所有落子记录 - 使用正确的intersections端点
        const intersectionsResponse = await api.get(`/datab/intersections/?game=${gameId}`)
        console.log('intersections API响应:', intersectionsResponse.data)
        const intersectionsData = intersectionsResponse.data

        // 创建19x19的空棋盘
        const board = Array(19).fill().map(() => Array(19).fill(null))

        // 将落子数据填充到棋盘上
        intersectionsData.forEach(intersection => {
          console.log('处理intersection:', intersection)
          if (intersection.row >= 1 && intersection.row <= 19 && intersection.col >= 1 && intersection.col <= 19) {
            board[intersection.row - 1][intersection.col - 1] = intersection.color
            console.log(`在位置(${intersection.row-1}, ${intersection.col-1})放置${intersection.color}子`)
          }
        })

        // 存储到store中
        this.currentGameBoard = board
        this.currentGameInfo = {
          ...gameData,
          intersections: intersectionsData
        }
        this.selectedGameId = gameId

        console.log(`成功加载棋局 ${gameId}，包含 ${intersectionsData.length} 手棋`)
        return { board, gameInfo: this.currentGameInfo }

      } catch (error) {
        this.error = error
        console.error(`加载棋局 ${gameId} 失败:`, error)
        console.error('错误详情:', error.response?.data)
        throw error
      } finally {
        this.loadingGame = false
      }
    },

    // 添加新对局到缓存
    addGame(game) {
      this.incompleteGames.unshift(game)
      console.log('新对局已添加到缓存:', game)
    },

    // 更新对局状态
    updateGame(gameId, updates) {
      const index = this.incompleteGames.findIndex(g => g.id === gameId)
      if (index !== -1) {
        this.incompleteGames[index] = { ...this.incompleteGames[index], ...updates }
        console.log(`对局 ${gameId} 已更新`)
      }
    },

    // 从缓存中移除对局
    removeGame(gameId) {
      this.incompleteGames = this.incompleteGames.filter(g => g.id !== gameId)
      console.log(`对局 ${gameId} 已从缓存中移除`)
      if (this.selectedGameId === gameId) {
        this.selectedGameId = null
      }
    },

    // 清空缓存
    clearCache() {
      this.incompleteGames = []
      this.completedGames = []
      this.lastLoaded = null
      this.completedGamesLastLoaded = null
      this.error = null
      this.selectedGameId = null
      this.gameInfoCache.clear()
      this.lastRefreshTimes.clear()
      this.refreshingGames.clear()
      this.gameInvitationMap.clear() // 清空邀请映射
      console.log('游戏缓存已清空')
    },

    // 添加邀请ID映射
    addInvitationMapping(gameId, invitationId) {
      this.gameInvitationMap.set(gameId, invitationId)
      console.log(`添加映射: 游戏${gameId} <- 邀请${invitationId}`)
    },

    // 获取游戏的邀请ID
    getInvitationId(gameId) {
      return this.gameInvitationMap.get(gameId)
    },

    // 移除邀请ID映射
    removeInvitationMapping(gameId) {
      const invitationId = this.gameInvitationMap.get(gameId)
      this.gameInvitationMap.delete(gameId)
      console.log(`移除映射: 游戏${gameId} <- 邀请${invitationId || '未知'}`)
      return invitationId
    },

    // 清空所有邀请ID映射
    clearInvitationMappings() {
      const count = this.gameInvitationMap.size
      this.gameInvitationMap.clear()
      console.log(`清空了 ${count} 个邀请ID映射`)
    },

    // 刷新单个游戏信息
    async refreshGameInfo(gameId) {
      try {
        console.log(`刷新游戏 ${gameId} 的玩家角色和最新落子颜色...`)

        // 添加到正在刷新集合
        this.refreshingGames.add(gameId)

        // 并发请求两个接口
        const [playerColorRes, latestMoveRes] = await Promise.all([
          getPlayerColor(gameId),
          getLatestMoveColor(gameId)
        ])

        const gameInfo = {
          playerColor: playerColorRes.success ? playerColorRes.data : null,
          latestMoveColor: latestMoveRes.success ? latestMoveRes.data : null,
          lastRefresh: new Date().toISOString()
        }

        // 处理错误情况
        if (!playerColorRes.success) {
          console.warn(`查询玩家角色失败: ${playerColorRes.error.message}`)
        }
        if (!latestMoveRes.success) {
          console.warn(`查询最新落子颜色失败: ${latestMoveRes.error.message}`)
        }

        // 更新缓存
        this.gameInfoCache.set(gameId, gameInfo)
        this.lastRefreshTimes.set(gameId, new Date())

        console.log(`游戏 ${gameId} 信息刷新完成:`, gameInfo)

        return {
          success: true,
          data: gameInfo,
          errors: {
            playerColor: playerColorRes.success ? null : playerColorRes.error,
            latestMove: latestMoveRes.success ? null : latestMoveRes.error
          }
        }
      } catch (error) {
        console.error(`刷新游戏 ${gameId} 信息时发生错误:`, error)
        return {
          success: false,
          error: {
            type: 'unknown',
            message: '刷新游戏信息时发生未知错误',
            details: error
          }
        }
      } finally {
        // 从正在刷新集合中移除
        this.refreshingGames.delete(gameId)
      }
    },

    // 批量刷新所有游戏信息
    async refreshAllGames() {
      try {
        console.log('开始批量刷新所有游戏信息...')

        const gameIds = this.incompleteGames.map(game => game.id)
        if (gameIds.length === 0) {
          console.log('没有需要刷新的游戏')
          return { success: true, results: [] }
        }

        // 为所有游戏添加刷新状态
        gameIds.forEach(id => this.refreshingGames.add(id))

        // 并发刷新所有游戏
        const refreshPromises = gameIds.map(gameId => this.refreshGameInfo(gameId))
        const results = await Promise.all(refreshPromises)

        console.log(`批量刷新完成，处理了 ${results.length} 个游戏`)

        return {
          success: true,
          results: results,
          total: gameIds.length,
          successful: results.filter(r => r.success).length
        }
      } catch (error) {
        console.error('批量刷新游戏信息时发生错误:', error)
        return {
          success: false,
          error: {
            type: 'batch_error',
            message: '批量刷新时发生错误',
            details: error
          }
        }
      } finally {
        // 清除所有刷新状态
        this.refreshingGames.clear()
      }
    },

    // 检查游戏信息是否需要刷新（5分钟缓存）
    needsRefresh(gameId) {
      const lastRefresh = this.lastRefreshTimes.get(gameId)
      if (!lastRefresh) return true

      const now = new Date()
      const diffMs = now - lastRefresh
      const CACHE_DURATION = 5 * 60 * 1000 // 5分钟

      return diffMs > CACHE_DURATION
    },

    // 创建经过验证的落子
    async createValidatedMove(gameId, row, col, color) {
      try {
        console.log(`正在创建验证落子: 游戏${gameId}, 位置(${row},${col}), 颜色${color}`)

        const result = await createValidatedMove(gameId, row, col, color)

        if (result.success) {
          console.log('验证落子成功:', result.data)

          // 更新当前游戏棋盘状态
          if (this.currentGameBoard && this.selectedGameId === gameId) {
            // 确保坐标在有效范围内
            if (row >= 1 && row <= 19 && col >= 1 && col <= 19) {
              this.currentGameBoard[row - 1][col - 1] = color
              console.log(`更新本地棋盘状态: 位置(${row-1},${col-1})设置为${color}`)
            }
          }

          // 如果有当前游戏信息，也更新 intersections 数据
          if (this.currentGameInfo && this.selectedGameId === gameId) {
            const newIntersection = {
              id: result.data.id,
              game: gameId,
              row: row,
              col: col,
              color: color,
              placed_at: result.data.placed_at
            }

            if (!this.currentGameInfo.intersections) {
              this.currentGameInfo.intersections = []
            }
            this.currentGameInfo.intersections.push(newIntersection)
          }

          return {
            success: true,
            data: result.data
          }
        } else {
          console.error('验证落子失败:', result.error)
          return result
        }
      } catch (error) {
        console.error('创建验证落子时发生错误:', error)
        return {
          success: false,
          error: {
            type: 'unknown',
            message: '创建落子时发生未知错误',
            details: error
          }
        }
      }
    },

    // 计算围棋得分（中国规则）
    calculateGoScore(board, komi = 3.75) {
      if (!board || board.length === 0) {
        return { blackScore: 0, whiteScore: komi, winner: 'white' }
      }

      const BOARD_SIZE = 19
      const visited = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(false))

      // 计算棋子数和领地
      let blackStones = 0
      let whiteStones = 0
      let blackTerritory = 0
      let whiteTerritory = 0

      // 检查一个区域的归属
      function checkTerritory(row, col) {
        if (row < 0 || row >= BOARD_SIZE || col < 0 || col >= BOARD_SIZE || visited[row][col]) {
          return []
        }

        const territory = []
        const stack = [[row, col]]
        let borders = new Set()

        while (stack.length > 0) {
          const [r, c] = stack.pop()

          if (r < 0 || r >= BOARD_SIZE || c < 0 || c >= BOARD_SIZE || visited[r][c]) {
            continue
          }

          visited[r][c] = true

          if (board[r][c] === null) {
            // 空位，属于领地
            territory.push([r, c])

            // 探索四个方向
            stack.push([r + 1, c])
            stack.push([r - 1, c])
            stack.push([r, c + 1])
            stack.push([r, c - 1])
          } else {
            // 遇到棋子，记录边界颜色
            borders.add(board[r][c])
          }
        }

        // 如果边界只有一种颜色的棋子，则领地属于该颜色
        if (borders.size === 1) {
          const owner = borders.values().next().value
          return { territory, owner }
        }

        return { territory: [], owner: null }
      }

      // 遍历整个棋盘
      for (let row = 0; row < BOARD_SIZE; row++) {
        for (let col = 0; col < BOARD_SIZE; col++) {
          if (board[row][col] === 'black') {
            blackStones++
          } else if (board[row][col] === 'white') {
            whiteStones++
          } else if (board[row][col] === null && !visited[row][col]) {
            // 检查空白区域的归属
            const { territory, owner } = checkTerritory(row, col)
            if (owner === 'black') {
              blackTerritory += territory.length
            } else if (owner === 'white') {
              whiteTerritory += territory.length
            }
          }
        }
      }

      // 计算总分（中国规则：棋子数 + 领地数）
      const blackTotal = blackStones + blackTerritory
      const whiteTotal = whiteStones + whiteTerritory + komi

      // 判断胜者
      let winner
      if (blackTotal > whiteTotal) {
        winner = 'black'
      } else if (whiteTotal > blackTotal) {
        winner = 'white'
      } else {
        winner = 'draw'
      }

      return {
        blackScore: blackTotal.toFixed(1),
        whiteScore: whiteTotal.toFixed(1),
        winner,
        details: {
          blackStones,
          whiteStones,
          blackTerritory,
          whiteTerritory,
          komi
        }
      }
    },

    // 强制刷新未完成游戏列表（忽略缓存）
    async forceRefreshIncompleteGames() {
      console.log('强制刷新未完成游戏列表...')
      this.loading = true
      this.error = null

      try {
        const response = await api.get('/datab/games/incomplete/')
        this.incompleteGames = response.data
        this.lastLoaded = new Date()

        console.log(`强制刷新完成，加载了 ${response.data.length} 个未完成对局`)
        return response.data
      } catch (error) {
        this.error = error
        console.error('强制刷新未完成对局失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 强制刷新已完成游戏列表（忽略缓存）
    async forceRefreshCompletedGames() {
      console.log('强制刷新已完成游戏列表...')
      this.loading = true
      this.error = null

      try {
        const response = await api.get('/datab/games/completed/')
        this.completedGames = response.data
        this.completedGamesLastLoaded = new Date()

        console.log(`强制刷新完成，加载了 ${response.data.length} 个已完成对局`)
        return response.data
      } catch (error) {
        this.error = error
        console.error('强制刷新已完成对局失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 结束对局
    async endGame(gameId) {
      try {
        console.log(`正在结束对局: ${gameId}`)

        // 获取当前游戏状态
        let board = this.currentGameBoard
        if (!board || this.selectedGameId !== gameId) {
          // 如果当前没有加载棋盘，先加载
          await this.loadSelectedGame(gameId)
          board = this.currentGameBoard
        }

        if (!board) {
          throw new Error('无法获取游戏棋盘状态')
        }

        // 计算得分
        const gameInfo = this.currentGameInfo
        const komi = parseFloat(gameInfo?.komi || 3.75)
        const scoreResult = this.calculateGoScore(board, komi)

        console.log('计算得分结果:', scoreResult)

        // 调用API结束对局
        const result = await endGame(gameId, scoreResult.winner)

        if (result.success) {
          console.log('对局结束成功:', result.data)

          // 更新本地状态
          this.updateGame(gameId, {
            winner: scoreResult.winner,
            score_black: scoreResult.blackScore,
            score_white: scoreResult.whiteScore
          })

          // 更新当前游戏信息
          if (this.currentGameInfo && this.selectedGameId === gameId) {
            this.currentGameInfo.winner = scoreResult.winner
            this.currentGameInfo.score_black = scoreResult.blackScore
            this.currentGameInfo.score_white = scoreResult.whiteScore
          }

          // 重新加载游戏列表以同步数据库状态
          console.log('正在重新加载游戏列表以同步数据库状态...')
          try {
            // 强制刷新未完成和已完成游戏列表
            await Promise.all([
              this.forceRefreshIncompleteGames(),
              this.forceRefreshCompletedGames()
            ])
            console.log('游戏列表重新加载完成')
          } catch (refreshError) {
            console.error('重新加载游戏列表失败:', refreshError)
            // 不影响主流程，只记录错误
          }

          return {
            success: true,
            data: {
              gameId,
              winner: scoreResult.winner,
              blackScore: scoreResult.blackScore,
              whiteScore: scoreResult.whiteScore,
              details: scoreResult.details
            }
          }
        } else {
          console.error('结束对局API调用失败:', result.error)
          return result
        }
      } catch (error) {
        console.error('结束对局时发生错误:', error)
        return {
          success: false,
          error: {
            type: 'unknown',
            message: '结束对局时发生未知错误',
            details: error
          }
        }
      }
    }
  }
})