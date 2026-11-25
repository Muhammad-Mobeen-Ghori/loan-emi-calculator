# Loan EMI Calculator – Kubernetes Deployment

## 1. Project Overview

The Loan EMI Calculator is a containerized web application developed using Node.js and Express.js and deployed on Kubernetes using Minikube.

The application allows users to calculate monthly loan instalments (EMI), total loan payments, and total interest. It also stores calculation history in MongoDB.

This project demonstrates containerization, Kubernetes orchestration, database replication, load balancing, self-healing, rolling updates, rollback, performance testing, resource profiling, and automatic scaling.

### Technologies Used

- Node.js
- Express.js
- HTML, Bootstrap and JavaScript
- MongoDB Replica Set
- Docker
- Kubernetes
- Minikube
- NGINX Ingress Controller
- Horizontal Pod Autoscaler (HPA)
- Python 3
- Git and GitHub

---

## 2. Project Objectives

The main objectives of this project are:

1. Develop a web-based Loan EMI Calculator.
2. Store loan calculation history in MongoDB.
3. Containerize the application using Docker.
4. Deploy the application on Kubernetes using Minikube.
5. Configure a three-member MongoDB replica set.
6. Expose the application through NGINX Ingress.
7. Implement load balancing across multiple application pods.
8. Demonstrate Kubernetes self-healing.
9. Perform rolling updates and rollback.
10. Conduct load testing at different request rates.
11. Profile CPU and memory utilization.
12. Implement Horizontal Pod Autoscaling.

---

## 3. Repository Structure

The GitHub repository is organized as follows:

```text
loan-emi-calculator/
│
├── app.js
├── Dockerfile
├── .dockerignore
├── .gitignore
│
├── k8s/
│   ├── 00-namespace.yaml
│   ├── 10-mongo-service.yaml
│   ├── 20-mongo-statefulset.yaml
│   ├── 30-mongo-init-job.yaml
│   ├── 40-emi-configmap.yaml
│   ├── 50-emi-web-deployment.yaml
│   ├── 60-emi-web-service.yaml
│   ├── 70-emi-ingress.yaml
│   └── 80-emi-hpa.yaml
│
├── milestone03/
│   ├── load_test.sh
│   ├── pods-3-replicas.txt
│   ├── pods-5-replicas.txt
│   ├── requests-3-replicas.txt
│   ├── requests-5-replicas.txt
│   ├── rolling_test.sh
│   ├── rolling-update-results.txt
│   └── screenshots/
│
├── package.json
├── package-lock.json
│
├── public/
│   └── index.html
│
├── README.md
│
├── results/
│   ├── autoscaling/
│   ├── autoscaling_host_cpu.csv
│   ├── autoscaling_pod_metrics.csv
│   ├── fixed-replicas/
│   ├── graphs/
│   ├── _host_cpu.csv
│   ├── _pod_metrics.csv
│   └── performance test CSV files
│
├── screenshot_milestone01/
│
├── screenshot_milestone02/
│
├── Screenshot_milestone4/
│
└── scripts/
    ├── generate_graphs.py
    ├── load_test.py
    ├── monitor_hpa.py
    ├── profile_system.py
    ├── run_autoscaling_test.sh
    └── run_fixed_experiments.sh
```

---

## 4. Application Description

The application is developed using Node.js and Express.js.

The frontend is available through `public/index.html`.

The backend provides the following functionality:

- Accepts loan amount, annual interest rate, and loan duration.
- Calculates monthly EMI.
- Calculates total payment.
- Calculates total interest.
- Stores calculation records in MongoDB.
- Retrieves recent calculation history.
- Provides an application health endpoint.

### Application API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application frontend |
| POST | `/api/emi` | Calculate EMI and save the record |
| GET | `/api/history` | Retrieve calculation history |
| GET | `/health` | Check application and database health |

### Sample EMI Calculation Request

```bash
curl -X POST http://emi.local/api/emi \
-H "Content-Type: application/json" \
-d '{"P":500000,"rate":12,"n":24}'
```

### Expected Calculation

For:

- Principal: 500,000
- Annual Interest Rate: 12%
- Duration: 24 months

The approximate results are:

- Monthly EMI: 23,536.74
- Total Payment: 564,881.67
- Total Interest: 64,881.67

---

## 5. Prerequisites

