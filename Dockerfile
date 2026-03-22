# Берем легкий образ Python
FROM python:3.11-slim

# Указываем рабочую директорию внутри контейнера
WORKDIR /app

# Сначала копируем только requirements, чтобы Docker закешировал слои
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Запускаем точку входа
CMD ["python", "main.py"]