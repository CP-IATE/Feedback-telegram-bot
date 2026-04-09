ARG PKG_FILE="./requirements.txt"

FROM python:3.11-slim AS application

ARG PKG_FILE

WORKDIR /opt/app

COPY "${PKG_FILE}" .
RUN pip install --no-cache-dir -r $PKG_FILE

COPY . .

CMD cd src && python -m main