The following tools are required to run the project:

- Ubuntu Linux
- Docker
- Minikube
- kubectl
- Git
- Python 3
- pip
- jq
- sysstat

Install the required Ubuntu packages:

```bash
sudo apt update

sudo apt install -y \
docker.io \
curl \
git \
python3 \
python3-pip \
python3-venv \
jq \
sysstat
```

Enable and start Docker:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

Verify the installations:

```bash
docker --version
minikube version
kubectl version --client
python3 --version
git --version
```

Minikube and kubectl must be installed separately if they are not already available.

---

## 6. Clone the GitHub Repository

Clone the repository:

```bash
git clone https://github.com/Muhammad-Mobeen-Ghori/loan-emi-calculator.git
```

Navigate to the project directory:

```bash
cd loan-emi-calculator
```

---

# 7. Deploy the Complete System on a Fresh Minikube Cluster

This section explains how to bring up the complete application and database system on a fresh Minikube cluster.

All Kubernetes configuration files are available in the `k8s/` directory.

## Step 1: Start Minikube

Start Minikube using the Docker driver:

```bash
minikube start --driver=docker
```

Verify the cluster:

```bash
minikube status
kubectl get nodes
```

## Step 2: Enable Kubernetes Addons

Enable the NGINX Ingress Controller:

```bash
minikube addons enable ingress
```

Enable Metrics Server:

```bash
minikube addons enable metrics-server
```

Verify the Ingress Controller:

```bash
kubectl get pods -n ingress-nginx
```

Wait until the Ingress Controller is running.

## Step 3: Build the Docker Image

Build the application image from the project root directory:

```bash
docker build -t emi-web:1.0 .
```

The Docker build uses:

- `Dockerfile`
- `app.js`
- `package.json`
- `package-lock.json`
- `public/`

Load the image into Minikube:

```bash
minikube image load emi-web:1.0
```

Verify the image:

```bash
minikube image ls | grep emi-web
```

The application Deployment uses the locally available image.

**Note:** If deploying a newer application version, build and load the corresponding image and update the Kubernetes Deployment image reference.

## Step 4: Apply All Kubernetes Manifests

The complete Kubernetes configuration is stored in the `k8s/` directory.

Apply all Kubernetes resources with one command:

```bash
kubectl apply -f k8s/
```

This command applies the following resources:

| Manifest | Purpose |
|---|---|
| `00-namespace.yaml` | Creates the Kubernetes namespace |
| `10-mongo-service.yaml` | Creates MongoDB headless Service |
| `20-mongo-statefulset.yaml` | Deploys three MongoDB replicas |
| `30-mongo-init-job.yaml` | Initializes MongoDB replica set |
| `40-emi-configmap.yaml` | Stores application configuration |
| `50-emi-web-deployment.yaml` | Deploys the web application |
| `60-emi-web-service.yaml` | Exposes the application internally |
| `70-emi-ingress.yaml` | Configures external access |
| `80-emi-hpa.yaml` | Configures automatic scaling |

## Step 5: Verify Kubernetes Resources

Check the namespace:

```bash
kubectl get namespaces
```

Check all resources:

```bash
kubectl get all -n emi
```

Check the pods:

```bash
kubectl get pods -n emi -o wide
```

Check MongoDB StatefulSet:

```bash
kubectl get statefulset -n emi
```

Check application Deployment:

```bash
kubectl get deployment -n emi
```

Check Services:

```bash
kubectl get services -n emi
```

## Step 6: Verify MongoDB Initialization

Wait for the MongoDB StatefulSet:

```bash
kubectl rollout status statefulset/mongo -n emi --timeout=300s
```

Check the initialization Job:

```bash
kubectl get jobs -n emi
```

Check the Job logs using its actual name:

```bash
kubectl logs job/<mongo-init-job-name> -n emi
```

Verify that the replica set initialization completed successfully.

## Step 7: Wait for Application Deployment

Wait for the web application Deployment:

```bash
kubectl rollout status deployment/emi-web -n emi --timeout=300s
```

Check application pods:

```bash
kubectl get pods -n emi -o wide
```

All expected application pods should become Ready.

**Important:** `kubectl apply -f k8s/` creates the resources but does not guarantee that MongoDB initialization and application readiness finish in dependency order. Verify MongoDB initialization and pod readiness before testing the application.

