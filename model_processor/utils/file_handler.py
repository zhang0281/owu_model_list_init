"""
文件操作工具模块
"""

import json
import glob
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from .logger import get_logger

logger = get_logger("FileHandler")


class FileHandler:
    """文件操作处理器"""
    
    @staticmethod
    def find_latest_export_file(base_path: str = ".") -> Optional[str]:
        """
        查找最新的models-export-*.json文件
        
        Args:
            base_path: 搜索基础路径
            
        Returns:
            最新文件的路径，如果没找到返回None
        """
        try:
            # 搜索匹配的文件
            pattern = str(Path(base_path) / "models-export-*.json")
            files = glob.glob(pattern)
            
            if not files:
                logger.warning(f"未找到匹配的文件: {pattern}")
                return None
            
            # 提取文件名中的数字并排序
            file_numbers = []
            for file_path in files:
                filename = Path(file_path).name
                # 提取数字部分
                match = re.search(r'models-export-(\d+)\.json', filename)
                if match:
                    number = int(match.group(1))
                    file_numbers.append((number, file_path))
            
            if not file_numbers:
                logger.warning("找到文件但无法提取数字")
                return None
            
            # 按数字排序，取最大的
            file_numbers.sort(key=lambda x: x[0], reverse=True)
            latest_file = file_numbers[0][1]
            
            logger.info(f"找到最新的导出文件: {latest_file}")
            return latest_file
            
        except Exception as e:
            logger.error(f"查找导出文件时出错: {e}")
            return None
    
    @staticmethod
    def load_json(file_path: str) -> Optional[List[Dict[Any, Any]]]:
        """
        安全加载JSON文件
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            解析后的JSON数据，出错时返回None
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"文件不存在: {file_path}")
                return None
            
            if not path.is_file():
                logger.error(f"路径不是文件: {file_path}")
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"成功加载JSON文件: {file_path}")
            
            # 确保返回的是列表
            if isinstance(data, list):
                return data
            else:
                logger.warning(f"JSON文件内容不是列表格式: {file_path}")
                return [data] if data else []
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误 {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"加载文件时出错 {file_path}: {e}")
            return None
    
    @staticmethod
    def save_json(data: List[Dict[Any, Any]], file_path: str, indent: int = 2) -> bool:
        """
        保存数据到JSON文件
        
        Args:
            data: 要保存的数据
            file_path: 目标文件路径
            indent: JSON格式化缩进
            
        Returns:
            保存成功返回True，失败返回False
        """
        try:
            path = Path(file_path)
            
            # 确保目录存在
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            
            logger.info(f"成功保存JSON文件: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存文件时出错 {file_path}: {e}")
            return False
    
    @staticmethod
    def validate_file(file_path: str) -> bool:
        """
        验证文件有效性
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件有效返回True，否则返回False
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.error(f"文件不存在: {file_path}")
                return False
            
            if not path.is_file():
                logger.error(f"路径不是文件: {file_path}")
                return False
            
            if path.stat().st_size == 0:
                logger.error(f"文件为空: {file_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证文件时出错 {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含文件信息的字典
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {"exists": False}
            
            stat = path.stat()
            return {
                "exists": True,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "is_file": path.is_file(),
                "absolute_path": str(path.absolute())
            }
            
        except Exception as e:
            logger.error(f"获取文件信息时出错 {file_path}: {e}")
            return {"exists": False, "error": str(e)}
