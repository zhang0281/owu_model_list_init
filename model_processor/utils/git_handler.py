"""
Git子模块操作工具
"""

import subprocess
import os
from pathlib import Path
from typing import Tuple, Optional
from .logger import get_logger

logger = get_logger("GitHandler")


class GitHandler:
    """Git操作处理器"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).absolute()
        self.lobe_icons_path = self.repo_path / "lobe-icons"
    
    def update_submodule(self) -> Tuple[bool, str]:
        """
        更新git子模块
        
        Returns:
            (成功状态, 输出信息)
        """
        try:
            logger.info("开始更新git子模块...")
            
            # 切换到仓库目录
            original_cwd = os.getcwd()
            os.chdir(self.repo_path)
            
            try:
                # 执行git submodule update命令
                result = subprocess.run(
                    ["git", "submodule", "update", "--init", "--recursive"],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                
                if result.returncode == 0:
                    logger.info("Git子模块更新成功")
                    return True, result.stdout
                else:
                    logger.error(f"Git子模块更新失败: {result.stderr}")
                    return False, result.stderr
                    
            finally:
                # 恢复原始工作目录
                os.chdir(original_cwd)
                
        except subprocess.TimeoutExpired:
            logger.error("Git子模块更新超时")
            return False, "操作超时"
        except FileNotFoundError:
            logger.error("未找到git命令，请确保git已安装")
            return False, "git命令未找到"
        except Exception as e:
            logger.error(f"更新子模块时出错: {e}")
            return False, str(e)
    
    def check_submodule_status(self) -> Tuple[bool, str]:
        """
        检查子模块状态
        
        Returns:
            (状态正常, 状态信息)
        """
        try:
            original_cwd = os.getcwd()
            os.chdir(self.repo_path)
            
            try:
                result = subprocess.run(
                    ["git", "submodule", "status"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    status_output = result.stdout.strip()
                    logger.info(f"子模块状态: {status_output}")
                    
                    # 检查是否有未初始化的子模块（以-开头）
                    if status_output.startswith('-'):
                        return False, "子模块未初始化"
                    
                    return True, status_output
                else:
                    logger.error(f"检查子模块状态失败: {result.stderr}")
                    return False, result.stderr
                    
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            logger.error(f"检查子模块状态时出错: {e}")
            return False, str(e)
    
    def validate_lobe_icons(self) -> bool:
        """
        验证lobe-icons目录结构
        
        Returns:
            目录结构有效返回True
        """
        try:
            # 检查主目录
            if not self.lobe_icons_path.exists():
                logger.error("lobe-icons目录不存在")
                return False
            
            if not self.lobe_icons_path.is_dir():
                logger.error("lobe-icons不是目录")
                return False
            
            # 检查packages目录
            packages_path = self.lobe_icons_path / "packages"
            if not packages_path.exists():
                logger.error("lobe-icons/packages目录不存在")
                return False
            
            # 检查static-png目录
            static_png_path = packages_path / "static-png"
            if not static_png_path.exists():
                logger.error("lobe-icons/packages/static-png目录不存在")
                return False
            
            # 检查light目录
            light_path = static_png_path / "light"
            if not light_path.exists():
                logger.error("lobe-icons/packages/static-png/light目录不存在")
                return False
            
            # 检查是否有图标文件
            icon_files = list(light_path.glob("*.png"))
            if not icon_files:
                logger.error("lobe-icons/packages/static-png/light目录中没有PNG文件")
                return False
            
            logger.info(f"lobe-icons目录结构验证成功，找到{len(icon_files)}个图标文件")
            return True
            
        except Exception as e:
            logger.error(f"验证lobe-icons目录时出错: {e}")
            return False
    
    def get_lobe_icons_path(self) -> Optional[Path]:
        """
        获取lobe-icons图标目录路径
        
        Returns:
            图标目录路径，如果无效返回None
        """
        if self.validate_lobe_icons():
            return self.lobe_icons_path / "packages" / "static-png" / "light"
        return None
    
    def ensure_submodule_ready(self) -> bool:
        """
        确保子模块准备就绪
        
        Returns:
            准备就绪返回True
        """
        logger.info("检查lobe-icons子模块状态...")
        
        # 首先检查目录结构
        if self.validate_lobe_icons():
            logger.info("lobe-icons子模块已准备就绪")
            return True
        
        # 如果目录结构不完整，尝试更新子模块
        logger.info("lobe-icons子模块需要更新...")
        success, message = self.update_submodule()
        
        if not success:
            logger.error(f"更新子模块失败: {message}")
            return False
        
        # 再次验证
        if self.validate_lobe_icons():
            logger.info("lobe-icons子模块更新并验证成功")
            return True
        else:
            logger.error("更新后lobe-icons子模块仍然无效")
            return False
