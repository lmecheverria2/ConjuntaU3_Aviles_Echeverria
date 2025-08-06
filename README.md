# ConjuntaU3_Aviles_Echeverria
Integrantes: 
- Daniel Aviles
- Luis Echeverria

Flujo
crear un agricultor -> Crear 2 insumos minimos (fertilizante y semillas) -> Crear un producto con precio -> Crear una cosecha -> verificar coleccion de colas 

la verificacion se da en el get de facturas y al notar que el stock de los productos disminuyo al hacer otro get 


# 🧪 Despliegue y pruebas de microservicios con Docker y Kubernetes

Este proyecto utiliza **Docker**, **Docker Hub**, **Minikube** y **Kubernetes** para construir, desplegar y probar microservicios relacionados con Inventario, Facturación y Cosechas (Agricultor).

---

## 🚀 Construcción y publicación de imágenes Docker

### 📦 Microservicio: Inventario

```bash
cd .\inventario\
docker build -t zuix1384/ms-inventario:latest .
docker login
docker push zuix1384/ms-inventario:latest
cd ..

Microservicio: Facturas
cd .\factura\
docker build -t zuix1384/ms-facturas:latest .
docker login
docker push zuix1384/ms-facturas:latest
cd ..

Microservicio: Cosechas (Agricultor)
cd .\agricultor\
docker build -t zuix1384/ms-agricultor:latest .
docker login
docker push zuix1384/ms-agricultor:latest
cd ..
☸️ Despliegue en Kubernetes con Minikube
🧱 Iniciar Minikube
minikube start --driver=docker
kubectl get nodes

📂 Aplicar archivos YAML de Kubernetes
bash
Copiar
Editar
cd k8s

# Servicios base
kubectl apply -f .\rabbitmq.yaml
kubectl apply -f .\postgres-inventario.yaml
kubectl apply -f .\postgres-factura.yaml
kubectl apply -f .\mysql-cosechas.yaml

# Despliegue de microservicios
kubectl apply -f inventario-deployment.yaml
kubectl apply -f facturas-deployment.yaml
kubectl apply -f .\cosechas-deployment.yaml
🧪 Pruebas locales con kubectl port-forward

Inventario
kubectl port-forward pod/ms-inventario-<hash> 8000:8000

Facturas
kubectl port-forward pod/ms-facturas-<hash> 8001:8001

Cosechas
kubectl port-forward pod/ms-cosechas-<hash> 8002:8002
kubectl get pods
