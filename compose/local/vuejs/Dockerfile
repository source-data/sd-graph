# base image
FROM node:14.19-bullseye

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH

# install and cache app dependencies
COPY ./frontend/package.json      /app/package.json
COPY ./frontend/package-lock.json /app/package-lock.json
RUN npm install
RUN npm install @vue/cli

COPY ./compose/local/vuejs/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start