---

# 8. Configure External Access Through NGINX Ingress

Get the Minikube IP address:

```bash
minikube ip
```

Add the Minikube IP to the Ubuntu hosts file.

Replace `<MINIKUBE_IP>` with the actual IP address:

```bash
echo "<MINIKUBE_IP> emi.local" | sudo tee -a /etc/hosts
```

Verify the Ingress resource:

```bash
kubectl get ingress -n emi
```

Open the application in a browser:

```text
http://emi.local
```

The application is now accessible through the NGINX Ingress Controller.

---

# 9. Verify Application Functionality

Check the application health:

```bash
curl http://emi.local/health
```

Submit a sample EMI calculation:

```bash
curl -X POST http://emi.local/api/emi \
-H "Content-Type: application/json" \
-d '{"P":500000,"rate":12,"n":24}'
```

Retrieve calculation history:

```bash
curl http://emi.local/api/history
```

The application should calculate the EMI and store the calculation record in MongoDB.

---

# 10. Verify MongoDB Replica Set

Connect to a MongoDB pod:

```bash
kubectl exec -it mongo-0 -n emi -- mongosh
```

Check replica set status:

```javascript
rs.status()
```

The MongoDB replica set consists of three members:

- mongo-0
- mongo-1
- mongo-2

One member should be PRIMARY and the remaining two should be SECONDARY.

Exit MongoDB:

```javascript
exit
```

---

# 11. Milestone 03 – Ingress, Load Balancing, Self-Healing and Rolling Updates

Milestone 03 demonstrates the availability and reliability of the Kubernetes application.

The work and supporting evidence are stored in:

```text
milestone03/
```

## 11.1 NGINX Ingress

The Ingress resource exposes the application through:

```text
http://emi.local
```

The configuration is available in:

```text
k8s/70-emi-ingress.yaml
```

Verify the Ingress:

```bash
kubectl get ingress -n emi
```

## 11.2 Load Balancing with Three Replicas

The application is deployed with three replicas.

Check the pods:

```bash
kubectl get pods -n emi -o wide
```

Run the load distribution test:

```bash
bash milestone03/load_test.sh
```

The test sends requests through the Ingress and records which application pod handles each request.

Supporting files:

- `milestone03/pods-3-replicas.txt`
- `milestone03/requests-3-replicas.txt`

## 11.3 Load Balancing with Five Replicas

Scale the application to five replicas:

```bash
kubectl scale deployment emi-web --replicas=5 -n emi
```

Verify the pods:

```bash
kubectl get pods -n emi -o wide
```

Run the load distribution test again:

```bash
bash milestone03/load_test.sh
```

Supporting files:

- `milestone03/pods-5-replicas.txt`
- `milestone03/requests-5-replicas.txt`

## 11.4 Self-Healing

Kubernetes automatically replaces failed application pods through the Deployment controller.

Delete an application pod:

```bash
kubectl get pods -n emi
```

```bash
kubectl delete pod <application-pod-name> -n emi
```

Monitor the replacement:

```bash
kubectl get pods -n emi -w
```

The Deployment creates a replacement pod to maintain the desired replica count.

## 11.5 MongoDB Primary Election

The MongoDB replica set supports primary election when the existing PRIMARY member becomes unavailable.

Check the current MongoDB replica set status:

```bash
kubectl exec mongo-0 -n emi -- mongosh --quiet --eval "rs.status()"
```

Identify the current PRIMARY and delete that MongoDB pod:

```bash
kubectl delete pod <mongo-primary-pod-name> -n emi
```

Monitor the MongoDB pods:

```bash
kubectl get pods -n emi -w
```

Check replica set status again:

```bash
kubectl exec mongo-0 -n emi -- mongosh --quiet --eval "rs.status()"
```

Verify that a new PRIMARY has been elected.

Test the application again:

```bash
curl -X POST http://emi.local/api/emi \
-H "Content-Type: application/json" \
-d '{"P":500000,"rate":12,"n":24}'
```

## 11.6 Rolling Update

The rolling update test is performed using the script:

```text
milestone03/rolling_test.sh
```

The application image is updated from version 1.0 to version 1.1.

The rolling update can be performed using:

```bash
docker build -t emi-web:1.1 .
```

Load the new image into Minikube:

```bash
minikube image load emi-web:1.1
```

