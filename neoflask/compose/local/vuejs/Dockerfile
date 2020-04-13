# base image
FROM node:13.12

# set working directory
WORKDIR /app/frontend

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/frontend/node_modules/.bin:$PATH

# install and cache app dependencies
COPY frontend/package.json /app/frontend/package.json
COPY frontend/package-lock.json /app/frontend/package-lock.json
RUN npm install
RUN npm install @vue/cli

COPY ./compose/local/vuejs/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
