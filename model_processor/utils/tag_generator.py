"""
智能标签生成器
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Set

# 添加父目录到Python路径以支持导入config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import FUNCTION_KEYWORDS, VENDOR_TAGS, SPECIAL_RULES
from .logger import get_logger

logger = get_logger("TagGenerator")


class TagGenerator:
    """智能标签生成器"""

    def __init__(self):
        self.function_keywords = FUNCTION_KEYWORDS
        self.vendor_tags = VENDOR_TAGS
        self.special_rules = SPECIAL_RULES

        # 定义允许的标签列表（精简后的标签体系）
        self.allowed_tags = {
            # 厂商标签
            'openai', 'claude', 'gemini', 'qwen', 'deepseek', 'grok', 'meta', 'mistral',
            'google', '硅基流动', '当贝',
            # 功能标签
            '推理思考', '文生图', '图生图', '语音处理', '视频处理', '多模态', '搜索检索', '嵌入向量',
            # 属性标签
            '免费'
        }

        # 定义标签映射规则（将旧标签映射到新标签）
        self.tag_mapping = {
            # 旧的推理相关标签 -> 推理思考
            '推理模型': '推理思考',
            '增强推理': '推理思考',
            '视觉推理': '推理思考',
            '数学推理': '推理思考',
            '复杂推理': '推理思考',
            '思考推理': '推理思考',
            '自适应思维': '推理思考',
            '动态思维': '推理思考',

            # 旧的搜索相关标签 -> 搜索检索
            '信息检索': '搜索检索',
            '搜索': '搜索检索',

            # 旧的图像相关标签 -> 文生图/图生图
            '图像生成': '文生图',
            '图像处理': '文生图',

            # 旧的语音相关标签 -> 语音处理
            '语音合成': '语音处理',
            '语音识别': '语音处理',

            # 旧的视频相关标签 -> 视频处理
            '视频生成': '视频处理',

            # 旧的嵌入相关标签 -> 嵌入向量
            '嵌入模型': '嵌入向量',

            # 删除的标签（映射为None表示删除）
            '推荐': None,
            '旗舰模型': None,
            '开源模型': None,
            '开源': None,
            '长上下文': None,
            '实时交互': None,
            '对话聊天': None,
            '代码编程': None,
            '代码生成': None,
            '编程': None,
            '最强': None,
            '最大': None,
            '高质量': None,
            '最先进': None,
            '快速': None,
            '轻量': None,
            '成本效益': None,
            '低延迟': None,
            '新一代': None,
            '端到端': None,
            '实时处理': None,
            '高吞吐量': None,
        }
    
    def extract_text_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        if not text:
            return []
        
        # 转小写
        text = text.lower()
        
        # 提取中英文词汇
        chinese_words = re.findall(r'[\u4e00-\u9fff]+', text)
        english_words = re.findall(r'[a-zA-Z]+', text)
        
        return chinese_words + english_words

    def filter_allowed_tags(self, tags: List[str]) -> List[str]:
        """
        过滤标签，只保留允许的标签，并应用标签映射

        Args:
            tags: 原始标签列表

        Returns:
            过滤后的标签列表
        """
        filtered_tags = []
        for tag in tags:
            # 首先检查是否需要映射
            if tag in self.tag_mapping:
                mapped_tag = self.tag_mapping[tag]
                if mapped_tag is not None and mapped_tag not in filtered_tags:
                    filtered_tags.append(mapped_tag)
                    logger.debug(f"标签映射: {tag} -> {mapped_tag}")
                elif mapped_tag is None:
                    logger.debug(f"删除标签: {tag}")
            # 然后检查是否在允许列表中
            elif tag in self.allowed_tags:
                if tag not in filtered_tags:
                    filtered_tags.append(tag)
            else:
                logger.debug(f"过滤掉不允许的标签: {tag}")

        return filtered_tags
    
    def generate_vendor_tags(self, icon_name: str, model_name: str, model_id: str) -> List[str]:
        """
        根据图标名称生成厂商标签
        
        Args:
            icon_name: 匹配到的图标名称
            model_name: 模型名称
            model_id: 模型ID
            
        Returns:
            厂商标签列表
        """
        tags = []
        
        try:
            # 从图标名称推断厂商
            if icon_name:
                # 去掉-color后缀
                base_icon_name = icon_name.replace('-color', '')
                
                if base_icon_name in self.vendor_tags:
                    tags.extend(self.vendor_tags[base_icon_name])
            
            # 检查特殊规则
            text_to_check = f"{model_name} {model_id}".lower()
            
            for rule_key, rule_config in self.special_rules.items():
                if rule_key in text_to_check:
                    if 'tags' in rule_config:
                        tags.extend(rule_config['tags'])
            
            # 去重
            tags = list(set(tags))
            
            if tags:
                logger.debug(f"生成厂商标签: {tags}")
            
            return tags
            
        except Exception as e:
            logger.error(f"生成厂商标签时出错: {e}")
            return []
    
    def generate_function_tags(self, model_name: str, description: str) -> List[str]:
        """
        根据模型名称和描述生成功能标签
        
        Args:
            model_name: 模型名称
            description: 模型描述
            
        Returns:
            功能标签列表
        """
        tags = []
        
        try:
            # 合并文本进行分析
            text_to_analyze = f"{model_name} {description}".lower()
            
            # 检查功能关键词
            for tag_name, keywords in self.function_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in text_to_analyze:
                        tags.append(tag_name)
                        break  # 找到一个关键词就够了
            
            # 特殊逻辑：根据模型名称特征推断（使用新的精简标签）
            if any(word in text_to_analyze for word in ['thinking', 'reasoning', 'r1', 'o1']):
                if '推理思考' not in tags:
                    tags.append('推理思考')

            if any(word in text_to_analyze for word in ['image', 'vision', 'vl', 'multimodal']):
                if '多模态' not in tags:
                    tags.append('多模态')

            if any(word in text_to_analyze for word in ['search', 'web', 'browse']):
                if '搜索检索' not in tags:
                    tags.append('搜索检索')
            
            # 去重
            tags = list(set(tags))
            
            if tags:
                logger.debug(f"生成功能标签: {tags}")
            
            return tags
            
        except Exception as e:
            logger.error(f"生成功能标签时出错: {e}")
            return []
    
    def analyze_description(self, description: str) -> Dict[str, Any]:
        """
        分析模型描述，提取有用信息
        
        Args:
            description: 模型描述
            
        Returns:
            分析结果字典
        """
        if not description:
            return {}
        
        try:
            analysis = {
                'has_chinese': bool(re.search(r'[\u4e00-\u9fff]', description)),
                'has_english': bool(re.search(r'[a-zA-Z]', description)),
                'length': len(description),
                'keywords': self.extract_text_keywords(description)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"分析描述时出错: {e}")
            return {}
    
    def merge_tags(self, existing_tags: List[Dict[str, str]], new_tags: List[str]) -> List[Dict[str, str]]:
        """
        合并现有标签和新标签
        
        Args:
            existing_tags: 现有标签列表（字典格式）
            new_tags: 新标签列表（字符串格式）
            
        Returns:
            合并后的标签列表
        """
        try:
            # 提取现有标签名称
            existing_tag_names = set()
            result_tags = []
            
            # 保留现有标签
            if existing_tags:
                for tag in existing_tags:
                    if isinstance(tag, dict) and 'name' in tag:
                        tag_name = tag['name']
                        existing_tag_names.add(tag_name)
                        result_tags.append(tag)
                    elif isinstance(tag, str):
                        # 处理字符串格式的标签
                        existing_tag_names.add(tag)
                        result_tags.append({'name': tag})
            
            # 添加新标签（避免重复）
            for tag_name in new_tags:
                if tag_name and tag_name not in existing_tag_names:
                    result_tags.append({'name': tag_name})
                    existing_tag_names.add(tag_name)
            
            logger.debug(f"标签合并完成: {len(result_tags)}个标签")
            return result_tags
            
        except Exception as e:
            logger.error(f"合并标签时出错: {e}")
            return existing_tags if existing_tags else []
    
    def generate_tags(self, model_data: Dict[str, Any], icon_name: str = "") -> List[Dict[str, str]]:
        """
        为模型生成完整的标签集合

        Args:
            model_data: 模型数据字典
            icon_name: 匹配到的图标名称

        Returns:
            完整的标签列表
        """
        try:
            model_name = model_data.get('name', '')
            model_id = model_data.get('id', '')

            # 确保meta字段存在
            if 'meta' not in model_data:
                model_data['meta'] = {}

            description = model_data.get('meta', {}).get('description', '')
            existing_tags = model_data.get('meta', {}).get('tags', [])

            # 生成厂商标签
            vendor_tags = self.generate_vendor_tags(icon_name, model_name, model_id)

            # 生成功能标签
            function_tags = self.generate_function_tags(model_name, description)

            # 合并所有新标签
            all_new_tags = vendor_tags + function_tags

            # 与现有标签合并
            final_tags = self.merge_tags(existing_tags, all_new_tags)

            # 过滤标签，只保留允许的标签
            filtered_tag_names = []
            for tag in final_tags:
                if isinstance(tag, dict) and 'name' in tag:
                    filtered_tag_names.append(tag['name'])
                elif isinstance(tag, str):
                    filtered_tag_names.append(tag)

            # 应用过滤
            allowed_tag_names = self.filter_allowed_tags(filtered_tag_names)

            # 转换回字典格式
            filtered_final_tags = [{'name': tag_name} for tag_name in allowed_tag_names]

            logger.info(f"为模型 '{model_name}' 生成了 {len(filtered_final_tags)} 个标签")
            return filtered_final_tags

        except Exception as e:
            logger.error(f"生成标签时出错: {e}")
            return model_data.get('meta', {}).get('tags', [])
