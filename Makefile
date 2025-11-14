PROFILE ?= default
WORKSPACE_LOCATION ?= $(PWD)
GLUE_IMAGE = public.ecr.aws/glue/aws-glue-libs:5
CONTAINER_NAME = glue5_pyspark
SSO ?= false

.PHONY: run clean stop remove start exec install

# --- Lógica Condicional de AWS (Manejada por MAKE) ---
ifeq ($(SSO),true)
AWS_LOGIN_CHECK = \
	@echo "Verificando credenciales AWS SSO para perfil '$(PROFILE)'..." && \
	if ! aws sts get-caller-identity --profile $(PROFILE) > /dev/null 2>&1; then \
		echo "No hay sesión válida, ejecutando 'aws sso login'..." && \
		aws sso login --profile $(PROFILE); \
	else \
		echo "Sesión SSO válida."; \
	fi
else
AWS_LOGIN_CHECK = @echo "Usando credenciales AWS normales (sin SSO)..."
endif
# -----------------------------------------------------

run:
	$(AWS_LOGIN_CHECK)
	@echo "Limpiando contenedor Docker viejo (si existe)..."
	-@docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	@echo "Creando contenedor Glue 5.0 (modo persistente)..."
	docker run -dit \
		-v ~/.aws:/home/hadoop/.aws \
		-v $(WORKSPACE_LOCATION):/home/hadoop/workspace/my_etl_lib \
		-e AWS_PROFILE=$(PROFILE) \
		--name $(CONTAINER_NAME) \
		$(GLUE_IMAGE) \
		pyspark

install:
	@echo "Instalando librerías en el contenedor $(CONTAINER_NAME) desde requirements.txt..."
	@if [ ! -f $(WORKSPACE_LOCATION)/requirements.txt ]; then \
		echo "No se encontró requirements.txt en $(WORKSPACE_LOCATION)/my_etl_lib"; exit 1; \
	fi
	docker exec -it $(CONTAINER_NAME) pip install --upgrade pip
	docker exec -it $(CONTAINER_NAME) pip install --user -r /home/hadoop/workspace/my_etl_lib/requirements.txt
	@echo "Iniciando contenedor $(CONTAINER_NAME)..."
	#docker start -ai $(CONTAINER_NAME)

stop:
	@echo "Deteniendo contenedor $(CONTAINER_NAME)..."
	-@docker stop $(CONTAINER_NAME) 2>/dev/null || echo "Contenedor no está corriendo."

remove:
	@echo "Eliminando contenedor $(CONTAINER_NAME)..."
	-@docker rm -f $(CONTAINER_NAME) 2>/dev/null || echo "Contenedor no existe o ya fue eliminado."

exec:
	docker exec -it $(CONTAINER_NAME) sh