Update the Deployment:

```bash
kubectl set image deployment/emi-web <container-name>=emi-web:1.1 -n emi
```

Monitor the rolling update:

```bash
kubectl rollout status deployment/emi-web -n emi
```

Check rollout history:

```bash
kubectl rollout history deployment/emi-web -n emi
```

## 11.7 Rollback

Rollback the application to the previous version:

```bash
kubectl rollout undo deployment/emi-web -n emi
```

Verify rollback:

```bash
kubectl rollout status deployment/emi-web -n emi
```

Check the current image:

```bash
kubectl get deployment emi-web -n emi -o wide
```

The detailed rolling update results are stored in:

```text
milestone03/rolling-update-results.txt
```

Screenshots and supporting evidence are stored in:

```text
milestone03/screenshots/
```

---

# 12. Milestone 04 – Load Testing, Profiling and Autoscaling

Milestone 04 evaluates application performance under different request rates and replica configurations.

The experiments use the NGINX Ingress endpoint:

```text
http://emi.local
```

Each successful POST request performs an EMI calculation and stores the result in MongoDB.

The scripts used for experiments are stored in:

```text
scripts/
```

## 12.1 Python Environment Setup

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install the required Python packages:

```bash
pip install psutil matplotlib pandas
```

Verify Metrics Server:

```bash
kubectl top pods -n emi
```

## 12.2 Fixed-Replica Load Testing

The fixed-replica experiments evaluate application performance with:

- 1 application replica
- 2 application replicas
- 3 application replicas

The request rates are:

| Test | Request Rate |
|---|---:|
| 1 | 10 requests/second |
| 2 | 25 requests/second |
| 3 | 50 requests/second |
| 4 | 100 requests/second |
| 5 | 200 requests/second |

Each experiment runs for 60 seconds.

This produces 15 fixed-replica experiments.

Run the experiments:

```bash
bash scripts/run_fixed_experiments.sh
```

The script uses:

- `load_test.py` to generate application requests.
- `profile_system.py` to monitor host CPU and Kubernetes pod resource utilization.
- Kubernetes scaling commands to change the number of application replicas.

### Results Location

Raw load testing results:

```text
results/fixed-replicas/
```

Host CPU and pod profiling results:

```text
results/
```

The CSV files contain response times, request results, CPU utilization, and memory measurements.

## 12.3 System Profiling

The profiling script is:

```text
scripts/profile_system.py
```

It collects:

- Host CPU utilization.
- Application pod CPU utilization.
- Application pod memory utilization.
- CPU utilization relative to the configured CPU request.
- Timestamp information.

The profiling data is stored in CSV files under:

```text
results/
```

## 12.4 Horizontal Pod Autoscaling

The HPA configuration is stored in:

```text
k8s/80-emi-hpa.yaml
```

The HPA uses:

| Configuration | Value |
|---|---:|
| Minimum replicas | 1 |
| Maximum replicas | 5 |
| Target CPU utilization | 50% |

Check the HPA:

```bash
kubectl get hpa -n emi
```

Describe the HPA:

```bash
kubectl describe hpa emi-web -n emi
```

Monitor autoscaling:

```bash
kubectl get hpa -n emi -w
```

## 12.5 Autoscaling Workload

The autoscaling experiment consists of three phases:

| Phase | Duration | Request Rate |
|---|---:|---:|
| Phase 1 – Low Load | 2 minutes | 10 requests/second |
| Phase 2 – High Load | 5 minutes | 100 requests/second |
| Phase 3 – Low Load | 3 minutes | 10 requests/second |

Run the autoscaling experiment:

```bash
bash scripts/run_autoscaling_test.sh
```

The experiment monitors:

- Request rate.
- Average response time.
- Successful and failed requests.
- HPA desired replicas.
- Current application replicas.
- Pod CPU utilization.
- Pod memory utilization.
- Host CPU utilization.

## 12.6 Autoscaling Results

The autoscaling experiment results are stored in:

```text
results/autoscaling/
```

The files include:

- `hpa_metrics.csv`
- `phase1_10rps.csv`
- `phase1_10rps_summary.csv`
- `phase2_100rps.csv`
- `phase2_100rps_summary.csv`
- `phase3_10rps.csv`
- `phase3_10rps_summary.csv`

Additional profiling files:

