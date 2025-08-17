#!/usr/bin/env python3

"""
Test script for FastWG import functionality
Can be run on remote machine to test the fixes
"""

import os
import sys
import tempfile

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastwg.core.wireguard import WireGuardManager
from fastwg.core.database import Database

def create_test_config():
    """Create a test WireGuard config file"""
    config_content = """[Interface]
Address = 10.42.42.1/24
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o ens3 -j MASQUERADE
ListenPort = 51820
PrivateKey = uHVgQ1FmX598gJIYiO9DxR7SS/U+5nfCqBFArueePVo=

[Peer]
# client1
PublicKey = 8wZQAnND4Gr4QfbYbGIIIhgmtyIpZBtQ3F51TCkSFw8=
AllowedIPs = 10.42.42.2/32
Endpoint = 5.35.114.145:33887

[Peer]
# client2
PublicKey = 0tYIPr1SUz+M3dUgbom+PVSmKTRgotN1nDfdXeJRkmA=
AllowedIPs = 10.42.42.3/32

[Peer]
# client3
PublicKey = wzJOQNhUK49H2yAHEGcQNsuEX0t98QMiMpnE7vndRzI=
AllowedIPs = 10.42.42.4/32
Endpoint = 5.35.114.145:49424

[Peer]
# client4
PublicKey = MzKX1k4UW1T6E7NfrT0YG5cNFfK6B6K2WfXIjgsncU8=
AllowedIPs = 10.42.42.5/32
Endpoint = 5.35.114.145:64163

[Peer]
# client5
PublicKey = 48O/cnQROD4DVLziQB6ZRgPDtgiOto3PK5uVGFv29WA=
AllowedIPs = 10.42.42.6/32
Endpoint = 5.35.114.145:55674

[Peer]
# client6
PublicKey = towH7ZkYHWNR+alSiRM9El1VjWdM/sxLv6sXM4fQnkU=
AllowedIPs = 10.42.42.7/32
Endpoint = 213.87.162.215:12901

[Peer]
# client7
PublicKey = EYCoo9B7umIJt4tm6noblQsyI6IhiH98bWlxDYyv8QY=
AllowedIPs = 10.42.42.8/32

[Peer]
# client8
PublicKey = 8els5AB/4cf1PMYLVG0r53zu6Pa8BQoe2vsiNLzndjw=
AllowedIPs = 10.42.42.9/32
"""
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write(config_content)
        return f.name

def test_import():
    """Test the import functionality"""
    print("🧪 Testing FastWG Import Functionality")
    print("=" * 50)
    
    # Create test config
    config_path = create_test_config()
    print(f"📁 Created test config: {config_path}")
    
    try:
        # Initialize WireGuard manager with temp directory and temp database
        temp_dir = os.path.dirname(config_path)
        
        # Create temporary database
        import tempfile
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        # Initialize database with temp file
        db = Database(db_path=temp_db.name)
        db._init_database()
        
        # Initialize WireGuard manager
        wg = WireGuardManager(config_dir=temp_dir)
        wg.db = db  # Use our temp database
        
        # Test scan
        print("\n🔍 Testing scan_existing_configs:")
        configs = wg.scan_existing_configs()
        print(f"Found {len(configs)} config(s)")
        
        for config in configs:
            print(f"  - {config['filename']}")
        
        # Test import
        print(f"\n📥 Testing import_existing_config:")
        success = wg.import_existing_config(config_path)
        print(f"Import result: {'✅ Success' if success else '❌ Failed'}")
        
        # Test list clients
        print(f"\n📋 Testing list_clients:")
        clients = wg.list_clients()
        print(f"Found {len(clients)} client(s)")
        
        for client in clients:
            status = []
            if client['is_active']:
                status.append("Active")
            else:
                status.append("Inactive")
            
            if client['is_blocked']:
                status.append("Blocked")
            
            if client['is_connected']:
                status.append("Connected")
            else:
                status.append("Disconnected")
            
            status_str = ", ".join(status)
            print(f"  - {client['name']} ({client['ip_address']}) - {status_str}")
        
        # Test with --all logic
        print(f"\n🔍 Testing '--all' logic:")
        all_clients = [c for c in clients]  # All clients
        active_clients = [c for c in clients if c['is_active'] and not c['is_blocked']]
        
        print(f"All clients: {len(all_clients)}")
        print(f"Active clients: {len(active_clients)}")
        
        if len(all_clients) != 8:
            print("❌ Expected 8 clients, but found different number!")
        else:
            print("✅ All 8 clients imported successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        os.unlink(config_path)
        os.unlink(temp_db.name)
        print(f"\n🧹 Cleaned up test files")

if __name__ == "__main__":
    test_import()
