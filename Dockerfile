FROM nginx:alpine

LABEL maintainer="너의이름"
LABEL description="Dev Workstation 커스텀 Nginx"

ENV APP_ENV=development

# 커스텀 정적 콘텐츠 복사
COPY app/ /usr/share/nginx/html/

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1
