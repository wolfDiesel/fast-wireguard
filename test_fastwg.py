#!/usr/bin/env python3

"""
Простой тест для FastWG
"""

import os
import sys
import tempfile
import shutil
from fastwg.core.wireguard import WireGuardManager
from fastwg.core.database import Database


def test_database():
    """Тестирует работу с базой данных"""
    print("Тестирование базы данных...")
    
    # Создаем временную базу данных
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        db = Database(db_path)
        
        # Тестируем создание клиента
        from fastwg.models import Client
        from datetime import datetime
        
        client = Client(
            id=None,
            name="test_client",
            public_key="test_public_key",
            private_key="test_private_key",
            ip_address="10.0.0.2",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None
        )
        
        # Добавляем клиента
        success = db.add_client(client)
        print(f"Добавление клиента: {'✓' if success else '✗'}")
        
        # Получаем клиента
        retrieved_client = db.get_client("test_client")
        print(f"Получение клиента: {'✓' if retrieved_client else '✗'}")
        
        if retrieved_client:
            print(f"  Имя: {retrieved_client.name}")
            print(f"  IP: {retrieved_client.ip_address}")
        
        # Получаем всех клиентов
        all_clients = db.get_all_clients()
        print(f"Всего клиентов: {len(all_clients)}")
        
        # Удаляем клиента
        deleted = db.delete_client("test_client")
        print(f"Удаление клиента: {'✓' if deleted else '✗'}")
        
    finally:
        # Удаляем временную базу данных
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    print("Тест базы данных завершен\n")


def test_wireguard_manager():
    """Тестирует WireGuard менеджер"""
    print("Тестирование WireGuard менеджера...")
    
    # Создаем временные директории
    temp_dir = tempfile.mkdtemp()
    config_dir = os.path.join(temp_dir, "config")
    keys_dir = os.path.join(temp_dir, "keys")
    
    try:
        # Создаем менеджер
        wg = WireGuardManager(config_dir, keys_dir)
        
        # Проверяем создание директорий
        print(f"Создание директорий: {'✓' if os.path.exists(config_dir) else '✗'}")
        print(f"  Config dir: {config_dir}")
        print(f"  Keys dir: {keys_dir}")
        
        # Тестируем генерацию ключей
        private_key = wg._generate_private_key()
        public_key = wg._generate_public_key(private_key)
        
        print(f"Генерация ключей: {'✓' if private_key and public_key else '✗'}")
        print(f"  Private key length: {len(private_key)}")
        print(f"  Public key length: {len(public_key)}")
        
        # Тестируем сканирование конфигураций
        configs = wg.scan_existing_configs()
        print(f"Сканирование конфигураций: {'✓' if isinstance(configs, list) else '✗'}")
        print(f"  Найдено конфигураций: {len(configs)}")
        
    finally:
        # Удаляем временные директории
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("Тест WireGuard менеджера завершен\n")


def main():
    """Основная функция тестирования"""
    print("=" * 50)
    print("Тестирование FastWG")
    print("=" * 50)
    
    test_database()
    test_wireguard_manager()
    
    print("Все тесты завершены!")


if __name__ == "__main__":
    main()
