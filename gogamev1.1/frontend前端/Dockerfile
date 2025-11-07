# 多阶段构建：前端Vue应用
FROM node:18-alpine AS build-stage

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装所有依赖（构建时需要开发依赖）
RUN npm ci

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段：Nginx静态文件服务
FROM nginx:1.25-alpine AS production-stage

# 安装curl用于健康检查
RUN apk add --no-cache curl

# 复制自定义nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 创建nginx临时目录
RUN mkdir -p /var/cache/nginx/tmp

# 设置权限
RUN chown -R nginx:nginx /var/cache/nginx && \
    chmod -R 755 /var/cache/nginx

# 复制我们的自定义index.html
COPY index.html /usr/share/nginx/html/

# 复制构建好的静态文件到nginx目录（不会覆盖已存在的index.html）
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 暴露80端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]