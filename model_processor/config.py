"""
配置文件 - 包含映射规则和系统配置
"""

import logging

# 日志配置
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 图标相关配置
ICON_BASE_PATH = "lobe-icons/packages/static-png/light"
ICON_BASE_URL = "https://registry.npmmirror.com/@lobehub/icons-static-png/latest/files/light"

# 厂商名称映射 - 将模型名称关键词映射到对应的图标文件名
VENDOR_MAPPING = {
    # OpenAI系列
    'gpt': 'openai',
    'openai': 'openai',
    'dall-e': 'dalle',
    'dalle': 'dalle',
    'o1': 'openai',
    'o3': 'openai',  # o3-mini 等模型
    'text-embedding': 'openai',  # text-embedding-3-small 等嵌入模型
    'omni-moderation': 'openai',  # omni-moderation-latest 等审核模型
    'tts': 'openai',  # tts-1 等语音合成模型
    
    # Anthropic系列
    'claude': 'claude',
    'anthropic': 'anthropic',
    
    # Google系列
    'gemini': 'gemini',
    'palm': 'palm',
    'bard': 'gemini',
    'google': 'google',
    'vertex': 'vertexai',
    'imagen': 'gemini',
    'chat-bison': 'palm',  # chat-bison-001 等 PaLM 模型
    'text-bison': 'palm',  # text-bison-001 等 PaLM 模型
    'bison': 'palm',  # 通用 bison 系列模型
    'veo': 'gemini',  # Veo 视频生成模型
    'gemini-2.5': 'gemini',  # Gemini 2.5 系列
    'gemini-2.0': 'gemini',  # Gemini 2.0 系列
    'gemini-1.5': 'gemini',  # Gemini 1.5 系列
    'gemini-embedding': 'gemini',  # Gemini 嵌入模型
    
    # 阿里系列
    'qwen': 'qwen',
    'qvq': 'qwen',  # QVQ 是阿里的推理模型
    'qwq': 'qwen',  # QWQ 也是阿里的推理模型
    'qwen3': 'qwen',  # Qwen3 第三代系列
    'qwen2.5': 'qwen',  # Qwen2.5 系列
    'qwen2': 'qwen',  # Qwen2 系列
    'qvq-max': 'qwen',  # QVQ-Max 视觉推理模型
    'tongyi': 'qwen',
    'alibaba': 'alibaba',
    'alibabacloud': 'alibabacloud',
    
    # 百度系列
    'wenxin': 'wenxin',
    'baidu': 'baidu',
    'ernie': 'wenxin',
    
    # 腾讯系列
    'hunyuan': 'hunyuan',
    'tencent': 'tencent',
    
    # 字节跳动系列
    'doubao': 'doubao',
    'bytedance': 'bytedance',
    
    # DeepSeek系列
    'deepseek': 'deepseek',
    
    # 智谱系列
    'chatglm': 'chatglm',
    'glm': 'chatglm',
    'zhipu': 'zhipu',
    
    # 月之暗面系列
    'kimi': 'kimi',
    'moonshot': 'moonshot',
    
    # xAI系列
    'grok': 'grok',
    'xai': 'xai',
    
    # Meta系列
    'llama': 'meta',
    'meta': 'meta',
    
    # Mistral系列
    'mistral': 'mistral',
    
    # Cohere系列
    'cohere': 'cohere',
    
    # 其他厂商
    'yi': 'yi',
    'baichuan': 'baichuan',
    'internlm': 'internlm',
    'spark': 'spark',
    'minimax': 'minimax',
    'stepfun': 'stepfun',
    'siliconcloud': 'siliconcloud',
    'microsoft': 'microsoft',
    'azure': 'azure',
}

