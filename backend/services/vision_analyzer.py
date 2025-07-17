import json
import logging
import os
from typing import Dict, Any, Optional
from openai import OpenAI
import asyncio

from ..models import StagingResult, ConfidenceScores
from .prompt_manager import PromptManager

logger = logging.getLogger(__name__)

class VisionAnalyzer:
    def __init__(self):
        self.client = None
        self.model_name = "gpt-4o"
        self.temperature = 0.2
        self.max_tokens = 300
        
        self.prompt_manager = PromptManager()
        
    async def initialize(self):
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise
    
    async def analyze_ct_scan(self, base64_image: str) -> StagingResult:
        """
        Analyze a CT scan image and return NSCLC staging results.
        
        Args:
            base64_image: Base64 encoded image string
            
        Returns:
            StagingResult with TNM staging and confidence scores
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        try:

            function_schema = {
                "name": "analyze_nsclc_staging",
                "description": "Analyze CT scan for NSCLC staging according to AJCC 8th edition",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "t_stage": {
                            "type": "string",
                            "enum": ["T0", "T1", "T1a", "T1b", "T1c", "T2", "T2a", "T2b", "T3", "T4"],
                            "description": "T stage based on primary tumor characteristics"
                        },
                        "n_stage": {
                            "type": "string",
                            "enum": ["N0", "N1", "N2", "N3"],
                            "description": "N stage based on regional lymph node involvement"
                        },
                        "m_stage": {
                            "type": "string",
                            "enum": ["M0", "M1a", "M1b", "M1c"],
                            "description": "M stage based on distant metastases"
                        },
                        "overall_stage": {
                            "type": "string",
                            "enum": ["IA1", "IA2", "IA3", "IB", "IIA", "IIB", "IIIA", "IIIB", "IIIC", "IVA", "IVB", "I", "II", "III", "IV"],
                            "description": "Overall stage based on TNM combination"
                        },
                        "confidence_scores": {
                            "type": "object",
                            "properties": {
                                "t_confidence": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                    "description": "Confidence score for T stage assessment"
                                },
                                "n_confidence": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                    "description": "Confidence score for N stage assessment"
                                },
                                "m_confidence": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                    "description": "Confidence score for M stage assessment"
                                },
                                "overall_confidence": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                    "description": "Confidence score for overall stage assessment"
                                }
                            },
                            "required": ["t_confidence", "n_confidence", "m_confidence", "overall_confidence"]
                        },
                        "error": {
                            "type": "string",
                            "description": "Error message if image is non-diagnostic or analysis fails"
                        }
                    },
                    "required": ["confidence_scores"]
                }
            }
            
            # Prepare the messages using YAML prompts
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": self._get_analysis_prompt()
                        }
                    ]
                }
            ]
            
            # Make the API call
            logger.info("Sending CT scan to OpenAI for analysis...")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                tools=[{"type": "function", "function": function_schema}],
                tool_choice={"type": "function", "function": {"name": "analyze_nsclc_staging"}}
            )
            
            if response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                result_data = json.loads(tool_call.function.arguments)
                

                staging_result = self._parse_analysis_result(result_data)
                
                logger.info(f"Analysis completed successfully: T{staging_result.t}, N{staging_result.n}, M{staging_result.m}, Stage {staging_result.stage}")
                return staging_result
            else:
                logger.error("No tool calls in response")
                return StagingResult(
                    t=None,
                    n=None,
                    m=None,
                    stage=None,
                    confidences=ConfidenceScores(t=0.0, n=0.0, m=0.0, stage=0.0),
                    error="No analysis result received from model"
                )
                
        except Exception as e:
            logger.error(f"Error during CT scan analysis: {str(e)}")
            return StagingResult(
                t=None,
                n=None,
                m=None,
                stage=None,
                confidences=ConfidenceScores(t=0.0, n=0.0, m=0.0, stage=0.0),
                error=f"Analysis failed: {str(e)}"
            )
    
    def _get_system_prompt(self) -> str:
        return self.prompt_manager.build_enhanced_system_prompt()
    
    def _get_analysis_prompt(self) -> str:
        return self.prompt_manager.get_analysis_prompt()
    
    def _parse_analysis_result(self, result_data: Dict[str, Any]) -> StagingResult:
        logger.info(f"Parsing analysis result data: {json.dumps(result_data, indent=2)}")
        try:
            # If the model returns an error, prioritize it.
            if error_msg := result_data.get('error'):
                logger.warning(f"Analysis returned an error: {error_msg}")
                return StagingResult(
                    t=None, n=None, m=None, stage=None,
                    confidences=ConfidenceScores(t=0.0, n=0.0, m=0.0, stage=0.0),
                    error=error_msg
                )

            confidences = result_data.get('confidence_scores', {})
            
            confidence_scores = ConfidenceScores(
                t=confidences.get('t_confidence', 0.0),
                n=confidences.get('n_confidence', 0.0),
                m=confidences.get('m_confidence', 0.0),
                stage=confidences.get('overall_confidence', 0.0)
            )
            
            return StagingResult(
                t=result_data.get('t_stage'),
                n=result_data.get('n_stage'),
                m=result_data.get('m_stage'),
                stage=result_data.get('overall_stage'),
                confidences=confidence_scores,
                error=result_data.get('error')
            )
            
        except Exception as e:
            logger.error(f"Error parsing analysis result: {str(e)}")
            return StagingResult(
                t=None,
                n=None,
                m=None,
                stage=None,
                confidences=ConfidenceScores(t=0.0, n=0.0, m=0.0, stage=0.0),
                error=f"Failed to parse analysis result: {str(e)}"
            )
    
    def reload_prompts(self):
        """런타임에 프롬프트 다시 로드"""
        self.prompt_manager.reload_config()
        logger.info("Prompts reloaded from YAML") 