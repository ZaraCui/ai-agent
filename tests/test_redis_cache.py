"""
Test script for Redis cache functionality
Run this script to verify Redis cache is working correctly
"""
import sys
import os

# Add parent directory to path to import agent modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.cache import cache
import json
import time


def test_connection():
    """Test Redis connection"""
    print("\n=== Testing Redis Connection ===")
    stats = cache.get_stats()
    
    if stats.get('enabled'):
        if stats.get('connected'):
            print("✓ Redis is enabled and connected")
            print(f"  Keys in cache: {stats.get('keys_count', 0)}")
            print(f"  Memory used: {stats.get('used_memory', 'N/A')}")
        else:
            print("✗ Redis is enabled but not connected")
            print(f"  Error: {stats.get('error', 'Unknown')}")
            return False
    else:
        print("⚠ Redis is disabled")
        print("  To enable, set REDIS_ENABLED=True in .env file")
        return False
    
    return True


def test_basic_operations():
    """Test basic cache operations"""
    print("\n=== Testing Basic Cache Operations ===")
    
    # Test SET
    test_key = "test:sample"
    test_value = {"message": "Hello Redis!", "timestamp": time.time()}
    
    print(f"Setting cache key: {test_key}")
    success = cache.set(test_key, test_value, ttl=300)
    
    if success:
        print("✓ Cache SET successful")
    else:
        print("✗ Cache SET failed")
        return False
    
    # Test GET
    print(f"Getting cache key: {test_key}")
    retrieved = cache.get(test_key)
    
    if retrieved and retrieved.get('message') == test_value['message']:
        print("✓ Cache GET successful")
        print(f"  Retrieved: {json.dumps(retrieved, indent=2)}")
    else:
        print("✗ Cache GET failed")
        return False
    
    # Test DELETE
    print(f"Deleting cache key: {test_key}")
    deleted = cache.delete(test_key)
    
    if deleted:
        print("✓ Cache DELETE successful")
    else:
        print("✗ Cache DELETE failed")
        return False
    
    # Verify deletion
    retrieved_after_delete = cache.get(test_key)
    if retrieved_after_delete is None:
        print("✓ Key successfully deleted (GET returns None)")
    else:
        print("✗ Key still exists after deletion")
        return False
    
    return True


def test_pattern_operations():
    """Test pattern-based operations"""
    print("\n=== Testing Pattern-Based Operations ===")
    
    # Create multiple keys
    test_keys = [
        ("test:pattern:1", {"data": "value1"}),
        ("test:pattern:2", {"data": "value2"}),
        ("test:pattern:3", {"data": "value3"}),
    ]
    
    print("Creating test keys with pattern 'test:pattern:*'")
    for key, value in test_keys:
        cache.set(key, value, ttl=300)
    
    print(f"✓ Created {len(test_keys)} test keys")
    
    # Clear by pattern
    print("Clearing keys matching pattern 'test:pattern:*'")
    cleared_count = cache.clear_pattern("test:pattern:*")
    
    if cleared_count == len(test_keys):
        print(f"✓ Successfully cleared {cleared_count} keys")
    else:
        print(f"⚠ Expected to clear {len(test_keys)} keys, but cleared {cleared_count}")
    
    # Verify clearing
    remaining = sum(1 for key, _ in test_keys if cache.get(key) is not None)
    if remaining == 0:
        print("✓ All keys successfully cleared")
        return True
    else:
        print(f"✗ {remaining} keys still remain")
        return False


def test_cache_performance():
    """Test cache performance"""
    print("\n=== Testing Cache Performance ===")
    
    test_data = {
        "city": "Shanghai",
        "spots": [
            {"name": f"Spot {i}", "lat": 31.23 + i*0.01, "lon": 121.47 + i*0.01}
            for i in range(100)
        ]
    }
    
    cache_key = "test:performance"
    
    # Test write performance
    start_time = time.time()
    cache.set(cache_key, test_data, ttl=300)
    write_time = (time.time() - start_time) * 1000
    
    print(f"✓ Write time: {write_time:.2f}ms")
    
    # Test read performance
    start_time = time.time()
    retrieved = cache.get(cache_key)
    read_time = (time.time() - start_time) * 1000
    
    print(f"✓ Read time: {read_time:.2f}ms")
    
    # Verify data integrity
    if retrieved and len(retrieved.get('spots', [])) == 100:
        print(f"✓ Data integrity verified (100 spots)")
    else:
        print("✗ Data integrity check failed")
        return False
    
    # Cleanup
    cache.delete(cache_key)
    
    return True


def run_all_tests():
    """Run all cache tests"""
    print("=" * 60)
    print("Redis Cache Test Suite")
    print("=" * 60)
    
    # Test connection
    if not test_connection():
        print("\n❌ Cannot proceed without Redis connection")
        print("\nTo fix:")
        print("1. Make sure Redis is running (redis-server)")
        print("2. Set REDIS_ENABLED=True in .env file")
        print("3. Check Redis connection settings in .env")
        return False
    
    # Run tests
    tests = [
        ("Basic Operations", test_basic_operations),
        ("Pattern Operations", test_pattern_operations),
        ("Performance", test_cache_performance),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ Test '{test_name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
