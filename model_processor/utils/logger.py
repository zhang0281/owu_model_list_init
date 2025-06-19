"""
统一日志系统
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# 添加父目录到Python路径以支持导入config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import LOG_LEVEL, LOG_FORMAT


class Logger:
    """统一日志管理器"""
    
    def __init__(self, name: str = "ModelProcessor"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(LOG_LEVEL)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LOG_LEVEL)
        console_formatter = logging.Formatter(LOG_FORMAT)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        log_file = Path("model_processor.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(LOG_LEVEL)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """调试信息"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """一般信息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """警告信息"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """错误信息"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """严重错误"""
        self.logger.critical(message)


# 创建全局日志实例
logger = Logger()


def get_logger(name: Optional[str] = None) -> Logger:
    """获取日志实例"""
    if name:
        return Logger(name)
    return logger
