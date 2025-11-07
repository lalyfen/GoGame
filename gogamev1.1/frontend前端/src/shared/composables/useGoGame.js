/**
 * 组合式围棋逻辑（无 DOM 操作）
 * 提供响应式状态与纯逻辑方法，适合在 Vue 组件中直接驱动渲染
 */
import { ref, reactive, computed } from 'vue';
import { useGameStore } from '../../stores/gameStore';

export function useGoGame(size = 19, gameId = null) {
  // 游戏存储引用
  const gameStore = useGameStore();

  // 游戏ID状态（支持动态更新）
  const currentGameId = ref(gameId);

  // 设置游戏ID的方法
  function setGameId(id) {
    currentGameId.value = id;
    console.log('设置游戏ID:', id);
  }

  // 基础状态
  const board = reactive(Array.from({ length: size }, () => Array.from({ length: size }, () => null))); // null | 'black' | 'white'
  const currentPlayer = ref('black');
  const captures = reactive({ black: 0, white: 0 });
  const koPoint = ref(null); // {row, col} | null
  const consecutivePasses = ref(0);
  const moveCount = ref(0);
  const territory = reactive(Array.from({ length: size }, () => Array.from({ length: size }, () => null))); // null | 'black' | 'white'
  const gameOver = ref(false);
  const lastMove = ref(null); // {row, col} | null
  const deadStonesSet = ref(new Set()); // key: `${row},${col}`
  const markingMode = ref(false);
  const scoringPhase = ref(false);
  const komi = ref(3.75);
  const currentPosition = ref({ row: 9, col: 9 });
  const positionIndicatorEnabled = ref(true);

  // 邀请ID管理
  const currentInvitationId = ref(null);

  // 消息系统（由 UI 组件展示）
  const messages = ref([]); // { id, type: 'info'|'warning'|'error'|'success'|'game-over', html?:true, text, time }
  const pushMessage = (text, type = 'info', html = false) => {
    messages.value.push({
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type,
      html,
      text,
      time: new Date(),
    });
    // 控制长度，避免无限增长
    if (messages.value.length > 200) messages.value.shift();
  };
  const clearMessages = () => {
    messages.value = [{
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'info',
      text: '消息已清空',
      time: new Date()
    }];
  };

  // 历史（悔棋用）
  const history = ref([]); // 保存快照

  // 初始化
  function resetBoardArrays() {
    for (let i = 0; i < size; i++) {
      for (let j = 0; j < size; j++) {
        board[i][j] = null;
        territory[i][j] = null;
      }
    }
  }

  function init() {
    resetBoardArrays();

    const savedKomi = localStorage.getItem('goGameKomi');
    if (savedKomi !== null) {
      const val = parseFloat(savedKomi);
      if (!Number.isNaN(val)) komi.value = val;
    }
  }
  init();

  // 工具函数
  const posKey = (r, c) => `${r},${c}`;
  const deadStones = computed(() => new Set(deadStonesSet.value)); // 只读副本
  const blackTerritoryCount = computed(() => sumTerritory('black'));
  const whiteTerritoryCount = computed(() => sumTerritory('white'));

  function sumTerritory(color) {
    let s = 0;
    for (let i = 0; i < size; i++) for (let j = 0; j < size; j++) if (territory[i][j] === color) s++;
    return s;
  }

  function positionToString(row, col) {
    const x = col + 1;
    const y = row + 1;
    return `x${x},y${y}`;
  }

  function stringToPosition(str) {
    if (!str) return null;
    str = str.toLowerCase().replace(/[xy]/g, '').replace(/\s+/g, ',');
    const parts = str.split(',');
    if (parts.length !== 2) return null;

    const x = parseInt(parts[0]);
    const y = parseInt(parts[1]);

    if (Number.isNaN(x) || Number.isNaN(y) || x < 1 || x > size || y < 1 || y > size) return null;

    return { row: y - 1, col: x - 1 };
  }

  function movePosition(dRow, dCol) {
    const newRow = Math.max(0, Math.min(size - 1, currentPosition.value.row + dRow));
    const newCol = Math.max(0, Math.min(size - 1, currentPosition.value.col + dCol));
    currentPosition.value = { row: newRow, col: newCol };
  }

  function updateKomi(value) {
    const newKomi = parseFloat(value);
    if (Number.isNaN(newKomi) || newKomi < 0 || newKomi > 15) {
      pushMessage('贴目值必须在0-15之间', 'error');
      return false;
    }
    if (scoringPhase.value || gameOver.value) {
      pushMessage('计分阶段不能修改贴目', 'warning');
      return false;
    }
    komi.value = newKomi;
    localStorage.setItem('goGameKomi', String(komi.value));
    pushMessage(`贴目已设置为 ${komi.value} 目`, 'success');
    return true;
  }

  // 邻接、提子与劫
  function getNeighbors(row, col) {
    const acc = [];
    const dirs = [[-1, 0], [1, 0], [0, -1], [0, 1]];
    for (const [dr, dc] of dirs) {
      const r = row + dr;
      const c = col + dc;
      if (r >= 0 && r < size && c >= 0 && c < size) acc.push([r, c]);
    }
    return acc;
  }

  function getGroup(row, col) {
    const color = board[row][col];
    if (color === null) return [];
    const visited = new Set();
    const stack = [[row, col]];
    const group = [];
    while (stack.length) {
      const [r, c] = stack.pop();
      const key = posKey(r, c);
      if (visited.has(key)) continue;
      visited.add(key);
      if (board[r][c] === color) {
        group.push([r, c]);
        for (const [nr, nc] of getNeighbors(r, c)) {
          if (!visited.has(posKey(nr, nc))) stack.push([nr, nc]);
        }
      }
    }
    return group;
  }

  function getGroupLiberties(group) {
    const libs = new Set();
    for (const [r, c] of group) {
      for (const [nr, nc] of getNeighbors(r, c)) {
        if (board[nr][nc] === null) libs.add(posKey(nr, nc));
      }
    }
    return Array.from(libs).map(k => k.split(',').map(Number));
  }

  function isValidMove(row, col, color) {
    if (board[row][col] !== null) return false;

    // 劫点
    if (koPoint.value && koPoint.value.row === row && koPoint.value.col === col) {
      pushMessage('此处为劫，不能立刻回提！', 'warning');
      return false;
    }

    // 假落子
    board[row][col] = color;

    const enemy = color === 'black' ? 'white' : 'black';
    const neighbors = getNeighbors(row, col);
    let wouldCapture = false;

    for (const [nr, nc] of neighbors) {
      if (board[nr][nc] === enemy) {
        const group = getGroup(nr, nc);
        if (getGroupLiberties(group).length === 0) {
          wouldCapture = true;
          break;
        }
      }
    }

    if (!wouldCapture) {
      const selfGroup = getGroup(row, col);
      const libs = getGroupLiberties(selfGroup);
      if (libs.length === 0) {
        board[row][col] = null;
        pushMessage('禁止着手！此处落子会导致自杀。', 'error');
        return false;
      }
    }

    // 复原
    board[row][col] = null;
    return true;
  }

  function captureStones(placedRow, placedCol, enemyColor) {
    const captured = [];
    const neighbors = getNeighbors(placedRow, placedCol);
    for (const [r, c] of neighbors) {
      if (board[r][c] === enemyColor) {
        const group = getGroup(r, c);
        const libs = getGroupLiberties(group);
        if (libs.length === 0) {
          for (const [gr, gc] of group) {
            board[gr][gc] = null;
            captured.push([gr, gc]);
          }
          const capturingColor = enemyColor === 'black' ? 'white' : 'black';
          captures[capturingColor] += group.length;
        }
      }
    }
    return captured;
  }

  function checkKo(row, col, capturedStones) {
    if (capturedStones.length === 1) {
      const [cr, cc] = capturedStones[0];
      const group = getGroup(row, col);
      if (group.length === 1) {
        const libs = getGroupLiberties(group);
        if (libs.length === 1 && libs[0][0] === cr && libs[0][1] === cc) {
          koPoint.value = { row: cr, col: cc };
          return;
        }
      }
    }
    koPoint.value = null;
  }

  function saveHistory() {
    const boardCopy = board.map(row => [...row]);
    history.value.push({
      board: boardCopy,
      currentPlayer: currentPlayer.value,
      captures: { ...captures },
      koPoint: koPoint.value ? { ...koPoint.value } : null,
      moveCount: moveCount.value,
      lastMove: lastMove.value ? { ...lastMove.value } : null,
      consecutivePasses: consecutivePasses.value,
      deadStones: new Set(deadStonesSet.value),
      scoringPhase: scoringPhase.value,
      gameOver: gameOver.value,
      komi: komi.value
    });
  }

  function undo() {
    if (history.value.length === 0) {
      pushMessage('没有可悔的棋！', 'warning');
      return false;
    }
    const state = history.value.pop();
    for (let i = 0; i < size; i++) {
      for (let j = 0; j < size; j++) {
        board[i][j] = state.board[i][j];
      }
    }
    currentPlayer.value = state.currentPlayer;
    captures.black = state.captures.black;
    captures.white = state.captures.white;
    koPoint.value = state.koPoint;
    moveCount.value = state.moveCount;
    lastMove.value = state.lastMove;
    consecutivePasses.value = state.consecutivePasses;
    deadStonesSet.value = new Set(state.deadStones);
    gameOver.value = false;
    scoringPhase.value = state.scoringPhase || false;
    // 复位属地图与标记模式
    for (let i = 0; i < size; i++) for (let j = 0; j < size; j++) territory[i][j] = null;
    markingMode.value = false;

    pushMessage('悔棋成功！', 'success');
    return true;
  }

  function placeStone(row, col, color) {
    saveHistory();

    board[row][col] = color;
    lastMove.value = { row, col };
    consecutivePasses.value = 0;
    moveCount.value++;

    const enemy = color === 'black' ? 'white' : 'black';
    const captured = captureStones(row, col, enemy);

    checkKo(row, col, captured);

    // 切换行棋方
    currentPlayer.value = enemy;
  }

  function handleMoveAt(row, col) {
    if (scoringPhase.value) {
      if (markingMode.value) {
        toggleDeadStone(row, col);
      } else {
        pushMessage('游戏已进入计分阶段，请标记死子后确认分数', 'warning');
      }
      return false;
    }
    if (gameOver.value) {
      pushMessage('游戏已结束，请开始新局', 'info');
      return false;
    }
    if (board[row][col] !== null) {
      pushMessage('此位置已有棋子', 'warning');
      return false;
    }
    if (!isValidMove(row, col, currentPlayer.value)) {
      return false;
    }

    // 如果有游戏ID，则调用API进行验证落子
    if (currentGameId.value) {
      return createApiValidatedMove(row, col, currentPlayer.value);
    } else {
      // 本地模式：直接落子
      placeStone(row, col, currentPlayer.value);
      return true;
    }
  }

  // API验证落子
  async function createApiValidatedMove(row, col, color) {
    try {
      // 保存当前状态用于回滚
      const boardState = board.map(row => [...row]);
      const capturesState = { ...captures };
      const currentPlayerState = currentPlayer.value;
      const moveCountState = moveCount.value;
      const lastMoveState = lastMove.value ? { ...lastMove.value } : null;

      // 乐观更新：先本地落子
      placeStone(row, col, color);

      // 调用API验证
      const result = await gameStore.createValidatedMove(currentGameId.value, row + 1, col + 1, color);

      if (result.success) {
        pushMessage('落子成功', 'success');

        // 如果有关联的邀请ID，自动删除邀请记录
        if (currentInvitationId.value) {
          console.log(`检测到邀请ID ${currentInvitationId.value}，准备自动删除邀请记录`);
          try {
            // 动态导入以避免循环依赖
            const { deleteInvitation } = await import('../utils/auth');
            const deleteResult = await deleteInvitation(currentInvitationId.value);

            if (deleteResult.success) {
              pushMessage(deleteResult.message || '邀请已自动删除', 'success');
              console.log('邀请记录删除成功');
            } else {
              pushMessage(`删除邀请失败: ${deleteResult.error.message}`, 'warning');
              console.warn('邀请记录删除失败:', deleteResult.error);
            }
          } catch (error) {
            pushMessage('删除邀请时发生错误', 'warning');
            console.error('删除邀请时发生错误:', error);
          } finally {
            // 清除邀请ID，避免重复删除
            currentInvitationId.value = null;
          }
        }

        // 落子成功后，通知外部组件可以触发刷新
        if (currentGameId.value) {
          // 延迟一小段时间确保服务器状态已更新
          setTimeout(() => {
            // 通过自定义事件通知父组件刷新
            window.dispatchEvent(new CustomEvent('moveSuccessful', {
              detail: { gameId: currentGameId.value }
            }));
          }, 500);
        }

        return true;
      } else {
        // API验证失败，回滚状态
        pushMessage(result.error.message || '落子验证失败', 'error');
        rollbackMoveState(boardState, capturesState, currentPlayerState, moveCountState, lastMoveState);
        return false;
      }
    } catch (error) {
      console.error('API落子验证过程中发生错误:', error);
      pushMessage('落子过程中发生错误，请重试', 'error');
      return false;
    }
  }

  // 回滚落子状态
  function rollbackMoveState(boardState, capturesState, currentPlayerState, moveCountState, lastMoveState) {
    // 恢复棋盘状态
    for (let i = 0; i < size; i++) {
      for (let j = 0; j < size; j++) {
        board[i][j] = boardState[i][j];
      }
    }

    // 恢复其他状态
    captures.black = capturesState.black;
    captures.white = capturesState.white;
    currentPlayer.value = currentPlayerState;
    moveCount.value = moveCountState;
    lastMove.value = lastMoveState;

    console.log('状态已回滚到落子前');
  }

  function toggleDeadStone(row, col) {
    if (board[row][col] === null) return;
    const group = getGroup(row, col);
    const firstKey = posKey(row, col);
    const groupDead = deadStonesSet.value.has(firstKey);

    const next = new Set(deadStonesSet.value);
    for (const [gr, gc] of group) {
      const key = posKey(gr, gc);
      if (groupDead) next.delete(key);
      else next.add(key);
    }
    deadStonesSet.value = next;
  }

  function toggleMarkingMode() {
    markingMode.value = !markingMode.value;
    if (!markingMode.value) {
      calculateTerritory();
    }
  }

  function passTurn() {
    if (gameOver.value || scoringPhase.value) {
      pushMessage('游戏已结束或正在计分中', 'warning');
      return;
    }
    saveHistory();
    consecutivePasses.value++;
    lastMove.value = null;
    const playerName = currentPlayer.value === 'black' ? '黑棋' : '白棋';

    if (consecutivePasses.value >= 2) {
      pushMessage(`${playerName}弃手`, 'info');
      enterScoringPhase();
    } else {
      const nextPlayerName = currentPlayer.value === 'black' ? '白棋' : '黑棋';
      currentPlayer.value = currentPlayer.value === 'black' ? 'white' : 'black';
      pushMessage(`${playerName}弃手，轮到${nextPlayerName}`, 'info');
    }
  }

  function enterScoringPhase() {
    scoringPhase.value = true;
    calculateTerritory();
    pushMessage('双方连续弃手，游戏进入终局计分阶段', 'success');
    pushMessage(
      `<p> 当前贴目：${komi.value} 目</p><p> 请标记死子(点击切换死活状态)后 点击"确认分数" 结束游戏</p>`,
      'info',
      true
    );
  }

  function confirmScore() {
    endGame();
  }

  function endGame() {
    gameOver.value = true;
    calculateTerritory();
    const scores = calculateScore();
    scores.blackCaptures = captures.black;
    scores.whiteCaptures = captures.white;

    const scoreDiff = parseFloat(Math.abs(scores.blackTotal - scores.whiteTotal).toFixed(2));
    const winner = scores.blackTotal > scores.whiteTotal ? '黑棋' : '白棋';

    const blackTotalDisplay = scores.blackTotal.toFixed(2);
    const whiteTotalDisplay = scores.whiteTotal.toFixed(2);

    const html = `
      <div class="game-result">
        <h3 class="result-title">🏆 游戏结束</h3>
        <div class="winner-info">${winner}胜 ${scoreDiff} 目</div>

        <div class="score-section">
          <h4>黑棋分数明细</h4>
          <table class="score-table">
            <tr><td>活子数：</td><td>${scores.blackStones}</td></tr>
            <tr><td>领地：</td><td>${scores.blackTerritory}</td></tr>
            <tr><td>提子：</td><td>${scores.blackCaptures}</td></tr>
            <tr><td>死子：</td><td>${scores.blackDeadStones}</td></tr>
            <tr><td>贴目：</td><td>${scores.komi}</td></tr>
            <tr class="total-row"><td>总计：</td><td>${blackTotalDisplay} 目</td></tr>
          </table>
        </div>

        <div class="score-section">
          <h4>白棋分数明细</h4>
          <table class="score-table">
            <tr><td>活子数：</td><td>${scores.whiteStones}</td></tr>
            <tr><td>领地：</td><td>${scores.whiteTerritory}</td></tr>
            <tr><td>提子：</td><td>${scores.whiteCaptures}</td></tr>
            <tr><td>死子：</td><td>${scores.whiteDeadStones}</td></tr>
            <tr class="total-row"><td>总计：</td><td>${whiteTotalDisplay} 目</td></tr>
          </table>
        </div>
      </div>
    `;
    messages.value.push({
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'game-over',
      html: true,
      text: html,
      time: new Date(),
    });
  }

  // 属地计算
  function calculateTerritory() {
    for (let i = 0; i < size; i++) for (let j = 0; j < size; j++) territory[i][j] = null;

    const visited = new Set();

    // 将死子视为空点
    const tempBoard = board.map((row, i) =>
      row.map((cell, j) => (deadStonesSet.value.has(posKey(i, j)) ? null : cell))
    );

    for (let i = 0; i < size; i++) {
      for (let j = 0; j < size; j++) {
        const k = posKey(i, j);
        if (tempBoard[i][j] === null && !visited.has(k)) {
          const terr = getEmptyTerritory(i, j, visited, tempBoard);
          const owner = getTerritoryOwner(terr, tempBoard);
          if (owner !== null) {
            for (const [tr, tc] of terr) territory[tr][tc] = owner;
          }
        }
      }
    }
  }

  function getEmptyTerritory(row, col, visited, tempBoard) {
    const terr = [];
    const stack = [[row, col]];
    while (stack.length) {
      const [r, c] = stack.pop();
      const key = posKey(r, c);
      if (visited.has(key)) continue;
      if (tempBoard[r][c] === null) {
        visited.add(key);
        terr.push([r, c]);
        for (const [nr, nc] of getNeighbors(r, c)) {
          if (!visited.has(posKey(nr, nc))) stack.push([nr, nc]);
        }
      }
    }
    return terr;
  }

  function getTerritoryOwner(terr, tempBoard) {
    const colors = new Set();
    for (const [r, c] of terr) {
      for (const [nr, nc] of getNeighbors(r, c)) {
        if (tempBoard[nr][nc] !== null) colors.add(tempBoard[nr][nc]);
      }
    }
    if (colors.size === 1) return Array.from(colors)[0];
    return null;
  }

  function countStones(color) {
    let count = 0;
    for (let i = 0; i < size; i++) for (let j = 0; j < size; j++) if (board[i][j] === color) count++;
    return count;
  }

  function calculateScore() {
    let blackDeadStones = 0;
    let whiteDeadStones = 0;

    for (const key of deadStonesSet.value) {
      const [r, c] = key.split(',').map(Number);
      if (board[r][c] === 'black') {
        blackDeadStones++;
      } else if (board[r][c] === 'white') {
        whiteDeadStones++;
      }
    }

    const blackStones = countStones('black') - blackDeadStones;
    const whiteStones = countStones('white') - whiteDeadStones;

    const blackT = blackTerritoryCount.value;
    const whiteT = whiteTerritoryCount.value;

    const whiteTotal = whiteStones + whiteT;
    const blackBeforeKomi = blackStones + blackT;
    const blackTotal = parseFloat((blackBeforeKomi - komi.value).toFixed(2));
    
    return {
      blackTotal,
      whiteTotal,
      blackTerritory: blackT,
      whiteTerritory: whiteT,
      blackStones,
      whiteStones,
      blackDeadStones,
      whiteDeadStones,
      komi: komi.value
    };
  }

  // 确认位置输入/按键
  function confirmPosition() {
    if (gameOver.value || scoringPhase.value) {
      pushMessage('游戏已结束或正在计分', 'warning');
      return false;
    }
    const { row, col } = currentPosition.value;
    if (markingMode.value) {
      toggleDeadStone(row, col);
      return true;
    }
    return handleMoveAt(row, col);
  }

  // 初始化游戏（从API数据加载）
  function initializeFromApi(gameData) {
    console.log('从API数据初始化游戏:', gameData);

    // 清空当前棋盘
    resetBoardArrays();

    // 重置游戏状态
    captures.black = 0;
    captures.white = 0;
    koPoint.value = null;
    consecutivePasses.value = 0;
    moveCount.value = 0;
    gameOver.value = false;
    scoringPhase.value = false;
    lastMove.value = null;
    deadStonesSet.value = new Set();
    markingMode.value = false;
    history.value = [];

    // 检查对局是否已经结束
    if (gameData.winner && gameData.winner !== null && gameData.winner !== '') {
      gameOver.value = true;
      pushMessage(`此对局已结束，${gameData.winner === 'black' ? '黑棋' : gameData.winner === 'white' ? '白棋' : '平局'}获胜`, 'info');
    }

    // 设置贴目
    if (gameData.komi) {
      komi.value = parseFloat(gameData.komi);
    }

    // 从intersections加载棋子
    if (gameData.intersections && Array.isArray(gameData.intersections)) {
      gameData.intersections.forEach(intersection => {
        const row = intersection.row - 1; // API使用1-19，转换为0-18
        const col = intersection.col - 1;

        if (row >= 0 && row < size && col >= 0 && col < size) {
          board[row][col] = intersection.color;

          // 更新最后一步棋
          lastMove.value = { row, col };
          moveCount.value++;
        }
      });
    }

    // 根据最后一步棋确定当前玩家
    currentPlayer.value = moveCount.value % 2 === 0 ? 'black' : 'white';

    // 只有对局未结束时才显示加载完成消息
    if (!gameOver.value) {
      pushMessage(`游戏已加载，当前${currentPlayer.value === 'black' ? '黑棋' : '白棋'}行棋`, 'info');
    }
  }

  function updatePositionFromInput(value) {
    const pos = stringToPosition(value);
    if (pos) {
      currentPosition.value = pos;
      return true;
    }
    return false;
  }

  // 新局
  function reset() {
    const k = komi.value;

    // 复位所有状态
    currentPlayer.value = 'black';
    captures.black = 0;
    captures.white = 0;
    koPoint.value = null;
    consecutivePasses.value = 0;
    moveCount.value = 0;
    gameOver.value = false;
    scoringPhase.value = false;
    lastMove.value = null;
    deadStonesSet.value = new Set();
    markingMode.value = false;
    komi.value = k;
    currentPosition.value = { row: 9, col: 9 };
    history.value = [];

    resetBoardArrays();
    pushMessage('游戏已重置，黑棋先行！', 'info');
  }

  // 设置邀请ID
  function setInvitationId(invitationId) {
    currentInvitationId.value = invitationId;
    console.log(`设置邀请ID: ${invitationId}`);
  }

  // 获取邀请ID
  function getInvitationId() {
    return currentInvitationId.value;
  }

  return {
    // 状态
    size,
    board,
    currentPlayer,
    captures,
    koPoint,
    consecutivePasses,
    moveCount,
    territory,
    gameOver,
    lastMove,
    deadStones,
    markingMode,
    scoringPhase,
    komi,
    currentPosition,
    positionIndicatorEnabled,
    messages,
    currentGameId, // 新增状态
    currentInvitationId, // 新增邀请ID状态

    // 只读/派生
    blackTerritoryCount,
    whiteTerritoryCount,

    // 方法
    pushMessage,
    clearMessages,
    positionToString,
    stringToPosition,
    movePosition,
    updateKomi,
    isValidMove,
    handleMoveAt,
    confirmPosition,
    placeStone,
    toggleDeadStone,
    toggleMarkingMode,
    passTurn,
    enterScoringPhase,
    confirmScore,
    endGame,
    calculateTerritory,
    calculateScore,
    reset,
    updatePositionFromInput,
    initializeFromApi, // 新增方法
    createApiValidatedMove, // 新增方法
    setGameId, // 新增方法
    setInvitationId, // 新增方法
    getInvitationId, // 新增方法
  };
}
