#!/usr/bin/env python3

import unittest
import sys
import os

def run_all_tests():
    """Запускает все тесты проекта"""
    
    # Добавляем путь к модулям проекта
    sys.path.insert(0, os.path.dirname(__file__))
    
    # Загружаем все тесты
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Возвращаем код выхода
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
