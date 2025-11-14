# Imagen base oficial de AWS Glue 5.0
FROM public.ecr.aws/glue/aws-glue-libs:5

# Cambiamos a root para instalar paquetes
USER root

# Instala JupyterLab y dependencias necesarias
RUN pip install --no-cache-dir jupyterlab ipykernel

# Crea una carpeta de trabajo
RUN mkdir -p /home/hadoop/workspace && chown -R hadoop:hadoop /home/hadoop/workspace

# Cambia de nuevo al usuario 'hadoop' (el que usa Glue)
USER hadoop
WORKDIR /home/hadoop/workspace

# Expone el puerto de Jupyter
