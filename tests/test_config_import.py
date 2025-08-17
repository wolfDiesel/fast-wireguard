import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
from datetime import datetime

from fastwg.core.wireguard import WireGuardManager
from fastwg.models import Client, Server


class TestConfigImport(unittest.TestCase):
    """Tests for WireGuard configuration import"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.wg_manager = WireGuardManager(config_dir=self.temp_dir)

        self.wg_manager.db = MagicMock()

        self.wg_manager._generate_private_key = MagicMock(
            return_value="test_private_key"
        )
        self.wg_manager._generate_public_key = MagicMock(return_value="test_public_key")

    def tearDown(self):
        """Clean up after tests"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_import_config_with_new_peers(self):
        """Test: import config with new clients"""
        test_config_content = """[Interface]
PrivateKey = server_private_key
Address = 10.42.42.0/24
ListenPort = 51820
MTU = 1420

[Peer]
# eliemeer
PublicKey = peer1_public_key
AllowedIPs = 10.42.42.6/32

[Peer]
# ipad
PublicKey = peer2_public_key
AllowedIPs = 10.42.42.5/32
"""

        config_file = os.path.join(self.temp_dir, "wg0.conf")
        with open(config_file, "w") as f:
            f.write(test_config_content)

        self.wg_manager._find_client_by_ip_and_key = MagicMock(return_value=None)
        self.wg_manager.db.save_server_config = MagicMock(return_value=True)
        self.wg_manager.db.add_client = MagicMock(return_value=True)

        result = self.wg_manager.import_existing_config(config_file)

        self.assertTrue(result)

        self.wg_manager.db.save_server_config.assert_called_once()

        self.assertEqual(self.wg_manager.db.add_client.call_count, 2)

        calls = self.wg_manager.db.add_client.call_args_list

        first_client = calls[0][0][0]
        self.assertEqual(first_client.name, "host_1")
        self.assertEqual(first_client.public_key, "peer1_public_key")
        self.assertEqual(first_client.ip_address, "10.42.42.6")

        second_client = calls[1][0][0]
        self.assertEqual(second_client.name, "host_2")
        self.assertEqual(second_client.public_key, "peer2_public_key")
        self.assertEqual(second_client.ip_address, "10.42.42.5")

    def test_import_config_with_existing_peers(self):
        """Test: import config with existing clients"""
        test_config_content = """[Interface]
PrivateKey = server_private_key
Address = 10.42.42.0/24
ListenPort = 51820

[Peer]
PublicKey = existing_peer_key
AllowedIPs = 10.42.42.6/32
"""

        existing_client = Client(
            id=1,
            name="existing_client",
            public_key="existing_peer_key",
            private_key="existing_private_key",
            ip_address="10.42.42.6",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None,
            config_path=None,
        )

        self.wg_manager._find_client_by_ip_and_key = MagicMock(
            return_value=existing_client
        )
        self.wg_manager.db.save_server_config = MagicMock(return_value=True)
        self.wg_manager.db.add_client = MagicMock(return_value=True)

        config_file = os.path.join(self.temp_dir, "wg0.conf")
        with open(config_file, "w") as f:
            f.write(test_config_content)

        result = self.wg_manager.import_existing_config(config_file)

        self.assertTrue(result)

        self.wg_manager.db.save_server_config.assert_called_once()

        self.wg_manager.db.add_client.assert_not_called()

    def test_import_config_mixed_scenario(self):
        """Test: mixed scenario - new and existing clients"""
        test_config_content = """[Interface]
PrivateKey = server_private_key
Address = 10.42.42.0/24
ListenPort = 51820

[Peer]
PublicKey = existing_peer_key
AllowedIPs = 10.42.42.6/32

[Peer]
PublicKey = new_peer_key
AllowedIPs = 10.42.42.7/32
"""

        existing_client = Client(
            id=1,
            name="existing_client",
            public_key="existing_peer_key",
            private_key="existing_private_key",
            ip_address="10.42.42.6",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None,
            config_path=None,
        )

        def mock_find_client(ip, key):
            if key == "existing_peer_key":
                return existing_client
            return None

        self.wg_manager._find_client_by_ip_and_key = MagicMock(
            side_effect=mock_find_client
        )
        self.wg_manager.db.save_server_config = MagicMock(return_value=True)
        self.wg_manager.db.add_client = MagicMock(return_value=True)

        config_file = os.path.join(self.temp_dir, "wg0.conf")
        with open(config_file, "w") as f:
            f.write(test_config_content)

        result = self.wg_manager.import_existing_config(config_file)

        self.assertTrue(result)

        self.wg_manager.db.save_server_config.assert_called_once()

        self.wg_manager.db.add_client.assert_called_once()

        added_client = self.wg_manager.db.add_client.call_args[0][0]
        self.assertEqual(added_client.name, "host_1")
        self.assertEqual(added_client.public_key, "new_peer_key")
        self.assertEqual(added_client.ip_address, "10.42.42.7")

    def test_import_config_with_peer_without_public_key(self):
        """Test: import config with peer without PublicKey"""
        test_config_content = """[Interface]
PrivateKey = server_private_key
Address = 10.42.42.0/24
ListenPort = 51820

[Peer]
AllowedIPs = 10.42.42.6/32

[Peer]
PublicKey = valid_peer_key
AllowedIPs = 10.42.42.7/32
"""

        self.wg_manager._find_client_by_ip_and_key = MagicMock(return_value=None)
        self.wg_manager.db.save_server_config = MagicMock(return_value=True)
        self.wg_manager.db.add_client = MagicMock(return_value=True)

        config_file = os.path.join(self.temp_dir, "wg0.conf")
        with open(config_file, "w") as f:
            f.write(test_config_content)

        result = self.wg_manager.import_existing_config(config_file)

        self.assertTrue(result)

        self.wg_manager.db.add_client.assert_called_once()

        added_client = self.wg_manager.db.add_client.call_args[0][0]
        self.assertEqual(added_client.public_key, "valid_peer_key")

    def test_import_config_with_peer_without_allowed_ips(self):
        """Test: import config with peer without AllowedIPs"""
        test_config_content = """[Interface]
PrivateKey = server_private_key
Address = 10.42.42.0/24
ListenPort = 51820

[Peer]
PublicKey = peer_key
"""

        self.wg_manager._find_client_by_ip_and_key = MagicMock(return_value=None)
        self.wg_manager.db.save_server_config = MagicMock(return_value=True)
        self.wg_manager.db.add_client = MagicMock(return_value=True)

        config_file = os.path.join(self.temp_dir, "wg0.conf")
        with open(config_file, "w") as f:
            f.write(test_config_content)

        result = self.wg_manager.import_existing_config(config_file)

        self.assertTrue(result)

        self.wg_manager.db.add_client.assert_called_once()
        added_client = self.wg_manager.db.add_client.call_args[0][0]
        self.assertEqual(added_client.ip_address, "")

    def test_import_config_without_interface_section(self):
        """Test: import config without [Interface] section"""
        test_config_content = """[Peer]
PublicKey = peer_key
AllowedIPs = 10.42.42.6/32
"""

        config_file = os.path.join(self.temp_dir, "wg0.conf")
        with open(config_file, "w") as f:
            f.write(test_config_content)

        result = self.wg_manager.import_existing_config(config_file)

        self.assertFalse(result)

    def test_import_config_database_error(self):
        """Test: database save error"""
        test_config_content = """[Interface]
PrivateKey = server_private_key
Address = 10.42.42.0/24
ListenPort = 51820

[Peer]
PublicKey = peer_key
AllowedIPs = 10.42.42.6/32
"""

        self.wg_manager.db.save_server_config = MagicMock(return_value=False)
        self.wg_manager._find_client_by_ip_and_key = MagicMock(return_value=None)

        config_file = os.path.join(self.temp_dir, "wg0.conf")
        with open(config_file, "w") as f:
            f.write(test_config_content)

        result = self.wg_manager.import_existing_config(config_file)

        self.assertFalse(result)

    def test_find_client_by_ip_and_key(self):
        """Test: find client by IP and public key"""
        client1 = Client(
            id=1,
            name="client1",
            public_key="key1",
            private_key="private1",
            ip_address="10.42.42.6",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None,
            config_path=None,
        )

        client2 = Client(
            id=2,
            name="client2",
            public_key="key2",
            private_key="private2",
            ip_address="10.42.42.7",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None,
            config_path=None,
        )

        self.wg_manager.db.get_all_clients = MagicMock(return_value=[client1, client2])

        found_client = self.wg_manager._find_client_by_ip_and_key(
            "10.42.42.6", "different_key"
        )
        self.assertEqual(found_client, client1)

        found_client = self.wg_manager._find_client_by_ip_and_key(
            "different_ip", "key2"
        )
        self.assertEqual(found_client, client2)

        found_client = self.wg_manager._find_client_by_ip_and_key("10.42.42.8", "key3")
        self.assertIsNone(found_client)


if __name__ == "__main__":
    unittest.main()
