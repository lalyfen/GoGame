# 🎯 GoGame - 围棋在线对弈平台

一个基于Django + Vue.js的全栈围棋游戏平台，支持用户认证、邀请系统和多容器Docker部署。

## ✨ 主要特性

- 🎮 **完整围棋游戏** - 标准围棋规则实现
- 👥 **用户系统** - JWT身份认证和用户管理
- 📧 **邀请系统** - 好友邀请对战功能
- 🏠 **多页面应用** - 登录、注册、游戏大厅、对弈界面
- 🐳 **容器化部署** - Docker Compose一键部署
- 🔄 **API设计** - RESTful API接口
- 💾 **数据持久化** - PostgreSQL + Redis缓存
- 🚀 **高性能** - Nginx反向代理 + Gunicorn

## 🛠️ 技术栈

### 后端
- **框架**: Django 5.2.5 + Django REST Framework
- **数据库**: PostgreSQL 15 (生产) + SQLite (开发)
- **缓存**: Redis 7 + django-redis
- **认证**: Django Simple JWT
- **服务器**: Gunicorn (生产) + Django runserver (开发)
- **容器化**: Docker + Docker Compose

### 前端
- **框架**: Vue 3 + Vue Router 4 + Pinia
- **构建工具**: Vite 5.0.0
- **HTTP客户端**: Axios 1.4.0
- **状态管理**: Pinia 3.0.3
- **部署**: Nginx (静态文件服务 + API反向代理)

## 🚀 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 最少2GB RAM
- 最少10GB磁盘空间

### 一键部署
```bash
# 克隆项目
git clone <repository-url>
cd gogamev1.1

# 配置环境变量
cp .env.example .env
cp backend后端/.env.example backend后端/.env
cp frontend前端/.env.example frontend前端/.env.production

# 编辑配置文件，设置数据库密码等敏感信息
nano .env
nano backend后端/.env
nano frontend前端/.env.production

# 启动所有服务
./deploy.sh start
```

### 手动部署
```bash
# 启动所有容器
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 📖 详细部署文档

请参考 [DEPLOYMENT.md](./DEPLOYMENT.md) 获取详细的部署指南和故障排除。

## 🏗️ 项目结构

```
gogamev1.1/
├── 📁 backend后端/                    # Django后端
│   ├── 📁 core/                       # 核心配置
│   │   ├── settings.py               # Django设置
│   │   ├── cache_manager.py         # 缓存管理
│   │   └── wsgi.py                   # WSGI配置
│   ├── 📁 api/                       # API应用
│   │   ├── views.py                  # API视图
│   │   ├── models.py                 # 数据模型
│   │   ├── serializers.py           # 序列化器
│   │   └── urls.py                   # URL配置
│   ├── 📁 datab/                     # 数据处理应用
│   ├── 📁 invitation/                # 邀请系统应用
│   ├── 📁 migrations/                # 数据库迁移
│   ├── Dockerfile                    # 后端Docker镜像
│   ├── requirements.txt              # Python依赖
│   └── gunicorn.conf.py              # Gunicorn配置
│
├── 📁 frontend前端/                   # Vue.js前端
│   ├── 📁 src/                       # 源代码
│   │   ├── 📁 auth/                  # 认证模块
│   │   ├── 📁 boardgame/             # 围棋游戏模块
│   │   ├── 📁 shared/                # 共享工具
│   │   └── 📁 stores/                # Pinia状态管理
│   ├── Dockerfile                    # 前端Docker镜像
│   ├── nginx.conf                    # 前端Nginx配置
│   ├── package.json                  # 前端依赖
│   └── vite.config.js               # Vite配置
│
├── 📁 nginx/                         # Nginx配置
│   └── default.conf                  # 站点配置
│
├── docker-compose.yml               # Docker编排
├── deploy.sh                         # Linux/macOS部署脚本
├── deploy.bat                        # Windows部署脚本
└── DEPLOYMENT.md                    # 部署文档
```

## 🔧 开发环境设置

### 后端开发
```bash
cd backend后端

# 安装Python依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

### 前端开发
```bash
cd frontend前端

# 安装Node.js依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 🔐 安全配置

项目使用环境变量管理敏感信息，请确保：

1. **设置强密码**: 在`.env`文件中设置数据库密码
2. **生成SECRET_KEY**: 使用Django的`get_random_secret_key()`生成
3. **JWT密钥**: 为JWT认证设置安全密钥
4. **生产环境**: 确保DEBUG=False

## 🌐 API文档

主要API端点：

- `POST /backend/api/auth/login/` - 用户登录
- `POST /backend/api/auth/register/` - 用户注册
- `GET /backend/api/user/profile/` - 用户信息
- `GET /backend/api/invitations/` - 邀请列表
- `POST /backend/api/game/create/` - 创建游戏

## 🎮 使用指南

1. **注册/登录**: 访问首页，创建账户或登录
2. **游戏大厅**: 查看可用游戏或创建新游戏
3. **邀请好友**: 使用邀请系统邀请其他用户
4. **开始对弈**: 进入游戏界面开始围棋对弈

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 许可证

本项目采用 GPL-3.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如有问题或建议，请：

- 创建 [Issue](../../issues)
- 发送邮件至项目维护者
- 查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 获取部署帮助

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！
