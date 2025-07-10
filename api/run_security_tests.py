#!/usr/bin/env python3
"""
Automated security test runner with rate limiting reset
"""

import requests
import time
import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reset_rate_limiting():
    """Reset rate limiting state"""
    try:
        response = requests.post("http://localhost:8000/security/reset-rate-limit", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Rate limiting reset successfully")
            return True
        else:
            logger.error(f"❌ Failed to reset rate limiting: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Error resetting rate limiting: {e}")
        return False

def check_server_health():
    """Check if server is running and healthy"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Server is healthy")
            return True
        else:
            logger.error(f"❌ Server not healthy: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Server not responding: {e}")
        return False

def run_security_tests():
    """Run the security tests"""
    try:
        logger.info("🚀 Starting security tests...")
        result = subprocess.run([sys.executable, "security_tests.py"], 
                              capture_output=True, text=True, timeout=300)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            logger.info("✅ Security tests completed successfully")
            return True
        else:
            logger.error(f"❌ Security tests failed with return code: {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("❌ Security tests timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error running security tests: {e}")
        return False

def main():
    """Main function to orchestrate the test process"""
    logger.info("🔧 Starting automated security test process...")
    
    # Step 1: Check server health
    if not check_server_health():
        logger.error("❌ Server is not running or not healthy. Please start the server first.")
        sys.exit(1)
    
    # Step 2: Reset rate limiting
    logger.info("🔄 Resetting rate limiting...")
    if not reset_rate_limiting():
        logger.error("❌ Failed to reset rate limiting. Exiting.")
        sys.exit(1)
    
    # Step 3: Wait a moment for reset to take effect
    logger.info("⏳ Waiting for rate limiting reset to take effect...")
    time.sleep(2)
    
    # Step 4: Run security tests
    logger.info("🧪 Running security tests...")
    success = run_security_tests()
    
    if success:
        logger.info("🎉 Security test process completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Security test process failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 