"""
模型数据处理主程序
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.file_handler import FileHandler
from utils.git_handler import GitHandler
from utils.icon_matcher import IconMatcher
from utils.tag_generator import TagGenerator
from utils.logger import get_logger

logger = get_logger("MainProcessor")


class ModelProcessor:
    """模型数据处理器"""
    
    def __init__(self, base_path: str = ".."):
        self.base_path = Path(base_path).absolute()
        self.file_handler = FileHandler()
        self.git_handler = GitHandler(str(self.base_path))
        self.icon_matcher = None  # type: Optional[IconMatcher]
        self.tag_generator = TagGenerator()
        
        # 统计信息
        self.stats = {
            'total_models': 0,
            'matched_icons': 0,
            'updated_tags': 0,
            'errors': 0,
            'start_time': time.time(),
            'failed_matches': []  # 存储匹配失败的模型
        }
    
    def initialize(self) -> bool:
        """初始化处理器"""
        try:
            logger.info("开始初始化模型处理器...")
            
            # 确保lobe-icons子模块准备就绪
            if not self.git_handler.ensure_submodule_ready():
                logger.error("lobe-icons子模块初始化失败")
                return False
            
            # 获取图标目录路径
            icons_path = self.git_handler.get_lobe_icons_path()
            if not icons_path:
                logger.error("无法获取图标目录路径")
                return False
            
            # 初始化图标匹配器
            self.icon_matcher = IconMatcher(icons_path)
            
            logger.info("模型处理器初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"初始化时出错: {e}")
            return False
    
    def find_input_file(self) -> str:
        """查找输入文件"""
        logger.info("查找最新的models-export文件...")
        
        input_file = self.file_handler.find_latest_export_file(str(self.base_path))
        if not input_file:
            logger.error("未找到models-export文件")
            return ""
        
        if not self.file_handler.validate_file(input_file):
            logger.error(f"输入文件无效: {input_file}")
            return ""
        
        return input_file
    
    def process_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个模型数据"""
        try:
            model_name = model_data.get('name', '')
            model_id = model_data.get('id', '')

            logger.debug(f"处理模型: {model_name} ({model_id})")

            # 确保meta字段存在
            if 'meta' not in model_data:
                model_data['meta'] = {}

            # 匹配图标
            if self.icon_matcher is None:
                logger.error("图标匹配器未初始化")
                return model_data

            match_result = self.icon_matcher.match_icon(model_name, model_id)

            # 更新图标URL
            if match_result.matched:
                model_data['meta']['profile_image_url'] = match_result.icon_url
                self.stats['matched_icons'] += 1
                logger.debug(f"更新图标URL: {match_result.icon_url}")
            else:
                # 记录匹配失败的模型
                self.stats['failed_matches'].append({
                    'name': model_name,
                    'id': model_id
                })
                logger.debug(f"未匹配到图标，保持原有URL或设置为空")

            # 生成和更新标签（总是尝试生成标签，即使没有匹配到图标）
            new_tags = self.tag_generator.generate_tags(model_data, match_result.icon_name if match_result.matched else "")

            # 总是更新标签，即使是空列表
            model_data['meta']['tags'] = new_tags
            self.stats['updated_tags'] += 1
            logger.debug(f"更新标签: {len(new_tags)}个")

            return model_data

        except Exception as e:
            logger.error(f"处理模型时出错 {model_data.get('name', 'Unknown')}: {e}")
            self.stats['errors'] += 1
            return model_data
    
    def process_models(self, models_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理所有模型数据"""
        logger.info(f"开始处理{len(models_data)}个模型...")
        
        self.stats['total_models'] = len(models_data)
        processed_models = []
        
        for i, model_data in enumerate(models_data):
            try:
                processed_model = self.process_model(model_data)
                processed_models.append(processed_model)
                
                # 每处理100个模型输出一次进度
                if (i + 1) % 100 == 0:
                    logger.info(f"已处理 {i + 1}/{len(models_data)} 个模型")
                    
            except Exception as e:
                logger.error(f"处理第{i+1}个模型时出错: {e}")
                processed_models.append(model_data)  # 保留原数据
                self.stats['errors'] += 1
        
        logger.info("模型处理完成")
        return processed_models
    
    def generate_report(self) -> str:
        """生成处理报告"""
        elapsed_time = time.time() - self.stats['start_time']

        report = f"""
=== 模型数据处理报告 ===
处理时间: {elapsed_time:.2f}秒
总模型数: {self.stats['total_models']}
成功匹配图标: {self.stats['matched_icons']}
更新标签: {self.stats['updated_tags']}
处理错误: {self.stats['errors']}
匹配成功率: {(self.stats['matched_icons'] / max(self.stats['total_models'], 1) * 100):.1f}%"""

        # 添加匹配失败的模型列表
        if self.stats['failed_matches']:
            report += f"\n匹配失败的模型 ({len(self.stats['failed_matches'])}个):"
            for i, failed_model in enumerate(self.stats['failed_matches'], 1):
                report += f"\n  {i}. {failed_model['name']} (ID: {failed_model['id']})"
        else:
            report += "\n所有模型都成功匹配到图标！"

        report += "\n========================\n"
        return report
    
    def run(self) -> bool:
        """运行主处理流程"""
        try:
            logger.info("开始模型数据处理...")
            
            # 初始化
            if not self.initialize():
                return False
            
            # 查找输入文件
            input_file = self.find_input_file()
            if not input_file:
                return False
            
            logger.info(f"使用输入文件: {input_file}")
            
            # 加载数据
            models_data = self.file_handler.load_json(input_file)
            if not models_data:
                logger.error("加载模型数据失败")
                return False
            
            # 处理数据
            processed_data = self.process_models(models_data)
            
            # 保存结果
            output_file = str(self.base_path / "models-export-mod.json")
            if not self.file_handler.save_json(processed_data, output_file):
                logger.error("保存处理结果失败")
                return False
            
            # 生成报告
            report = self.generate_report()
            logger.info(report)
            
            logger.info(f"处理完成，结果已保存到: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"主流程执行时出错: {e}")
            return False


def main():
    """主函数"""
    try:
        processor = ModelProcessor()
        success = processor.run()
        
        if success:
            logger.info("程序执行成功")
            sys.exit(0)
        else:
            logger.error("程序执行失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
