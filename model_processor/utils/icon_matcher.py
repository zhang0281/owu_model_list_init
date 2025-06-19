"""
智能图标匹配算法
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from config import VENDOR_MAPPING, ICON_BASE_URL
from .logger import get_logger

logger = get_logger("IconMatcher")


@dataclass
class MatchResult:
    """匹配结果"""
    matched: bool
    icon_name: str
    icon_url: str
    confidence: float
    match_type: str


class IconIndex:
    """图标索引管理器"""
    
    def __init__(self, icons_path: Path):
        self.icons_path = icons_path
        self.color_icons: Dict[str, str] = {}  # 带-color后缀的图标
        self.normal_icons: Dict[str, str] = {}  # 普通图标
        self.all_icons: Set[str] = set()  # 所有图标名称（不含扩展名）
        self._build_index()
    
    def _build_index(self):
        """构建图标索引"""
        try:
            if not self.icons_path.exists():
                logger.error(f"图标目录不存在: {self.icons_path}")
                return
            
            png_files = list(self.icons_path.glob("*.png"))
            logger.info(f"找到{len(png_files)}个PNG文件")
            
            for png_file in png_files:
                name = png_file.stem  # 不含扩展名的文件名
                self.all_icons.add(name)
                
                if name.endswith('-color'):
                    # 带颜色后缀的图标
                    base_name = name[:-6]  # 去掉-color后缀
                    self.color_icons[base_name] = name
                    self.color_icons[name] = name  # 也支持完整名称匹配
                else:
                    # 普通图标
                    self.normal_icons[name] = name
            
            logger.info(f"索引构建完成: {len(self.color_icons)}个彩色图标, {len(self.normal_icons)}个普通图标")
            
        except Exception as e:
            logger.error(f"构建图标索引时出错: {e}")
    
    def get_icon_url(self, icon_name: str) -> str:
        """获取图标URL"""
        return f"{ICON_BASE_URL}/{icon_name}.png"
    
    def find_best_match(self, icon_name: str) -> Optional[str]:
        """查找最佳匹配的图标"""
        # 优先查找彩色版本
        if icon_name in self.color_icons:
            return self.color_icons[icon_name]
        
        # 查找普通版本
        if icon_name in self.normal_icons:
            return self.normal_icons[icon_name]
        
        return None


class IconMatcher:
    """智能图标匹配器"""
    
    def __init__(self, icons_path: Path):
        self.index = IconIndex(icons_path)
    
    def normalize_name(self, name: str) -> str:
        """标准化名称"""
        if not name:
            return ""
        
        # 转小写
        name = name.lower()
        
        # 去除特殊字符，保留字母数字和连字符
        name = re.sub(r'[^a-z0-9\-_]', '', name)
        
        # 将下划线替换为连字符
        name = name.replace('_', '-')
        
        # 去除多余的连字符
        name = re.sub(r'-+', '-', name)
        name = name.strip('-')
        
        return name
    
    def extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        if not text:
            return []
        
        # 转小写并分割
        words = re.findall(r'[a-zA-Z0-9]+', text.lower())
        
        # 过滤短词和常见词
        filtered_words = []
        skip_words = {'the', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by'}
        
        for word in words:
            if len(word) >= 2 and word not in skip_words:
                filtered_words.append(word)
        
        return filtered_words
    
    def exact_match(self, model_name: str, model_id: str) -> Optional[MatchResult]:
        """精确匹配"""
        candidates = [model_name, model_id]
        
        for candidate in candidates:
            if not candidate:
                continue
            
            normalized = self.normalize_name(candidate)
            matched_icon = self.index.find_best_match(normalized)
            
            if matched_icon:
                return MatchResult(
                    matched=True,
                    icon_name=matched_icon,
                    icon_url=self.index.get_icon_url(matched_icon),
                    confidence=1.0,
                    match_type="exact"
                )
        
        return None
    
    def vendor_mapping_match(self, model_name: str, model_id: str) -> Optional[MatchResult]:
        """基于厂商映射的匹配"""
        text_to_check = f"{model_name} {model_id}".lower()
        
        for keyword, vendor in VENDOR_MAPPING.items():
            if keyword in text_to_check:
                matched_icon = self.index.find_best_match(vendor)
                if matched_icon:
                    return MatchResult(
                        matched=True,
                        icon_name=matched_icon,
                        icon_url=self.index.get_icon_url(matched_icon),
                        confidence=0.8,
                        match_type="vendor_mapping"
                    )
        
        return None
    
    def keyword_match(self, model_name: str, model_id: str) -> Optional[MatchResult]:
        """关键词匹配"""
        all_keywords = self.extract_keywords(f"{model_name} {model_id}")
        
        best_match = None
        best_confidence = 0
        
        for keyword in all_keywords:
            normalized_keyword = self.normalize_name(keyword)
            matched_icon = self.index.find_best_match(normalized_keyword)
            
            if matched_icon:
                # 计算置信度（基于关键词长度和位置）
                confidence = min(0.7, len(keyword) / 10)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = MatchResult(
                        matched=True,
                        icon_name=matched_icon,
                        icon_url=self.index.get_icon_url(matched_icon),
                        confidence=confidence,
                        match_type="keyword"
                    )
        
        return best_match
    
    def fuzzy_match(self, model_name: str, model_id: str) -> Optional[MatchResult]:
        """模糊匹配"""
        candidates = [self.normalize_name(model_name), self.normalize_name(model_id)]
        
        best_match = None
        best_confidence = 0
        
        for candidate in candidates:
            if not candidate:
                continue
            
            for icon_name in self.index.all_icons:
                # 简单的包含匹配
                if candidate in icon_name or icon_name in candidate:
                    confidence = 0.5
                    matched_icon = self.index.find_best_match(icon_name)
                    
                    if matched_icon and confidence > best_confidence:
                        best_confidence = confidence
                        best_match = MatchResult(
                            matched=True,
                            icon_name=matched_icon,
                            icon_url=self.index.get_icon_url(matched_icon),
                            confidence=confidence,
                            match_type="fuzzy"
                        )
        
        return best_match
    
    def match_icon(self, model_name: str, model_id: str) -> MatchResult:
        """
        主匹配函数，按优先级尝试各种匹配策略
        
        Args:
            model_name: 模型名称
            model_id: 模型ID
            
        Returns:
            匹配结果
        """
        logger.debug(f"开始匹配图标: name='{model_name}', id='{model_id}'")
        
        # 按优先级尝试不同的匹配策略
        strategies = [
            ("精确匹配", self.exact_match),
            ("厂商映射匹配", self.vendor_mapping_match),
            ("关键词匹配", self.keyword_match),
            ("模糊匹配", self.fuzzy_match),
        ]
        
        for strategy_name, strategy_func in strategies:
            try:
                result = strategy_func(model_name, model_id)
                if result and result.matched:
                    logger.info(f"匹配成功 [{strategy_name}]: {model_name} -> {result.icon_name} (置信度: {result.confidence:.2f})")
                    return result
            except Exception as e:
                logger.error(f"{strategy_name}匹配时出错: {e}")
        
        # 所有策略都失败，返回未匹配结果
        logger.warning(f"未找到匹配的图标: name='{model_name}', id='{model_id}'")
        return MatchResult(
            matched=False,
            icon_name="",
            icon_url="",
            confidence=0.0,
            match_type="none"
        )
