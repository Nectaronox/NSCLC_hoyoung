# backend/services/prompt_manager.py
import yaml
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PromptManager:
    def __init__(self, yaml_path: str = None):
        if yaml_path is None:
            # 현재 파일 위치를 기준으로 prompt.yaml 경로 설정
            current_dir = os.path.dirname(__file__)
            yaml_path = os.path.join(current_dir, '..', 'prompt.yaml')
        
        self.yaml_path = yaml_path
        self.config = self._load_yaml()
    
    def _load_yaml(self) -> Dict[str, Any]:
        """YAML 파일 로드"""
        try:
            with open(self.yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Prompt configuration loaded from {self.yaml_path}")
            return config
            
        except FileNotFoundError:
            logger.error(f"Prompt YAML file not found: {self.yaml_path}")
            return self._get_fallback_config()
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return self._get_fallback_config()
        except Exception as e:
            logger.error(f"Failed to load prompt config: {e}")
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """YAML 로드 실패시 기본 설정"""
        return {
            'system_prompt': 'You are a thoracic radiologist specializing in NSCLC staging.',
            'analysis_prompt': 'Please analyze this CT scan for NSCLC staging.',
            'staging_guidelines': {},
            'analysis_instructions': [],
            'quality_indicators': [],
            'output_format': []
        }
    
    def get_system_prompt(self) -> str:
        return self.config.get('system_prompt', '')
    
    def get_analysis_prompt(self) -> str:
        """분석 프롬프트 반환"""
        return self.config.get('analysis_prompt', '')
    
    def get_staging_guidelines(self) -> Dict[str, Any]:
        """병기 분류 가이드라인 반환"""
        return self.config.get('staging_guidelines', {})
    
    def get_analysis_instructions(self) -> List[str]:
        """분석 지침 반환"""
        return self.config.get('analysis_instructions', [])
    
    def get_quality_indicators(self) -> List[str]:
        """품질 지표 반환"""
        return self.config.get('quality_indicators', [])
    
    def get_output_format(self) -> List[str]:
        """출력 형식 지침 반환"""
        return self.config.get('output_format', [])
    
    def build_enhanced_system_prompt(self) -> str:
        """YAML의 모든 정보를 통합한 향상된 시스템 프롬프트 생성"""
        base_prompt = self.get_system_prompt()
        
        # 병기 분류 가이드라인 추가
        guidelines = self.get_staging_guidelines()
        if guidelines:
            base_prompt += "\n\n## TNM Staging Guidelines:\n"
            
            for stage_type, stages in guidelines.items():
                base_prompt += f"\n### {stage_type.upper().replace('_', ' ')}:\n"
                for stage, description in stages.items():
                    base_prompt += f"- {stage}: {description}\n"
        
        # 분석 지침 추가
        instructions = self.get_analysis_instructions()
        if instructions:
            base_prompt += "\n\n## Analysis Instructions:\n"
            for i, instruction in enumerate(instructions, 1):
                base_prompt += f"{i}. {instruction}\n"
        
        # 품질 지표 추가
        quality_indicators = self.get_quality_indicators()
        if quality_indicators:
            base_prompt += "\n\n## Quality Indicators:\n"
            for indicator in quality_indicators:
                base_prompt += f"- {indicator}\n"
        
        # 출력 형식 추가
        output_format = self.get_output_format()
        if output_format:
            base_prompt += "\n\n## Output Format:\n"
            for format_rule in output_format:
                base_prompt += f"- {format_rule}\n"
        
        return base_prompt
    
    def reload_config(self):
        """설정 다시 로드 (런타임에 YAML 변경사항 반영)"""
        self.config = self._load_yaml()
        logger.info("Prompt configuration reloaded")