# 功能关键词映射 - 根据模型名称和描述推断功能标签
FUNCTION_KEYWORDS = {
    '推理思考': ['thinking', 'reasoning', 'r1', 'o1', 'qwq', 'qvq', 'reasoning', '推理', '思维', '思考', '动态思维', '长链式思维', 'enhanced', 'visual', 'math', 'mathematical', '数学', '数理', 'adaptive'],
    '文生图': ['image', 'generation', 'dall-e', 'dalle', 'midjourney', 'stable', 'flux', 'imagen', '图像生成', 'text-to-image'],
    '图生图': ['image-to-image', 'img2img', '图生图', 'image', 'vision', 'edit'],
    '语音处理': ['tts', 'speech', 'voice', '语音生成', 'omni', '自然语音', 'native-audio', 'asr', 'whisper', '语音识别'],
    '视频处理': ['video', 'generation', 'veo', '视频生成', 'video-generation'],
    '多模态': ['vision', 'multimodal', 'vl', 'omni', '视觉', '图像', '视频', '音频', '全模态'],
    '搜索检索': ['search', 'web', 'browse', 'retrieval', 'rag', '信息检索'],
    '嵌入向量': ['embedding', 'embed', 'vector'],
    '免费': ['free', 'fovt', '公益'],
}

# 厂商标签映射 - 根据匹配到的图标文件推断厂商标签
VENDOR_TAGS = {
    'openai': ['openai'],
    'claude': ['claude'],
    'anthropic': ['anthropic'],
    'gemini': ['gemini'],
    'google': ['google'],
    'palm': ['google'],  # PaLM 模型属于 Google
    'qwen': ['qwen'],
    'deepseek': ['deepseek'],
    'grok': ['grok'],
    'meta': ['meta'],
    'mistral': ['mistral'],
    'siliconcloud': ['硅基流动'],
}

# 特殊处理规则
SPECIAL_RULES = {
    # 硅基流动的特殊处理
    'siliconcloud': {
        'url_pattern': 'siliconcloud-color.png',
        'tags': ['硅基流动']
    },
    # 当贝的特殊处理
    'dangbei': {
        'tags': ['当贝']
    },
    # FOVT公益的特殊处理
    'fovt': {
        'tags': ['免费']
    },
    # Qwen3系列特殊处理
    'qwen3-235b': {
        'tags': ['推理思考']
    },
    'qwen3-30b': {
        'tags': ['多模态']
    },
    'qwen3-32b': {
        'tags': ['推理思考']
    },
    # Qwen2.5系列特殊处理
    'qwen2.5-max': {
        'tags': ['推理思考']
    },
    'qwen2.5-plus': {
        'tags': ['推理思考']
    },
    'qwen2.5-turbo': {
        'tags': ['多模态']
    },
    'qwen2.5-omni': {
        'tags': ['多模态']
    },
    'qvq-max': {
        'tags': ['推理思考', '多模态']
    },
    'qwen2.5-vl': {
        'tags': ['多模态']
    },
    'qwen2.5-14b-1m': {
        'tags': ['多模态']
    },
    'qwen2.5-coder': {
        'tags': ['推理思考']
    },
    'qwen2.5-72b': {
        'tags': ['多模态']
    },
    # Google Gemini系列特殊处理
    'gemini-2.5-pro': {
        'tags': ['推理思考', '多模态']
    },
    'gemini-2.5-flash': {
        'tags': ['推理思考']
    },
    'gemini-2.5-flash-lite': {
        'tags': ['多模态']
    },
    'gemini-2.5-flash-preview-native-audio': {
        'tags': ['语音处理']
    },
    'gemini-2.5-flash-preview-tts': {
        'tags': ['语音处理']
    },
    'gemini-2.5-pro-preview-tts': {
        'tags': ['语音处理']
    },
    'gemini-2.0-flash': {
        'tags': ['多模态']
    },
    'gemini-2.0-flash-preview-image-generation': {
        'tags': ['文生图']
    },
    'gemini-2.0-flash-lite': {
        'tags': ['多模态']
    },
    'gemini-1.5-flash': {
        'tags': ['多模态']
    },
    'gemini-1.5-flash-8b': {
        'tags': ['多模态']
    },
    'gemini-1.5-pro': {
        'tags': ['推理思考', '多模态']
    },
    'gemini-embedding': {
        'tags': ['嵌入向量']
    },
    'imagen-3.0': {
        'tags': ['文生图']
    },
    'veo-2.0': {
        'tags': ['视频处理']
    },
    'gemini-2.0-flash-live': {
        'tags': ['语音处理', '视频处理']
    }
}
