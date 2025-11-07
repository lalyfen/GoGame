# GoGame 后端 API 文档

## 概述

本API提供围棋游戏的后端服务，使用Django REST Framework构建，采用JWT（JSON Web Token）进行认证，并使用HttpOnly Cookie存储刷新令牌以增强安全性。

- **Base URL**: `http://your_server_ip:8000/api/`
- **认证方式**: JWT Access Token + HttpOnly Refresh Cookie
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证机制

### JWT令牌说明

- **Access Token**: 短期有效（默认5分钟），用于访问受保护的API端点
- **Refresh Token**: 长期有效（默认24小时），通过HttpOnly Cookie存储，用于获取新的Access Token
- **认证头格式**: `Authorization: Bearer <access_token>`

### Cookie配置

- **名称**: `refresh`
- **属性**: HttpOnly, Secure（生产环境）, SameSite=Lax, Path=/
- **自动刷新**: 当Access Token过期时，可使用Refresh Token自动获取新的Access Token

## API 端点

### 1. 用户认证

#### 1.1 用户注册

**POST** `/api/register/`

创建新用户账户。

**权限**: 公开访问

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
    "username": "string",
    "email": "string",
    "password": "string"
}
```

**字段说明**:
- `username` (string, 必填): 用户名，唯一标识
- `email` (string, 必填): 邮箱地址，用于账户验证
- `password` (string, 必填): 密码，最少8个字符，建议包含字母、数字和特殊字符

**成功响应** (201 Created):
```json
{
    "id": 1,
    "username": "alice",
    "email": "alice@example.com"
}
```

**错误响应** (400 Bad Request):
```json
{
    "username": ["用户名已存在"],
    "email": ["邮箱格式不正确"],
    "password": ["密码至少需要8个字符"]
}
```

#### 1.2 用户登录（获取令牌）

**POST** `/api/token/`

获取Access Token和Refresh Token。

**权限**: 公开访问

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
    "username": "string",
    "password": "string"
}
```

**成功响应** (200 OK):
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**响应头**:
```
Set-Cookie: refresh=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...; HttpOnly; Path=/; SameSite=Lax
```

**错误响应** (401 Unauthorized):
```json
{
    "detail": "找不到该用户",
    "detail": "密码错误"
}
```

#### 1.3 刷新令牌

**POST** `/api/token/refresh/`

使用Refresh Token获取新的Access Token。

**权限**: 公开访问（需要有效的Refresh Cookie）

**请求头**:
```
Content-Type: application/json
Cookie: refresh=<refresh_token>
```

**成功响应** (200 OK):
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**错误响应** (401 Unauthorized):
```json
{
    "detail": "未提供刷新令牌"
}
```

```json
{
    "detail": "无效的刷新令牌"
}
```

#### 1.4 用户登出

**POST** `/api/logout/`

使Refresh Token失效并清除Cookie。

**权限**: 需要有效的Access Token

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
Cookie: refresh=<refresh_token>
```

**成功响应** (205 Reset Content):
- 无响应体
- 清除refresh Cookie

**错误响应** (400 Bad Request):
```json
{
    "detail": "无效的刷新令牌"
}
```

#### 1.5 受保护端点测试

**GET** `/api/protected/`

测试认证状态的示例端点。

**权限**: 需要有效的Access Token

**请求头**:
```
Authorization: Bearer <access_token>
```

**成功响应** (200 OK):
```json
{
    "message": "你好, alice! 这是一个受保护的端点，只有持有有效JWT访问令牌的用户才能访问。"
}
```

**错误响应** (401 Unauthorized):
```json
{
    "detail": "认证凭据未提供。"
}
```

### 2. 游戏管理

#### 2.1 游戏列表

**GET** `/api/datab/games/`

获取当前用户参与的游戏列表，按创建时间降序排列。

**权限**: 需要有效的Access Token

**安全说明**: 只返回当前用户作为黑棋玩家(player1)或白棋玩家(player2)参与的游戏

**请求头**:
```
Authorization: Bearer <access_token>
```

**成功响应** (200 OK):
```json
[
    {
        "id": 1,
        "player1": 2,
        "player2": 3,
        "winner": "black",
        "score_black": "45.50",
        "score_white": "30.00",
        "komi": "3.75",
        "created_at": "2025-10-04T12:00:00Z",
        "updated_at": "2025-10-04T12:10:00Z",
        "intersections": [
            {
                "id": 1,
                "game": 1,
                "row": 4,
                "col": 16,
                "color": "black",
                "placed_at": "2025-10-04T12:01:02Z"
            }
        ]
    }
]
```

#### 2.2 创建游戏

**POST** `/api/datab/games/`

创建新的围棋游戏。

**权限**: 需要有效的Access Token

**频率限制**:
- 每用户每分钟最多创建1个游戏
- 每用户每小时最多创建5个游戏
- 每用户总游戏数不能超过50个
- 每用户进行中游戏数不能超过10个

**安全说明**: 防止DDoS攻击和资源滥用

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
    "player1": 2,
    "player2": 3,
    "winner": "black",
    "score_black": "0.00",
    "score_white": "0.00",
    "komi": "3.75"
}
```

