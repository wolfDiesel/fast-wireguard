import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from fastwg.core.wireguard import WireGuardManager
from fastwg.models.server import Server
from fastwg.models.client import Client


class TestClientConfigGeneration(unittest.TestCase):
    """Test client configuration generation with mocked server"""

    def setUp(self):
        """Set up test environment with mocked database"""
        self.mock_db = Mock()
        with patch("os.makedirs"):
            self.wg_manager = WireGuardManager()
        self.wg_manager.db = self.mock_db

    def test_create_client_config_with_external_ip(self):
        """Test that client config uses external IP when available"""
        # Mock server configuration with external IP
        server_config = Server(
            id=1,
            interface="wg0",
            private_key="server_private_key_base64",
            public_key="server_public_key_base64",
            address="10.42.42.1/24",
            port=51820,
            dns="8.8.8.8",
            mtu=1420,
            config_path="/etc/wireguard/wg0.conf",
            external_ip="109.120.158.164",  # External IP
        )

        # Mock client
        client = Client(
            id=1,
            name="test_client",
            private_key="client_private_key_base64",
            public_key="client_public_key_base64",
            ip_address="10.42.42.9",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=datetime.now(),
            config_path="./wireguard/configs/test_client.conf",
        )

        # Mock database methods
        self.mock_db.get_server_config.return_value = server_config
        self.mock_db.save_server_config.return_value = True

        # Mock file operations and directory creation
        with patch("builtins.open", create=True) as mock_open, patch("os.chmod") as mock_chmod:

            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            # Call the method that generates client config
            config_path = self.wg_manager._create_client_config(client)

            # Verify files were opened for writing (private key, public key, config)
            self.assertEqual(mock_open.call_count, 3)

            # Get the written content from the last call (config file)
            written_content = mock_file.write.call_args_list[-1][0][0]

            # Verify the config contains correct external IP
            self.assertIn("Endpoint = 109.120.158.164:51820", written_content)
            self.assertNotIn("Endpoint = 10.42.42.1:51820", written_content)

            # Verify other required fields
            self.assertIn("PrivateKey = client_private_key_base64", written_content)
            self.assertIn("Address = 10.42.42.9/24", written_content)
            self.assertIn("PublicKey = server_public_key_base64", written_content)
            self.assertIn("DNS = 8.8.8.8", written_content)

    def test_create_client_config_without_external_ip(self):
        """Test that client config falls back to internal IP when external IP is not set"""
        # Mock server configuration without external IP
        server_config = Server(
            id=1,
            interface="wg0",
            private_key="server_private_key_base64",
            public_key="server_public_key_base64",
            address="10.42.42.1/24",
            port=51820,
            dns="8.8.8.8",
            mtu=1420,
            config_path="/etc/wireguard/wg0.conf",
            external_ip=None,  # No external IP
        )

        # Mock client
        client = Client(
            id=1,
            name="test_client",
            private_key="client_private_key_base64",
            public_key="client_public_key_base64",
            ip_address="10.42.42.9",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=datetime.now(),
            config_path="./wireguard/configs/test_client.conf",
        )

        # Mock database methods
        self.mock_db.get_server_config.return_value = server_config
        self.mock_db.save_server_config.return_value = True

        # Mock file operations
        with patch("builtins.open", create=True) as mock_open, patch("os.chmod") as mock_chmod:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            # Call the method that generates client config
            config_path = self.wg_manager._create_client_config(client)

            # Verify files were opened for writing (private key, public key, config)
            self.assertEqual(mock_open.call_count, 3)

            # Get the written content from the last call (config file)
            written_content = mock_file.write.call_args_list[-1][0][0]

            # Verify the config falls back to internal IP
            self.assertIn("Endpoint = 10.42.42.1:51820", written_content)

            # Verify other required fields
            self.assertIn("PrivateKey = client_private_key_base64", written_content)
            self.assertIn("Address = 10.42.42.9/24", written_content)
            self.assertIn("PublicKey = server_public_key_base64", written_content)
            self.assertIn("DNS = 8.8.8.8", written_content)

    def test_create_client_config_with_empty_external_ip(self):
        """Test that client config falls back to internal IP when external IP is empty string"""
        # Mock server configuration with empty external IP
        server_config = Server(
            id=1,
            interface="wg0",
            private_key="server_private_key_base64",
            public_key="server_public_key_base64",
            address="10.42.42.1/24",
            port=51820,
            dns="8.8.8.8",
            mtu=1420,
            config_path="/etc/wireguard/wg0.conf",
            external_ip="",  # Empty external IP
        )

        # Mock client
        client = Client(
            id=1,
            name="test_client",
            private_key="client_private_key_base64",
            public_key="client_public_key_base64",
            ip_address="10.42.42.9",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=datetime.now(),
            config_path="./wireguard/configs/test_client.conf",
        )

        # Mock database methods
        self.mock_db.get_server_config.return_value = server_config
        self.mock_db.save_server_config.return_value = True

        # Mock file operations
        with patch("builtins.open", create=True) as mock_open, patch("os.chmod") as mock_chmod:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            # Call the method that generates client config
            config_path = self.wg_manager._create_client_config(client)

            # Verify files were opened for writing (private key, public key, config)
            self.assertEqual(mock_open.call_count, 3)

            # Get the written content from the last call (config file)
            written_content = mock_file.write.call_args_list[-1][0][0]

            # Verify the config falls back to internal IP
            self.assertIn("Endpoint = 10.42.42.1:51820", written_content)

    def test_create_client_config_with_different_port(self):
        """Test that client config uses correct port from server config"""
        # Mock server configuration with different port
        server_config = Server(
            id=1,
            interface="wg0",
            private_key="server_private_key_base64",
            public_key="server_public_key_base64",
            address="10.42.42.1/24",
            port=51821,  # Different port
            dns="8.8.8.8",
            mtu=1420,
            config_path="/etc/wireguard/wg0.conf",
            external_ip="109.120.158.164",
        )

        # Mock client
        client = Client(
            id=1,
            name="test_client",
            private_key="client_private_key_base64",
            public_key="client_public_key_base64",
            ip_address="10.42.42.9",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=datetime.now(),
            config_path="./wireguard/configs/test_client.conf",
        )

        # Mock database methods
        self.mock_db.get_server_config.return_value = server_config
        self.mock_db.save_server_config.return_value = True

        # Mock file operations
        with patch("builtins.open", create=True) as mock_open, patch("os.chmod") as mock_chmod:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            # Call the method that generates client config
            config_path = self.wg_manager._create_client_config(client)

            # Verify files were opened for writing (private key, public key, config)
            self.assertEqual(mock_open.call_count, 3)

            # Get the written content from the last call (config file)
            written_content = mock_file.write.call_args_list[-1][0][0]

            # Verify the config uses correct port
            self.assertIn("Endpoint = 109.120.158.164:51821", written_content)

    def test_create_client_config_with_different_dns(self):
        """Test that client config uses DNS from server config"""
        # Mock server configuration with different DNS
        server_config = Server(
            id=1,
            interface="wg0",
            private_key="server_private_key_base64",
            public_key="server_public_key_base64",
            address="10.42.42.1/24",
            port=51820,
            dns="1.1.1.1",  # Different DNS
            mtu=1420,
            config_path="/etc/wireguard/wg0.conf",
            external_ip="109.120.158.164",
        )

        # Mock client
        client = Client(
            id=1,
            name="test_client",
            private_key="client_private_key_base64",
            public_key="client_public_key_base64",
            ip_address="10.42.42.9",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=datetime.now(),
            config_path="./wireguard/configs/test_client.conf",
        )

        # Mock database methods
        self.mock_db.get_server_config.return_value = server_config
        self.mock_db.save_server_config.return_value = True

        # Mock file operations
        with patch("builtins.open", create=True) as mock_open, patch("os.chmod") as mock_chmod:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            # Call the method that generates client config
            config_path = self.wg_manager._create_client_config(client)

            # Verify files were opened for writing (private key, public key, config)
            self.assertEqual(mock_open.call_count, 3)

            # Get the written content from the last call (config file)
            written_content = mock_file.write.call_args_list[-1][0][0]

            # Verify the config uses correct DNS
            self.assertIn("DNS = 1.1.1.1", written_content)

    def test_create_client_config_complete_structure(self):
        """Test that client config has complete and correct structure"""
        # Mock server configuration
        server_config = Server(
            id=1,
            interface="wg0",
            private_key="server_private_key_base64",
            public_key="server_public_key_base64",
            address="10.42.42.1/24",
            port=51820,
            dns="8.8.8.8",
            mtu=1420,
            config_path="/etc/wireguard/wg0.conf",
            external_ip="109.120.158.164",
        )

        # Mock client
        client = Client(
            id=1,
            name="test_client",
            private_key="client_private_key_base64",
            public_key="client_public_key_base64",
            ip_address="10.42.42.9",
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=datetime.now(),
            config_path="./wireguard/configs/test_client.conf",
        )

        # Mock database methods
        self.mock_db.get_server_config.return_value = server_config
        self.mock_db.save_server_config.return_value = True

        # Mock file operations
        with patch("builtins.open", create=True) as mock_open, patch("os.chmod") as mock_chmod:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            # Call the method that generates client config
            config_path = self.wg_manager._create_client_config(client)

            # Verify files were opened for writing (private key, public key, config)
            self.assertEqual(mock_open.call_count, 3)

            # Get the written content from the last call (config file)
            written_content = mock_file.write.call_args_list[-1][0][0]

            # Verify complete config structure
            expected_lines = [
                "[Interface]",
                "PrivateKey = client_private_key_base64",
                "Address = 10.42.42.9/24",
                "DNS = 8.8.8.8",
                "#",
                "[Peer]",
                "PublicKey = server_public_key_base64",
                "Endpoint = 109.120.158.164:51820",
                "AllowedIPs = 0.0.0.0/0",
                "PersistentKeepalive = 15",
            ]

            for line in expected_lines:
                self.assertIn(line, written_content)

            # Verify config ends with newline
            self.assertTrue(written_content.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
