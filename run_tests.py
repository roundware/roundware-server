import sys
import pytest

def main():
    # test path
    test_path = 'roundware/api2/tests/'
    
    if len(sys.argv) > 1:
        if sys.argv[1].endswith('.py'):
            test_path = sys.argv[1]
            sys.argv.pop(1)
    
    # coverage 
    if '-c' in sys.argv:
        sys.argv.remove('-c')
        sys.argv.extend([
            '--cov=roundware/api2/tests',
            '--cov-report=term-missing',
            '--cov-report=html'
        ])
    
    sys.exit(pytest.main([test_path] + sys.argv[1:]))

if __name__ == '__main__':
    main() 