**字段说明**:
- `player1` (integer, 必填): 黑棋玩家ID
- `player2` (integer, 必填): 白棋玩家ID
- `winner` (string, 必填): 获胜方，可选值: "black", "white", "draw"
- `score_black` (decimal, 必填): 黑棋得分
- `score_white` (decimal, 必填): 白棋得分
- `komi` (decimal, 必填): 贴目

**成功响应** (201 Created):
```json
{
    "id": 2,
    "player1": 2,
    "player2": 3,
    "winner": "black",
    "score_black": "0.00",
    "score_white": "0.00",
    "komi": "3.75",
    "created_at": "2025-10-12T10:00:00Z",
    "updated_at": "2025-10-12T10:00:00Z",
    "intersections": []
}
```

#### 2.3    游戏详情

**GET** `/api/datab/games/{id}/`

获取指定游戏的详细信息。

**权限**: 需要有效的Access Token，且必须是游戏参与者

**安全说明**: 只有作为黑棋玩家(player1)或白棋玩家(player2)参与游戏的用户才能访问

**路径参数**:
- `id` (integer): 游戏ID

**请求头**:
```
Authorization: Bearer <access_token>
```

**成功响应** (200 OK):
```json
{
    "id": 1,
    "player1": 2,
    "player2": 3,
    "winner": "black",
    "score_black": "45.50",
    "score_white": "30.00",
    "komi": "3.75",
    "created_at": "2025-10-04T12:00:00Z",
    "updated_at": "2025-10-04T12:10:00Z",
    "intersections": [...]
}
```

**错误响应** (403 Forbidden):
```json
{
    "detail": "您无权访问该游戏。"
}
```

**错误响应** (404 Not Found):
```json
{
    "detail": "未找到。"
}
```

#### 2.4 更新游戏

**PUT** `/api/datab/games/{id}/` - 完全更新游戏
**PATCH** `/api/datab/games/{id}/` - 部分更新游戏

**权限**: 需要有效的Access Token，且必须是游戏参与者

**安全说明**: 只有作为黑棋玩家(player1)或白棋玩家(player2)参与游戏的用户才能更新

**路径参数**:
- `id` (integer): 游戏ID

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体** (PUT):
```json
{
    "player1": 2,
    "player2": 3,
    "winner": "white",
    "score_black": "45.50",
    "score_white": "48.50",
    "komi": "3.75"
}
```

**请求体** (PATCH):
```json
{
    "winner": "white",
    "score_white": "48.50"
}
```

**成功响应** (200 OK):
返回更新后的游戏对象

#### 2.5 删除游戏

**DELETE** `/api/datab/games/{id}/`

删除指定游戏。

**权限**: 需要有效的Access Token，且必须是游戏参与者

**安全说明**: 只有作为黑棋玩家(player1)或白棋玩家(player2)参与游戏的用户才能删除

**路径参数**:
- `id` (integer): 游戏ID

**请求头**:
```
Authorization: Bearer <access_token>
```

**成功响应** (204 No Content):
- 无响应体

### 3. 棋子管理

#### 3.1 棋子列表

**GET** `/api/datab/intersections/`

获取当前用户参与的游戏中的棋子位置列表，可按游戏ID过滤。

**权限**: 需要有效的Access Token

