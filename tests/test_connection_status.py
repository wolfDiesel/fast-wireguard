#!/usr/bin/env python3

import os
import sys

# Добавляем путь к модулям проекта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from unittest.mock import MagicMock, patch  # noqa: E402

from fastwg.core.wireguard import WireGuardManager  # noqa: E402


class TestConnectionStatus(unittest.TestCase):
    """Тесты для определения статуса подключения клиентов"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.wg_manager = WireGuardManager()

    def test_parse_handshake_time_seconds(self):
        """Тест парсинга времени в секундах"""
        time_str = "30 seconds ago"
        parsed_time = self.wg_manager._parse_handshake_time(time_str)
        expected_diff = timedelta(seconds=30)
        actual_diff = datetime.now() - parsed_time

        # Проверяем с погрешностью в 5 секунд
        self.assertLess(abs(actual_diff - expected_diff).total_seconds(), 5)

    def test_parse_handshake_time_minutes(self):
        """Тест парсинга времени в минутах"""
        time_str = "2 minutes ago"
        parsed_time = self.wg_manager._parse_handshake_time(time_str)
        expected_diff = timedelta(minutes=2)
        actual_diff = datetime.now() - parsed_time

        # Проверяем с погрешностью в 5 секунд
        self.assertLess(abs(actual_diff - expected_diff).total_seconds(), 5)

    def test_parse_handshake_time_hours(self):
        """Тест парсинга времени в часах"""
        time_str = "1 hour, 30 minutes ago"
        parsed_time = self.wg_manager._parse_handshake_time(time_str)
        expected_diff = timedelta(hours=1, minutes=30)
        actual_diff = datetime.now() - parsed_time

        # Проверяем с погрешностью в 10 секунд
        self.assertLess(abs(actual_diff - expected_diff).total_seconds(), 10)

    def test_parse_handshake_time_days(self):
        """Тест парсинга времени в днях"""
        time_str = "2 days, 5 hours ago"
        parsed_time = self.wg_manager._parse_handshake_time(time_str)
        expected_diff = timedelta(days=2, hours=5)
        actual_diff = datetime.now() - parsed_time

        # Проверяем с погрешностью в 60 секунд
        self.assertLess(abs(actual_diff - expected_diff).total_seconds(), 60)

    def test_is_peer_connected_no_handshake(self):
        """Тест: peer без handshake не подключен"""
        result = self.wg_manager._is_peer_connected(has_handshake=False, handshake_time=None)
        self.assertFalse(result)

    def test_is_peer_connected_recent_handshake(self):
        """Тест: peer с недавним handshake подключен"""
        recent_time = datetime.now() - timedelta(minutes=30)
        result = self.wg_manager._is_peer_connected(has_handshake=True, handshake_time=recent_time)
        self.assertTrue(result)

    def test_is_peer_connected_old_handshake(self):
        """Тест: peer со старым handshake не подключен"""
        old_time = datetime.now() - timedelta(hours=2)
        result = self.wg_manager._is_peer_connected(has_handshake=True, handshake_time=old_time)
        self.assertFalse(result)

    def test_is_peer_connected_exact_hour(self):
        """Тест: peer с handshake ровно час назад не подключен (граничный случай)"""
        exact_hour_time = datetime.now() - timedelta(hours=1)
        result = self.wg_manager._is_peer_connected(has_handshake=True, handshake_time=exact_hour_time)
        self.assertFalse(result)

    def test_parse_wg_show_output_simple(self):
        """Тест парсинга простого вывода wg show"""
        wg_output = """interface: wg0
  public key: test_key
  private key: (hidden)
  listening port: 51820

peer: peer1_key=
  endpoint: 1.2.3.4:1234
  allowed ips: 10.0.0.2/32
  latest handshake: 30 seconds ago
  transfer: 1.0 MiB received, 2.0 MiB sent

peer: peer2_key=
  allowed ips: 10.0.0.3/32"""

        active_peers = self.wg_manager._parse_wg_show_output(wg_output)

        # Ожидаем только peer1_key= как активный (30 секунд назад)
        expected = {"peer1_key="}
        self.assertEqual(active_peers, expected)

    def test_parse_wg_show_output_complex(self):
        """Тест парсинга сложного вывода wg show с разными временами"""
        wg_output = """interface: wg0
  public key: test_key
  private key: (hidden)
  listening port: 51820

peer: recent_peer=
  endpoint: 1.2.3.4:1234
  allowed ips: 10.0.0.2/32
  latest handshake: 30 seconds ago
  transfer: 1.0 MiB received, 2.0 MiB sent

