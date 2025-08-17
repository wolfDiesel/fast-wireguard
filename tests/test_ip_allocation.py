#!/usr/bin/env python3

import sys
import tempfile
import unittest
from unittest.mock import patch

# Add the project root to the path
sys.path.insert(0, '.')

from fastwg.core.wireguard import WireGuardManager
from fastwg.models import Server


class TestIPAllocation(unittest.TestCase):
    """Test IP address allocation logic"""

    def setUp(self):
        """Set up test environment"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        
        # Create WireGuardManager with temporary database
        with patch('fastwg.core.database.Database') as mock_db_class:
            mock_db_instance = mock_db_class.return_value
            self.wg_manager = WireGuardManager()
            # Set the database instance
            self.wg_manager.db = mock_db_instance

    def tearDown(self):
        """Clean up test environment"""
        import os
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_get_next_ip_with_server_config(self):
        """Test IP allocation when server config exists with host bits"""
        # Mock server config with host bits set
        server_config = Server(
            id=1,
            interface="wg0",
            private_key="test_private_key",
            public_key="test_public_key", 
            address="10.42.42.1/24",  # This has host bits set
            port=51820,
            dns="8.8.8.8",
            mtu=1420,
            config_path="/etc/wireguard/wg0.conf"
        )
        
        # Mock database methods
        with patch.object(self.wg_manager.db, 'get_server_config', return_value=server_config):
            with patch.object(self.wg_manager.db, 'get_all_clients', return_value=[]):
                # Should not raise ValueError
                next_ip = self.wg_manager._get_next_ip()
                
                # Should return a valid IP from the network
                self.assertTrue(next_ip.startswith("10.42.42."))
                self.assertNotEqual(next_ip, "10.42.42.1")  # Should not be server IP
                self.assertNotEqual(next_ip, "10.42.42.0")  # Should not be network address
                self.assertNotEqual(next_ip, "10.42.42.255")  # Should not be broadcast

    def test_get_next_ip_without_server_config(self):
        """Test IP allocation when no server config exists"""
        # Mock database methods
        with patch.object(self.wg_manager.db, 'get_server_config', return_value=None):
            with patch.object(self.wg_manager.db, 'get_all_clients', return_value=[]):
                # Should use default network
                next_ip = self.wg_manager._get_next_ip()
                
                # Should return a valid IP from default network
                self.assertTrue(next_ip.startswith("10.0.0."))
                self.assertNotEqual(next_ip, "10.0.0.0")  # Should not be network address
                self.assertNotEqual(next_ip, "10.0.0.255")  # Should not be broadcast

    def test_get_next_ip_avoids_existing_ips(self):
        """Test that IP allocation avoids existing client IPs"""
        from fastwg.models import Client
        from datetime import datetime
        
        # Mock server config
        server_config = Server(
            id=1,
            interface="wg0",
            private_key="test_private_key",
            public_key="test_public_key",
            address="10.42.42.1/24",
            port=51820,
            dns="8.8.8.8",
            mtu=1420,
            config_path="/etc/wireguard/wg0.conf"
        )
        
        # Mock existing clients
        existing_clients = [
            Client(
                id=1,
                name="client1",
                public_key="key1",
                private_key="priv1",
                ip_address="10.42.42.10",
                is_active=True,
                is_blocked=False,
                created_at=datetime.now(),
                last_seen=None
            ),
            Client(
                id=2,
                name="client2", 
                public_key="key2",
                private_key="priv2",
                ip_address="10.42.42.20",
                is_active=True,
                is_blocked=False,
                created_at=datetime.now(),
                last_seen=None
            )
        ]
        
        # Mock database methods
        with patch.object(self.wg_manager.db, 'get_server_config', return_value=server_config):
            with patch.object(self.wg_manager.db, 'get_all_clients', return_value=existing_clients):
                next_ip = self.wg_manager._get_next_ip()
                
                # Should not return existing IPs
                self.assertNotEqual(next_ip, "10.42.42.10")
                self.assertNotEqual(next_ip, "10.42.42.20")
                # Should return a valid IP from the network
                self.assertTrue(next_ip.startswith("10.42.42."))


if __name__ == '__main__':
    unittest.main()
