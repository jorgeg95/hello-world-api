# Simple hello-world WEB API to store username and birthdays

This repository contains a simple hello-world WEB API (``revolut_code_challenge_server.py``) that saves user's birthdays to a postgres database. It also returns the number of days until the next birthday, or wishes a Happy Birthday if the user birthday is the same day of the request. 

The WEB API exposes a ``/hello/<username>`` endpoint that accepts two request methods ``GET`` and ``PUT``. For the ``PUT`` it requires a request with a payload: ``{"dateOfBirth": "YYYY-MM-DD"}`` and it will insert/update the ``dateOfBirth`` value to the correspondant ``username`` row in the database.
When you send a ``GET`` request like: ``Get /hello/<username>`` it responds with the following two possible messages:

``{ "message": "Hello, <username>! Your birthday is in N day(s)"}`` if the the user's birthday is in ``N`` days.

Or ``{ "message": "Hello, <username>! Happy birthday!" }`` if the user's birthday is today.

The WEB API is written in python using the flask framework and the psycopg2 library to connect to the postgres database.

## Environment variables

Since some variables are secrets, like database password, the approach used was to use environment variables.
A simple ``.env.example`` was provided to allow to run the application out-of-the-box.
Simply run the command: ``export $(grep -v '^#' .env.example | xargs)`` to export all environment variables from the file except the ones that start with ``#``.

## Running WEB API and Database on Docker container

* Download all repository files to a specific folder and "cd" into it.
* To build the Docker image, run the command: ``make build``
* To run the API and Database as Docker containers with ``docker compose`` run the command: ``make compose-up`` 
* After the above steps you can access the WEB API in the port 8080 of the host running Docker.

## Deploy on Kubernetes

You can use Kubernetes to more easily deploy, manage, automate and scale the WEB API and Database if needed. 

I used Helm to manage the deployment to Kubernetes since it helps to define, install, and upgrade Kubernetes based applications providing interesting features such as rolling upgrades of the application without downtime, speccially useful for production environments.

To deploy the WEB API and Database on Kubernetes locally, with Docker Desktop, you can use the Helm chart provided in the folder ``kubernetes/helm``, and run the command: ``make helm-install``. 
On a Production environment you can use the Helm chart as well but you will need to push your custom WEB API Docker image to a registry in order to provide Kubernetes nodes a way pull it when deploying the container. By default kubernetes uses docker.io public registry. 

For the WEB API, a deployment was used since it is stateless and to ensure that a minimum number of replicas, as configured, are up and running even in a case of failure such as a node being down. Apart from that it can be easily scaled to more replicas if needed to serve more client traffic. For the Database, a deployment was used as well since this is a simple exercise, however, in a Production environment it would make more sense to deploy the Database as a ``StatefulSet``, so the pod replicas are aware of the state, and with persistent storage so no data is lost in case of a pod being shutdown or fails.

In order to scale the WEB API automatically an Horizontal Pod Autoscaler (HPA) is deployed as well, however to work the cluster needs to provide the ``metrics.k8s.io`` API which is usually provided by an add-on named ``Metrics Server``, that needs to be launched separately. 
In the example provided in the Helm chart, Kubernetes will create new replicas, to the maximum of 3 replicas, of the WEB API pod every time that the cpu load is above 50%. And scale back down to 1 replica if the load reduces.
Note that different configurations for different metrics (for instance memory usage, number of requests, etc) can be configured using custom implementations of the autoscaler.

In order to reach the API you would also need a Kubernetes Service, since the Pod IP address is not static and can be different every time a new pod is deployed. Furthermore, the service provides Load-Balancing capabilities whenever more that one replica is running. An example of a simple NodePort service is deployed with the Helm chart. This service will open a port on the Kubernetes nodes to allow access to the service from outside the cluster, similar to port-forwarding.

To reach the API from outside the cluster you can also use an Ingress with a simpler ``ClusterIP`` service type. You would also need an Ingress Controller such as the simple and widely used ``NGINX Ingress Controller``. 

To monitor your WEB API there are different approaches that can be used:
* The simpler one is to use the Kubernetes API with kubectl commands such as ``kubectl get pods``, ``kubectl describe pod <name_of_the_pod>``, ``kubectl logs <name_of_the_pod>``. This approach is more useful for the deployment phase and to troubleshoot some possible problems that may occur when deploying.
* To passively monitor your application, that is, to collect metrics for status and performance for example, there are multiple tools that can be integrated in the Kubernetes cluster. You can use the simple metrics API that was addressed abovee: ``Metrics Server``. However, the most common tools for monitoring Kubernetes are Prometheus and Grafana, for collecting metrics and disply them using graphs and dashboards, respectively. They can be easily integrated with the cluster and collect metrics from the pods, such as CPU, MEM, network traffic, number of request and much more. With the metrics collected you can easily create dashboards to display the information and create alerts to be triggered and send an email, slack message or other notification when a metric value crosses a defined threshold.

## Test the application

In order to test the application a simple test file was produced (``test_revolut_code_challenge_server.py``) that tests 7 cases:
* Test the database connection.
* Make a valid ``PUT`` request and check the response status code.
* Make a ``GET`` request and check the response message and status code.
* Make a ``PUT`` request with a ``dateOfBirth`` in the future and check the response message and status code.
* Make a ``GET`` request with an invalid ``username`` and check the response message and status code.
* Make a ``PUT`` request with an invalid ``dateOfBirth`` and check the response message and status code.
* Make a ``PUT`` request without body
  
To run the tests you can simply run: ``make test``.

## System diagram for an example of the solution deployed to AWS
![System Diagram](/revolut-challenge-system-diagram.png)