```text
results/autoscaling_host_cpu.csv
results/autoscaling_pod_metrics.csv
```

## 12.7 Generate Performance Graphs

The graph generation script is:

```text
scripts/generate_graphs.py
```

Run:

```bash
python3 scripts/generate_graphs.py
```

Three performance graphs are generated.

### Graph 1 – Average Response Time vs Request Rate

File:

```text
results/graphs/graph1_response_time.png
```

This graph compares average response time at different request rates for one, two, and three application replicas.

### Graph 2 – Pod CPU Utilization Over Time

File:

```text
results/graphs/graph2_pod_cpu.png
```

This graph shows CPU utilization of application pods during the 100 requests/second experiment with three replicas.

### Graph 3 – Autoscaling Performance

File:

```text
results/graphs/graph3_autoscaling.png
```

This graph presents:

- Request rate over time.
- Average CPU utilization over time.
- Number of application replicas over time.

The graph uses a shared time axis to compare workload changes with CPU utilization and autoscaling behavior.

---

# 13. Results and Evidence

The repository contains experiment data, graphs, screenshots, and recordings for all milestones.

## Milestone 01

Evidence is available in:

```text
screenshot_milestone01/
```

It contains:

- Application command-line execution recording.
- Database connection evidence.
- Calculation history screenshot.
- Application UI screenshot.

## Milestone 02

Evidence is available in:

```text
screenshot_milestone02/
```

It contains:

- Kubernetes resource deployment evidence.
- MongoDB replica set status.
- Port forwarding.
- Application UI.
- Deployment verification.

## Milestone 03

Evidence is available in:

```text
milestone03/screenshots/
```

It contains:

- Ingress configuration.
- Application through Ingress.
- Load distribution with three replicas.
- Load distribution with five replicas.
- Application pod deletion and self-healing.
- MongoDB primary election.
- MongoDB recovery.
- Rolling update.
- Rollout history.
- Successful rollback.
- Zero failed requests during rolling update.

## Milestone 04

Evidence is available in:

```text
Screenshot_milestone4/
```

It contains:

- HPA configuration.
- Load generator test.
- Profiling CSV files.
- Experiment screenshots and recording.

Performance graphs are available in:

```text
results/graphs/
```

Raw experimental data is available in:

```text
results/fixed-replicas/
results/autoscaling/
```

---

# 14. Monitoring and Troubleshooting

## Check All Kubernetes Resources

```bash
kubectl get all -n emi
```

## Check Pods

```bash
kubectl get pods -n emi -o wide
```

## Check Application Logs

```bash
kubectl logs deployment/emi-web -n emi
```

## Check MongoDB Logs

```bash
kubectl logs mongo-0 -n emi
```

## Check Services

```bash
kubectl get services -n emi
```

## Check Ingress

```bash
kubectl get ingress -n emi
```

## Check CPU and Memory

```bash
kubectl top pods -n emi
```

## Check HPA

```bash
kubectl get hpa -n emi
```

## Check Deployment Status

```bash
kubectl rollout status deployment/emi-web -n emi
```

## Check Minikube Status

```bash
minikube status
```

---

# 15. Cleanup

To remove the Kubernetes resources:

```bash
kubectl delete -f k8s/
```

To stop Minikube:

```bash
minikube stop
```

To delete the Minikube cluster:

```bash
minikube delete
```

**Note:** Deleting the cluster also removes its local Kubernetes resources and persistent volumes.

---

# 16. Conclusion

The Loan EMI Calculator project demonstrates the deployment and management of a containerized web application using Kubernetes.

The application uses MongoDB Replica Set for persistent data storage and NGINX Ingress for external access.

Kubernetes Deployments and Services provide application management and load balancing, while self-healing and rolling updates improve availability and reliability.

Load testing and system profiling evaluate application performance under different workloads. Horizontal Pod Autoscaler automatically adjusts the number of application replicas according to CPU utilization.

The project demonstrates practical implementation of:

- Docker containerization.
- Kubernetes orchestration.
- MongoDB replication.
- Ingress-based application access.
- Load balancing.
- Self-healing.
- Rolling updates and rollback.
- Load testing.
- CPU and memory profiling.
- Horizontal Pod Autoscaling.

---

## GitHub Repository

**Repository:**  
https://github.com/Muhammad-Mobeen-Ghori/loan-emi-calculator