peer: old_peer=
  endpoint: 1.2.3.5:1235
  allowed ips: 10.0.0.3/32
  latest handshake: 2 hours ago
  transfer: 1.0 MiB received, 2.0 MiB sent

peer: no_handshake_peer=
  allowed ips: 10.0.0.4/32"""

        active_peers = self.wg_manager._parse_wg_show_output(wg_output)

        # Ожидаем только recent_peer= как активный
        expected = {"recent_peer="}
        self.assertEqual(active_peers, expected)

    def test_parse_wg_show_output_real_data(self):
        """Тест с реальными данными из пользовательского примера"""
        real_wg_output = """interface: wg0
  public key: 6kW4UBw3mEuRBKkpErw7v7SnS335oIlp8Ewk9/6z8zE=
  private key: (hidden)
  listening port: 51820

peer: wzJOQNhUK49H2yAHEGcQNsuEX0t98QMiMpnE7vndRzI=
  endpoint: 5.35.114.145:63557
  allowed ips: 10.42.42.4/32
  latest handshake: 1 minute, 10 seconds ago
  transfer: 1.67 GiB received, 70.31 GiB sent

peer: 8wZQAnND4Gr4QfbYbGIIIhgmtyIpZBtQ3F51TCkSFw8=
  endpoint: 5.35.114.145:37134
  allowed ips: 10.42.42.2/32
  latest handshake: 1 minute, 35 seconds ago
  transfer: 7.85 GiB received, 206.24 GiB sent

peer: 48O/cnQROD4DVLziQB6ZRgPDtgiOto3PK5uVGFv29WA=
  endpoint: 5.35.114.145:52404
  allowed ips: 10.42.42.6/32
  latest handshake: 1 minute, 56 seconds ago
  transfer: 8.99 GiB received, 234.63 GiB sent

peer: towH7ZkYHWNR+alSiRM9El1VjWdM/sxLv6sXM4fQnkU=
  endpoint: 217.107.126.102:6464
  allowed ips: 10.42.42.7/32
  latest handshake: 1 hour, 1 minute, 13 seconds ago
  transfer: 1.11 GiB received, 11.14 GiB sent

peer: 0tYIPr1SUz+M3dUgbom+PVSmKTRgotN1nDfdXeJRkmA=
  allowed ips: 10.42.42.3/32

peer: EYCoo9B7umIJt4tm6noblQsyI6IhiH98bWlxDYyv8QY=
  allowed ips: 10.42.42.8/32"""

        active_peers = self.wg_manager._parse_wg_show_output(real_wg_output)

        # Ожидаем только 3 активных peers (с handshake < 1 часа)
        expected = {
            "wzJOQNhUK49H2yAHEGcQNsuEX0t98QMiMpnE7vndRzI=",
            "8wZQAnND4Gr4QfbYbGIIIhgmtyIpZBtQ3F51TCkSFw8=",
            "48O/cnQROD4DVLziQB6ZRgPDtgiOto3PK5uVGFv29WA=",
        }
        self.assertEqual(active_peers, expected)

    @patch("subprocess.run")
    def test_get_active_connections_mock(self, mock_run):
        """Тест получения активных подключений с моком subprocess"""
        # Мокаем вывод wg show
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """interface: wg0
  public key: test_key
  private key: (hidden)
  listening port: 51820

peer: active_peer=
  endpoint: 1.2.3.4:1234
  allowed ips: 10.0.0.2/32
  latest handshake: 30 seconds ago
  transfer: 1.0 MiB received, 2.0 MiB sent

peer: inactive_peer=
  allowed ips: 10.0.0.3/32"""

        mock_run.return_value = mock_result

        active_peers = self.wg_manager._get_active_connections()

        # Проверяем что subprocess.run был вызван
        mock_run.assert_called_once_with(["wg", "show"], capture_output=True, text=True)

        # Проверяем результат
        expected = {"active_peer="}
        self.assertEqual(active_peers, expected)

    @patch("subprocess.run")
    def test_get_active_connections_error(self, mock_run):
        """Тест обработки ошибки при получении активных подключений"""
        # Мокаем ошибку
        mock_run.side_effect = Exception("Command not found")

        active_peers = self.wg_manager._get_active_connections()

        # При ошибке должен вернуться пустой set
        self.assertEqual(active_peers, set())


if __name__ == "__main__":
    unittest.main(verbosity=2)
