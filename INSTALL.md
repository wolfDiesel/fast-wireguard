# Инструкции по установке и удалению FastWG

## Предварительные требования

### Системные требования
- Linux система (Ubuntu, Debian, Fedora, RHEL, CentOS)
- Python 3.8 или выше
- Git
- Root привилегии

### Установка WireGuard

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install wireguard wireguard-tools
```

#### Fedora/RHEL/CentOS:
```bash
sudo dnf install wireguard-tools
# или
sudo yum install wireguard-tools
```

#### Arch Linux:
```bash
sudo pacman -S wireguard-tools
```

### Установка Python зависимостей
```bash
# Установка pip (если не установлен)
sudo apt install python3-pip  # Ubuntu/Debian
sudo dnf install python3-pip  # Fedora/RHEL
```

## Установка FastWG

### Способ 1: Установка из исходного кода (рекомендуемый)

```bash
# 1. Клонируем репозиторий
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard

# 2. Устанавливаем зависимости
pip install -r requirements.txt

# 3. Устанавливаем в систему
sudo pip install -e .
```

### Способ 2: Установка через setup.py

```bash
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard
sudo python setup.py install
```

### Способ 3: Создание пакета и установка

```bash
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard

# Создаем дистрибутив
python setup.py sdist bdist_wheel

# Устанавливаем созданный пакет
sudo pip install dist/fastwg-1.0.0.tar.gz
```

### Способ 4: Установка в виртуальное окружение

```bash
# Создаем виртуальное окружение
python3 -m venv fastwg_env
source fastwg_env/bin/activate

# Клонируем и устанавливаем
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard
pip install -r requirements.txt
pip install -e .

# Активируем окружение при каждом использовании
source fastwg_env/bin/activate
fastwg --help
```

## Проверка установки

```bash
# Проверяем версию
fastwg --version

# Проверяем справку
fastwg --help

# Проверяем где установлен
which fastwg

# Проверяем список команд
fastwg --help
```

## Удаление FastWG

### Способ 1: Удаление через pip

```bash
# Удаляем пакет
sudo pip uninstall fastwg

# Проверяем что удалилось
which fastwg
```

### Способ 2: Удаление вручную

```bash
# Находим где установлен fastwg
which fastwg

# Удаляем исполняемый файл
sudo rm /usr/local/bin/fastwg  # или /usr/bin/fastwg

# Удаляем пакет из Python
sudo pip uninstall fastwg
```

### Способ 3: Полная очистка

```bash
# Удаляем пакет
sudo pip uninstall fastwg

# Удаляем данные (если нужно)
sudo rm -rf /etc/wireguard/fastwg*
sudo rm -rf ~/.fastwg
sudo rm -f wireguard.db

# Удаляем директории проекта
rm -rf ~/fast-wireguard
```

### Способ 4: Удаление из виртуального окружения

```bash
# Деактивируем окружение
deactivate

# Удаляем виртуальное окружение
rm -rf fastwg_env
```

## Обновление

### Обновление из исходного кода

```bash
# Переходим в директорию проекта
cd fast-wireguard

# Обновляем код
git pull

# Переустанавливаем
sudo pip install -e . --force-reinstall
```

### Обновление через pip

```bash
# Если установлен через pip
sudo pip install --upgrade fastwg
```

## Резервное копирование

### Создание резервной копии

```bash
# Создаем резервную копию конфигураций
sudo cp -r /etc/wireguard /etc/wireguard.backup

# Создаем резервную копию базы данных
sudo cp wireguard.db wireguard.db.backup

# Создаем резервную копию конфигураций клиентов
sudo cp -r ./wireguard/configs ./wireguard/configs.backup
```

### Восстановление из резервной копии

```bash
# Восстанавливаем конфигурации сервера
sudo cp -r /etc/wireguard.backup/* /etc/wireguard/

# Восстанавливаем базу данных
cp wireguard.db.backup wireguard.db

# Восстанавливаем конфигурации клиентов
cp -r ./wireguard/configs.backup/* ./wireguard/configs/
```

## Автоматизация (опционально)

### Создание systemd сервиса

```bash
# Создаем файл сервиса
sudo tee /etc/systemd/system/fastwg.service << EOF
[Unit]
Description=FastWG WireGuard Manager
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/fastwg status
User=root

[Install]
WantedBy=multi-user.target
EOF

# Включаем сервис
sudo systemctl enable fastwg.service
sudo systemctl start fastwg.service
```

### Создание алиаса

```bash
# Добавляем алиас в ~/.bashrc
echo 'alias wg="sudo fastwg"' >> ~/.bashrc
source ~/.bashrc

# Теперь можно использовать
wg list
wg create client_name
```

## Устранение неполадок

### Ошибка "Требуются root привилегии"
```bash
# Запускайте команды с sudo
sudo fastwg create client_name
```

### Ошибка "WireGuard не установлен"
```bash
# Установите WireGuard
sudo apt install wireguard wireguard-tools  # Ubuntu/Debian
sudo dnf install wireguard-tools  # Fedora/RHEL
```

### Ошибка "Команда fastwg не найдена"
```bash
# Проверьте установку
pip list | grep fastwg

# Переустановите
sudo pip install -e . --force-reinstall

# Проверьте PATH
echo $PATH
```

### Ошибка "Permission denied"
```bash
# Проверьте права на конфигурационные файлы
ls -la /etc/wireguard/

# Исправьте права если нужно
sudo chmod 600 /etc/wireguard/*.conf
sudo chown root:root /etc/wireguard/*.conf
```

### Ошибка "Module not found"
```bash
# Переустановите зависимости
pip install -r requirements.txt --force-reinstall

# Проверьте версию Python
python3 --version
```

### Проблемы с базой данных
```bash
# Удалите поврежденную базу данных
rm wireguard.db

# Перезапустите утилиту - база создастся заново
fastwg scan
```

## Логи и отладка

### Включение отладочного режима
```bash
# Запуск с подробным выводом
sudo fastwg --debug list

# Просмотр логов systemd
sudo journalctl -u fastwg.service
```

### Проверка состояния WireGuard
```bash
# Статус WireGuard
sudo wg show

# Статус интерфейсов
sudo ip link show

# Проверка конфигураций
sudo cat /etc/wireguard/wg0.conf
```

## Безопасность

### Рекомендации по безопасности
1. Всегда используйте sudo для команд fastwg
2. Регулярно обновляйте WireGuard и систему
3. Используйте сложные имена клиентов
4. Регулярно ротируйте ключи
5. Мониторьте активные подключения

### Проверка безопасности
```bash
# Проверка прав доступа
ls -la /etc/wireguard/
ls -la ./wireguard/configs/

# Проверка активных подключений
sudo fastwg list
sudo wg show
```
