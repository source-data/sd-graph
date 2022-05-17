# build stage
# FROM node:lts-alpine as build-stage
FROM node:14.19-bullseye as build-stage
WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm ci --production
COPY ./frontend .
RUN npm run build

# production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY ./compose/production/vuejs/nginx-default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]