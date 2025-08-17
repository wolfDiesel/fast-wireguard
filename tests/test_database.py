#!/usr/bin/env python3

import os
import sys
import tempfile

# Добавляем путь к модулям проекта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest  # noqa: E402
from datetime import datetime  # noqa: E402

from fastwg.core.database import Database  # noqa: E402
from fastwg.models.client import Client  # noqa: E402
from fastwg.models.server import Server  # noqa: E402


class TestDatabase(unittest.TestCase):
    """Тесты для работы с базой данных"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временную базу данных
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = Database(db_path=self.temp_db.name)
        self.db._init_database()

    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временную базу данных
        os.unlink(self.temp_db.name)

    def test_add_and_get_client(self):
        """Тест добавления и получения клиента"""
        # Создаем тестового клиента
        client = Client(
            id=1,
            name="test_client",
            public_key="test_public_key",
            private_key="test_private_key",
            ip_address="10.0.0.2",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None,
        )

        # Добавляем клиента
        self.db.add_client(client)

        # Получаем клиента
        retrieved_client = self.db.get_client("test_client")

        # Проверяем что клиент получен правильно
        self.assertIsNotNone(retrieved_client)
        self.assertEqual(retrieved_client.name, "test_client")
        self.assertEqual(retrieved_client.public_key, "test_public_key")
        self.assertEqual(retrieved_client.ip_address, "10.0.0.2")

    def test_get_nonexistent_client(self):
        """Тест получения несуществующего клиента"""
        client = self.db.get_client("nonexistent")
        self.assertIsNone(client)

    def test_get_all_clients(self):
        """Тест получения всех клиентов"""
        # Добавляем несколько клиентов
        client1 = Client(
            id=1,
            name="client1",
            public_key="key1",
            private_key="priv1",
            ip_address="10.0.0.2",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None,
        )
        client2 = Client(
            id=2,
            name="client2",
            public_key="key2",
            private_key="priv2",
            ip_address="10.0.0.3",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None,
        )

        self.db.add_client(client1)
        self.db.add_client(client2)

        # Получаем всех клиентов
        all_clients = self.db.get_all_clients()

        # Проверяем количество
        self.assertEqual(len(all_clients), 2)

        # Проверяем что оба клиента есть
        client_names = [c.name for c in all_clients]
        self.assertIn("client1", client_names)
        self.assertIn("client2", client_names)

    def test_delete_client(self):
        """Тест удаления клиента"""
        # Добавляем клиента
        client = Client(
            id=1,
            name="to_delete",
            public_key="key",
            private_key="priv",
            ip_address="10.0.0.2",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None,
        )
        self.db.add_client(client)

        # Проверяем что клиент добавлен
        self.assertIsNotNone(self.db.get_client("to_delete"))

        # Удаляем клиента
        self.db.delete_client("to_delete")

        # Проверяем что клиент удален
        self.assertIsNone(self.db.get_client("to_delete"))

    def test_update_client_status(self):
        """Тест обновления статуса клиента"""
        # Добавляем клиента
        client = Client(
            id=1,
            name="test_client",
            public_key="key",
            private_key="priv",
            ip_address="10.0.0.2",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None,
        )
        self.db.add_client(client)

        # Обновляем статус
        self.db.update_client_status("test_client", is_active=False, is_blocked=True)

        # Получаем обновленного клиента
        updated_client = self.db.get_client("test_client")

        # Проверяем изменения
        self.assertFalse(updated_client.is_active)
        self.assertTrue(updated_client.is_blocked)

    def test_update_client_last_seen(self):
        """Тест обновления времени последнего подключения"""
        # Добавляем клиента
        client = Client(
            id=1,
            name="test_client",
            public_key="key",
            private_key="priv",
            ip_address="10.0.0.2",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None,
        )
        self.db.add_client(client)

        # Обновляем время последнего подключения
        test_time = datetime.now()
        self.db.update_client_last_seen("test_client", test_time)

        # Получаем обновленного клиента
        updated_client = self.db.get_client("test_client")

        # Проверяем что время обновлено
        self.assertEqual(updated_client.last_seen, test_time)

    def test_save_and_get_server_config(self):
        """Тест сохранения и получения конфигурации сервера"""
        # Создаем конфигурацию сервера
        server = Server(
            id=1,
            interface="wg0",
            private_key="server_private_key",
            public_key="server_public_key",
            address="10.0.0.0/24",
            port=51820,
            dns="8.8.8.8",
            mtu=1420,
            config_path="/etc/wireguard/wg0.conf",
        )

        # Сохраняем конфигурацию
        self.db.save_server_config(server)

        # Получаем конфигурацию
        retrieved_server = self.db.get_server_config()

        # Проверяем что конфигурация получена правильно
        self.assertIsNotNone(retrieved_server)
        self.assertEqual(retrieved_server.interface, "wg0")
        self.assertEqual(retrieved_server.private_key, "server_private_key")
        self.assertEqual(retrieved_server.address, "10.0.0.0/24")
        self.assertEqual(retrieved_server.port, 51820)

    def test_get_server_config_nonexistent(self):
        """Тест получения несуществующей конфигурации сервера"""
        server = self.db.get_server_config()
        self.assertIsNone(server)

    def test_client_to_dict(self):
        """Тест сериализации клиента в словарь"""
        client = Client(
            id=1,
            name="test_client",
            public_key="test_public_key",
            private_key="test_private_key",
            ip_address="10.0.0.2",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None,
        )

        client_dict = client.to_dict()

        # Проверяем что все поля присутствуют
        self.assertEqual(client_dict["name"], "test_client")
        self.assertEqual(client_dict["public_key"], "test_public_key")
        self.assertEqual(client_dict["ip_address"], "10.0.0.2")
        self.assertTrue(client_dict["is_active"])
        self.assertFalse(client_dict["is_blocked"])

    def test_server_to_dict(self):
        """Тест сериализации сервера в словарь"""
        server = Server(
            id=1,
            interface="wg0",
            private_key="server_private_key",
            public_key="server_public_key",
            address="10.0.0.0/24",
            port=51820,
            dns="8.8.8.8",
            mtu=1420,
            config_path="/etc/wireguard/wg0.conf",
        )

        server_dict = server.to_dict()

        # Проверяем что все поля присутствуют
        self.assertEqual(server_dict["interface"], "wg0")
        self.assertEqual(server_dict["private_key"], "server_private_key")
        self.assertEqual(server_dict["address"], "10.0.0.0/24")
        self.assertEqual(server_dict["port"], 51820)


if __name__ == "__main__":
    unittest.main(verbosity=2)