**安全说明**: 只返回当前用户作为参与者（黑棋或白棋）的游戏中的棋子

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `game` (integer, 可选): 游戏ID，用于过滤特定游戏的棋子（仅限用户参与的游戏）

**示例**: `/api/datab/intersections/?game=1`

**安全说明**: 如果指定了游戏ID，系统会验证用户是否是该游戏的参与者

**成功响应** (200 OK):
```json
[
    {
        "id": 10,
        "game": 1,
        "row": 4,
        "col": 16,
        "color": "black",
        "placed_at": "2025-10-04T12:01:02Z"
    },
    {
        "id": 11,
        "game": 1,
        "row": 16,
        "col": 4,
        "color": "white",
        "placed_at": "2025-10-04T12:02:19Z"
    }
]
```

#### 3.2 创建棋子

**POST** `/api/datab/intersections/`

在指定位置放置棋子。

**权限**: 需要有效的Access Token，且必须是游戏参与者

**安全说明**: 只能在用户参与的游戏中放置棋子

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
    "game": 1,
    "row": 4,
    "col": 16,
    "color": "black"
}
```

**字段说明**:
- `game` (integer, 必填): 游戏ID
- `row` (integer, 必填): 行坐标 (1-19)
- `col` (integer, 必填): 列坐标 (1-19)
- `color` (string, 必填): 棋子颜色，可选值: "black", "white", "empty"

**成功响应** (201 Created):
```json
{
    "id": 12,
    "game": 1,
    "row": 4,
    "col": 16,
    "color": "black",
    "placed_at": "2025-10-12T10:05:00Z"
}
```

**错误响应** (400 Bad Request):
```json
{
    "non_field_errors": ["同一游戏中该位置已有棋子"]
}
```

**错误响应** (403 Forbidden):
```json
{
    "detail": "您无权在该游戏中放置棋子。"
}
```

**错误响应** (429 Too Many Requests):
```json
{
    "detail": "落子过于频繁，请稍后再试",
    "type": "move_limit",
    "min_interval": 1
}
```

#### 3.3 棋子详情

**GET** `/api/datab/intersections/{id}/`

获取指定棋子的详细信息。

**权限**: 需要有效的Access Token，且必须是游戏参与者

**安全说明**: 只能访问用户参与的游戏中的棋子

#### 3.4 更新棋子

**PUT** `/api/datab/intersections/{id}/` - 完全更新
**PATCH** `/api/datab/intersections/{id}/` - 部分更新

**权限**: 需要有效的Access Token，且必须是游戏参与者

**安全说明**: 只能更新用户参与的游戏中的棋子

#### 3.5 删除棋子

**DELETE** `/api/datab/intersections/{id}/`

删除指定棋子。

**权限**: 需要有效的Access Token，且必须是游戏参与者

**安全说明**: 只能删除用户参与的游戏中的棋子

## 数据模型

### Game 模型

```json
{
    "id": "integer",           // 游戏ID
    "player1": "integer",      // 黑棋玩家ID
    "player2": "integer",      // 白棋玩家ID
    "winner": "string",        // 获胜方: "black" | "white" | "draw"
    "score_black": "decimal",  // 黑棋得分 (最大999.99)
    "score_white": "decimal",  // 白棋得分 (最大999.99)
    "komi": "decimal",         // 贴目 (最大99.99)
    "created_at": "datetime",  // 创建时间
    "updated_at": "datetime",  // 更新时间
    "intersections": "array"   // 关联的棋子列表
}
```

### Intersection 模型

```json
{
    "id": "integer",         // 棋子ID
    "game": "integer",       // 游戏ID
    "row": "integer",        // 行坐标 (1-19)
    "col": "integer",        // 列坐标 (1-19)
    "color": "string",       // 棋子颜色: "black" | "white" | "empty"
    "placed_at": "datetime"  // 落子时间 (服务器自动生成)
}
```

## 错误响应格式

### 标准错误响应

```json
{
    "detail": "错误描述信息"
}
```

### 验证错误响应 (400 Bad Request)

```json
{
    "field_name": ["错误信息1", "错误信息2"]
}
```

### 常见错误码

- **400 Bad Request**: 请求参数错误或数据验证失败
- **401 Unauthorized**: 认证失败或令牌无效
- **403 Forbidden**: 权限不足
- **404 Not Found**: 资源不存在
- **405 Method Not Allowed**: HTTP方法不被允许
- **429 Too Many Requests**: 请求过于频繁，触发频率限制
- **500 Internal Server Error**: 服务器内部错误

## 使用示例

### curl 命令示例

#### 1. 用户注册
```bash
curl -X POST http://your_server_ip:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"Str0ng_Pwd!"}'
```

#### 2. 用户登录
```bash
curl -i -X POST http://your_server_ip:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Str0ng_Pwd!"}' \
  -c cookies.txt  # 保存Cookie到文件
