# # base image
# FROM node:13.12

# # set working directory
# WORKDIR /app/frontend

# # add `/app/node_modules/.bin` to $PATH
# ENV PATH /app/frontend/node_modules/.bin:$PATH

# # install and cache app dependencies
# COPY frontend /app/frontend
# RUN npm install
# RUN npm install @vue/cli
# RUN cd /app/frontend && npm run build

# build stage
FROM node:lts-alpine as build-stage
WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend .
RUN npm run build

# production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]