# pull official base image
FROM node:18.12.1-alpine

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH

# install app dependencies
COPY package.json ./
COPY package-lock.json ./
RUN npm install --silent -f
RUN npm install react-scripts@5.0.1 -g --silent

# add app
COPY . ./

# start app
#CMD ["npm", "start"]
#RUN npm run build

#FROM nginx:stable-alpine
#COPY --from=build /app/build /usr/share/nginx/html
# new
#COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
#EXPOSE 80
#CMD ["nginx", "-g", "daemon off;"]