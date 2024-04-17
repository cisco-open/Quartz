## Deploying the Application

### Cloning the repository

Before running the dashboard, we need to fetch all the required code to our system. To clone the Git repository to the local system,

```
git clone [ Insert Git Clone Command Here]
```

## Launching the Dashboard

The dashboard is currently running on docker, so we need to build the container and deploy it.

```
cd Quartz/quartz-dashboard
docker-compose build
docker-compose up
```

## Accessing the application

Navigate to http://localhost:3000 to access the dashboard.

## Terminating the Dashboard

To stop the dashboard containers, type CTRL+C to stop the running instance. Then, we can stop the containers by using the below command:

```
docker-compose down
```
