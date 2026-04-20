FROM apache/airflow:3.2.0

# Copiamos o arquivo para dentro do container
COPY requirements.txt /requirements.txt

# O usuário airflow já tem permissão para instalar no seu próprio PATH
USER airflow

RUN pip install --no-cache-dir --user -r /requirements.txt