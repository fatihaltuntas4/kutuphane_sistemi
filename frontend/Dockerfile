FROM nginx:alpine

# Nginx'in varsayılan html dizinini temizle ve kendi dosyalarımızı at
RUN rm -rf /usr/share/nginx/html/*
COPY . /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