```

#### 3. 获取游戏列表
```bash
curl -X GET http://your_server_ip:8000/api/datab/games/ \
  -H "Authorization: Bearer <access_token>"
```

#### 4. 创建新游戏
```bash
curl -X POST http://your_server_ip:8000/api/datab/games/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"player1":2,"player2":3,"winner":"black","score_black":"0.00","score_white":"0.00","komi":"6.50"}'
```

#### 5. 放置棋子
```bash
curl -X POST http://your_server_ip:8000/api/datab/intersections/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"game":1,"row":4,"col":16,"color":"black"}'
```

#### 6. 刷新令牌
```bash
curl -i -X POST http://your_server_ip:8000/api/token/refresh/ \
  -b cookies.txt  # 使用保存的Cookie
```

#### 7. 用户登出
```bash
curl -X POST http://your_server_ip:8000/api/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -b cookies.txt
```

### JavaScript 示例

```javascript
// 登录并获取令牌
async function login(username, password) {
    const response = await fetch('/api/token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    });

    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('accessToken', data.access);
        return data.access;
    }
    throw new Error('登录失败');
}

// 获取游戏列表
async function getGames() {
    const token = localStorage.getItem('accessToken');
    const response = await fetch('/api/datab/games/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    if (response.ok) {
        return await response.json();
    }
    throw new Error('获取游戏列表失败');
}

// 创建新游戏
async function createGame(gameData) {
    const token = localStorage.getItem('accessToken');
    const response = await fetch('/api/datab/games/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(gameData)
    });

    if (response.ok) {
        return await response.json();
    }
    throw new Error('创建游戏失败');
}
```

## 安全考虑

1. **HTTPS**: 生产环境必须使用HTTPS加密传输
2. **CORS**: 配置适当的跨域资源共享策略
3. **令牌过期**: Access Token应在较短时间内过期
4. **Cookie安全**: 生产环境启用Secure和HttpOnly标志
5. **输入验证**: 所有用户输入都应进行严格验证
6. **权限控制**: 确保用户只能访问自己有权限的资源
7. **游戏数据隔离**: 用户只能访问自己参与的游戏（作为黑棋或白棋玩家）
8. **对象级权限**: 实现了细粒度的对象级权限控制，防止越权访问
9. **数据过滤**: 列表接口默认过滤数据，只返回用户有权限查看的记录
10. **频率限制**: 防止DDoS攻击和资源滥用
    - 游戏创建频率：每分钟1个，每小时5个
    - 落子操作频率：每秒1个
    - 用户游戏数量限制：总共50个，进行中10个
11. **数据清理**: 提供定期清理旧游戏数据的工具命令

## 版本信息

- **API版本**: v1
- **Django版本**: 4.x
- **Django REST Framework**: 3.x
- **SimpleJWT**: 5.x

## 更新日志

- **v1.2.0**: 修复DDoS和资源滥用漏洞，实现全面的频率限制机制
  - 添加频率限制装饰器系统，支持多层级限制
  - 游戏创建限制：每分钟1个，每小时5个，用户总数50个，进行中10个
  - 落子操作限制：每秒1个操作
  - 添加数据清理命令，定期清理过期游戏数据
  - 更新API文档，说明频率限制和安全措施
- **v1.1.0**: 修复权限控制漏洞，实现对象级权限控制，确保用户只能访问自己参与的游戏
  - 添加自定义权限类 IsGameParticipant 和 IsIntersectionGameParticipant
  - 修改游戏和棋子相关接口，限制访问权限
  - 更新API文档，说明安全变更
- **v1.0.0**: 初始版本，包含基本的用户认证和游戏管理功能