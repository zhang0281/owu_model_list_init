"""
智能描述生成器
"""

import re
from typing import Dict, Any, List, Optional
from model_processor.config import VENDOR_MAPPING, FUNCTION_KEYWORDS, VENDOR_TAGS, SPECIAL_RULES
from .logger import get_logger

logger = get_logger("DescriptionGenerator")


class DescriptionGenerator:
    """智能描述生成器"""

    def __init__(self):
        self.vendor_mapping = VENDOR_MAPPING
        self.function_keywords = FUNCTION_KEYWORDS
        self.vendor_tags = VENDOR_TAGS
        self.special_rules = SPECIAL_RULES
        
        # 描述模板
        self.templates = {
            '推理思考': {
                'base': '{vendor}的{version}推理模型，具备强大的逻辑思维和问题解决能力',
                'with_search': '{vendor}的{version}推理模型，具备联网搜索和深度思考能力',
                'vision': '{vendor}的{version}视觉推理模型，支持图像理解和逻辑分析'
            },
            '文生图': {
                'base': '{vendor}的{version}图像生成模型，支持高质量文本到图像转换',
                'advanced': '{vendor}的{version}图像生成模型，提供专业级的AI绘画体验'
            },
            '图生图': {
                'base': '{vendor}的{version}图像编辑模型，支持图像到图像的智能转换'
            },
            '语音处理': {
                'tts': '{vendor}的语音合成模型，提供自然流畅的文本转语音服务',
                'base': '{vendor}的语音处理模型，支持语音识别和合成功能'
            },
            '视频处理': {
                'base': '{vendor}的{version}视频生成模型，支持高质量视频内容创作'
            },
            '多模态': {
                'base': '{vendor}的{version}多模态模型，支持文本、图像、语音等多种输入',
                'vision': '{vendor}的{version}视觉语言模型，具备强大的图像理解能力'
            },
            '搜索检索': {
                'base': '{vendor}的搜索增强模型，具备联网检索和信息整合能力'
            },
            '嵌入向量': {
                'base': '{vendor}的文本嵌入模型，用于向量化和语义相似度计算'
            },
            'default': {
                'base': '{vendor}的{version}大语言模型，支持多种AI任务和对话交互',
                'free': '{vendor}的{version}大语言模型（免费版），提供基础AI对话服务'
            }
        }
        
        # 厂商中文名映射
        self.vendor_chinese = {
            'openai': 'OpenAI',
            'claude': 'Anthropic Claude',
            'anthropic': 'Anthropic',
            'gemini': 'Google Gemini',
            'google': 'Google',
            'palm': 'Google PaLM',
            'qwen': '阿里通义千问',
            'deepseek': 'DeepSeek',
            'grok': 'xAI Grok',
            'meta': 'Meta',
            'mistral': 'Mistral',
            '硅基流动': '硅基流动',
            '当贝': '当贝'
        }

    def extract_vendor_info(self, model_name: str, model_id: str, tags: List[Dict[str, str]]) -> str:
        """提取厂商信息"""
        try:
            # 从标签中提取厂商信息
            tag_names = [tag.get('name', '') for tag in tags if isinstance(tag, dict)]
            
            # 优先从标签中查找厂商
            for tag_name in tag_names:
                if tag_name in self.vendor_chinese:
                    return self.vendor_chinese[tag_name]
            
            # 从模型名称和ID中推断厂商
            text_to_check = f"{model_name} {model_id}".lower()
            
            for keyword, vendor in self.vendor_mapping.items():
                if keyword in text_to_check:
                    return self.vendor_chinese.get(vendor, vendor.title())
            
            # 默认返回
            return "AI"
            
        except Exception as e:
            logger.error(f"提取厂商信息时出错: {e}")
            return "AI"

    def extract_version_info(self, model_name: str, model_id: str) -> str:
        """提取版本信息"""
        try:
            text = f"{model_name} {model_id}".lower()
            
            # 版本模式匹配
            version_patterns = [
                r'(\d+\.\d+)',  # 2.5, 3.0 等
                r'(r\d+)',      # r1, r2 等
                r'(o\d+)',      # o1, o3 等
                r'(v\d+)',      # v3 等
                r'(\d+b)',      # 32b, 72b 等参数量
            ]
            
            versions = []
            for pattern in version_patterns:
                matches = re.findall(pattern, text)
                versions.extend(matches)
            
            if versions:
                # 优先返回数字版本
                for version in versions:
                    if re.match(r'\d+\.\d+', version):
                        return version
                return versions[0].upper()
            
            return ""
            
        except Exception as e:
            logger.error(f"提取版本信息时出错: {e}")
            return ""

    def extract_main_function(self, tags: List[Dict[str, str]], model_name: str, model_id: str) -> str:
        """提取主要功能"""
        try:
            tag_names = [tag.get('name', '') for tag in tags if isinstance(tag, dict)]
            
            # 功能优先级
            function_priority = [
                '推理思考', '文生图', '图生图', '语音处理', '视频处理', 
                '搜索检索', '嵌入向量', '多模态'
            ]
            
            # 按优先级查找功能
            for func in function_priority:
                if func in tag_names:
                    return func
            
            # 从模型名称推断功能
            text = f"{model_name} {model_id}".lower()
            
            if any(word in text for word in ['thinking', 'reasoning', 'r1', 'o1']):
                return '推理思考'
            elif any(word in text for word in ['image', 'generation', 'dall-e']):
                return '文生图'
            elif any(word in text for word in ['tts', 'speech', 'voice']):
                return '语音处理'
            elif any(word in text for word in ['search', 'web']):
                return '搜索检索'
            elif any(word in text for word in ['embedding', 'embed']):
                return '嵌入向量'
            elif any(word in text for word in ['vision', 'vl', 'multimodal']):
                return '多模态'
            
            return 'default'
            
        except Exception as e:
            logger.error(f"提取主要功能时出错: {e}")
            return 'default'

    def has_special_feature(self, model_name: str, model_id: str, tags: List[Dict[str, str]]) -> Dict[str, bool]:
        """检查特殊功能"""
        try:
            text = f"{model_name} {model_id}".lower()
            tag_names = [tag.get('name', '') for tag in tags if isinstance(tag, dict)]
            
            features = {
                'search': 'search' in text or '搜索检索' in tag_names,
                'vision': any(word in text for word in ['vision', 'vl']) or '多模态' in tag_names,
                'free': 'fovt' in text or '免费' in tag_names,
                'thinking': any(word in text for word in ['thinking', 'reasoning']),
                'advanced': any(word in text for word in ['pro', 'max', 'plus', 'ultra'])
            }
            
            return features
            
        except Exception as e:
            logger.error(f"检查特殊功能时出错: {e}")
            return {}

    def select_template(self, main_function: str, features: Dict[str, bool]) -> str:
        """选择合适的描述模板"""
        try:
            templates = self.templates.get(main_function, self.templates['default'])

            # 根据特殊功能选择模板
            if main_function == '推理思考':
                if features.get('search'):
                    return templates.get('with_search', templates['base'])
                elif features.get('vision'):
                    return templates.get('vision', templates['base'])
                else:
                    return templates['base']
            elif main_function == '文生图':
                if features.get('advanced'):
                    return templates.get('advanced', templates['base'])
                else:
                    return templates['base']
            elif main_function == '语音处理':
                # 检查是否是TTS模型
                return templates.get('tts', templates['base'])
            elif main_function == '多模态':
                if features.get('vision'):
                    return templates.get('vision', templates['base'])
                else:
                    return templates['base']
            elif main_function == 'default':
                if features.get('free'):
                    return templates.get('free', templates['base'])
                else:
                    return templates['base']
            else:
                return templates.get('base', templates['base'])

        except Exception as e:
            logger.error(f"选择模板时出错: {e}")
            return self.templates['default']['base']

    def generate_description(self, model_data: Dict[str, Any], icon_name: str = "") -> str:
        """
        生成模型描述

        Args:
            model_data: 模型数据字典
            icon_name: 匹配到的图标名称（可选）

        Returns:
            生成的描述字符串
        """
        try:
            model_name = model_data.get('name', '')
            model_id = model_data.get('id', '')

            # 确保meta字段存在
            if 'meta' not in model_data:
                model_data['meta'] = {}

            # 获取现有描述，如果已有描述则不覆盖
            existing_description = model_data.get('meta', {}).get('description')
            if existing_description and existing_description.strip():
                logger.info(f"模型 '{model_name}' 已有描述，跳过生成")
                return existing_description

            tags = model_data.get('meta', {}).get('tags', [])

            # 提取信息
            vendor = self.extract_vendor_info(model_name, model_id, tags)
            version = self.extract_version_info(model_name, model_id)
            main_function = self.extract_main_function(tags, model_name, model_id)
            features = self.has_special_feature(model_name, model_id, tags)

            # 选择模板
            template = self.select_template(main_function, features)

            # 构建描述
            description = template.format(
                vendor=vendor,
                version=version + " " if version else ""
            ).strip()

            # 清理多余空格
            description = re.sub(r'\s+', ' ', description)

            # 添加特殊说明
            if features.get('free'):
                if '免费' not in description:
                    description += "，提供免费AI服务"

            # 长度控制
            if len(description) > 200:
                description = description[:197] + "..."

            logger.info(f"为模型 '{model_name}' 生成描述: {description}")
            return description

        except Exception as e:
            logger.error(f"生成描述时出错: {e}")
            return f"{model_data.get('name', 'AI')}模型"

    def batch_generate_descriptions(self, models_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量生成描述

        Args:
            models_data: 模型数据列表

        Returns:
            处理结果统计
        """
        try:
            stats = {
                'total': len(models_data),
                'generated': 0,
                'skipped': 0,
                'errors': 0
            }

            for model_data in models_data:
                try:
                    model_name = model_data.get('name', '')
                    existing_description = model_data.get('meta', {}).get('description')

                    if existing_description and existing_description.strip():
                        stats['skipped'] += 1
                        continue

                    # 生成描述
                    description = self.generate_description(model_data)

                    # 更新模型数据
                    if 'meta' not in model_data:
                        model_data['meta'] = {}
                    model_data['meta']['description'] = description

                    stats['generated'] += 1

                except Exception as e:
                    logger.error(f"处理模型 '{model_name}' 时出错: {e}")
                    stats['errors'] += 1

            logger.info(f"批量生成完成: 总计{stats['total']}个模型，生成{stats['generated']}个，跳过{stats['skipped']}个，错误{stats['errors']}个")
            return stats

        except Exception as e:
            logger.error(f"批量生成描述时出错: {e}")
            return {'total': 0, 'generated': 0, 'skipped': 0, 'errors': 0}
