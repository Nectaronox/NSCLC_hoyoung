import os
import tempfile
import logging
from typing import Optional, Tuple, Union
import numpy as np
from PIL import Image
import cv2
import pydicom
from pydicom.errors import InvalidDicomError
from pydicom import multival
from io import BytesIO
import base64
import sys

from ..models import ImageMetadata

logger = logging.getLogger(__name__)

# DICOM 파일 읽는 것(이외에도 png, jpg, jpeg 파일 지원함)
'''
DCM 파일과 일반 이미지 파일은 여러 차이가 있음.
CT 데이터를 통해 찍은 사진은 -1000dptj +3000의 HU(CT 영상에서 조직의 방사선 흡수/감쇠 계수를 정량적으로 나타내는 단위) 값을 지님
하지만 모니터는 0~255의 그레이스케일(회색조-> 각 화소의 값이 빛의 양을 나타내는 하나의 샘플인 이미지)

그래서 window를 다르게 하면 모니터에서 잘 보이는 조직이 달라짐
폐 window -> center = -600, width = 1500으로 하면 폐 조직이 잘 보이고,
각 다른 window를 설정하면 다들 잘 보일 수 있게 됨. 

'''
class ImageProcessor:
    
    def __init__(self):
        self.supported_formats = ['.dcm', '.png', '.jpg', '.jpeg']
        self.target_size = (512, 512)

    async def read_and_normalize(self, file_path: str) -> str:

        try:
            # 한 번만 DICOM 여부 확인
            is_dicom = self._is_dicom_file(file_path)
            
            if is_dicom:
                image_array = self._read_dicom(file_path)
            else:
                image_array = self._read_standard_image(file_path)
            
            # 이거는 이미지 정규화 작업임
            normalized_image = self._normalize_ct_image(image_array)
            pil_image = Image.fromarray(normalized_image)
            
            # 이미지 크기 조정 작업임
            if pil_image.size != self.target_size:
                pil_image = pil_image.resize(self.target_size, Image.Resampling.LANCZOS)
            
            # base64로 변환
            base64_image = self._pil_to_base64(pil_image)
            
            logger.info(f"Successfully processed image: {file_path}")
            return base64_image
            
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {str(e)}")
            raise
    
    def _is_dicom_file(self, file_path: str) -> bool:
        """더 효율적인 DICOM 검사"""
        # 1. 먼저 확장자로 빠른 체크
        _, ext = os.path.splitext(file_path.lower())
        if ext == '.dcm':
            return True
        
        # 2. 확장자가 .dcm이 아니면 헤더 검사
        try:
            pydicom.dcmread(file_path, stop_before_pixels=True)
            return True
        except (InvalidDicomError, Exception):
            return False
    
    def _read_dicom(self, file_path: str) -> np.ndarray:
        #DCM 확장자로 끝나는 파일을 읽는 작업임
        try:
            ds = pydicom.dcmread(file_path)

            pixel_array = ds.pixel_array
            
            # hasattr -> ds에 PhotometricInterpretation 속성이 있는지 확인하는 작업임
            if hasattr(ds, 'PhotometricInterpretation'):
                if ds.PhotometricInterpretation == 'MONOCHROME1':
                    # 이거는 MONOCHROME1 형식인 경우 이미지를 반전하는 작업임
                    pixel_array = np.max(pixel_array) - pixel_array
            
            
            # 이거는 이미지 윈도우 설정 작업임
            if hasattr(ds, 'WindowCenter') and hasattr(ds, 'WindowWidth'):
                window_center = ds.WindowCenter
                window_width = ds.WindowWidth

                if isinstance(window_center, (list, multival.MultiValue)):
                    window_center = window_center[0]
                if isinstance(window_width, (list, multival.MultiValue)):
                    window_width = window_width[0]
                
                pixel_array = self._apply_window_level(pixel_array, window_center, window_width)
            
            logger.info(f"DICOM image loaded: {pixel_array.shape}, dtype: {pixel_array.dtype}")
            return pixel_array
            
        except Exception as e:
            logger.error(f"Error reading DICOM file {file_path}: {str(e)}")
            raise
    
    def _read_standard_image(self, file_path: str) -> np.ndarray:
        #PNG, JPG, JPEG 확장자로 끝나는 파일을 읽는 작업임
        #근디 솔직히 없을 것 같긴 한데...
        try:
            # PIL을 사용하여 이미지를 읽음
            image = Image.open(file_path)
            
            # 이미지 모드를 확인하고 그레이스케일로 변환
            if image.mode != 'L':
                image = image.convert('L')
            
            # numpy array로 변환
            image_array = np.array(image)
            
            logger.info(f"Standard image loaded: {image_array.shape}, dtype: {image_array.dtype}")
            return image_array
            
        except Exception as e:
            logger.error(f"Error reading standard image {file_path}: {str(e)}")
            raise
    
    def _apply_window_level(self, image: np.ndarray, window_center: float, window_width: float) -> np.ndarray:
        
        min_val = window_center - window_width / 2
        max_val = window_center + window_width / 2
        
        windowed = np.clip(image, min_val, max_val)
        windowed = ((windowed - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        
        return windowed
    
    def _normalize_ct_image(self, image: np.ndarray) -> np.ndarray:
        """
        CT 이미지 정규화를 하는 이유 -> GPT 모델은 일반 이미지에만 훈련되었기 때문에 
        CT 이미지를 정규화하여 일반 이미지로 표현할 필요가 있음.
        """

        if len(image.shape) > 2:
            image = image[:, :, 0] if image.shape[2] > 1 else image.squeeze()
        image = image.astype(np.float32)
        
        # 0-255 범위로 정규화
        if image.max() > image.min():
            image = (image - image.min()) / (image.max() - image.min()) * 255
        else:
            image = np.zeros_like(image)
        
        # openCV의 모듈을 통해 정보 손실 최소화하면서 압축축
        image_uint8 = image.astype(np.uint8)
        equalized = cv2.equalizeHist(image_uint8)
        
        # 노이즈 감소를 위해 가우시안 블러 적용
        blurred = cv2.GaussianBlur(equalized, (3, 3), 0)
        
        return blurred
    
    def _pil_to_base64(self, image: Image.Image) -> str:
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        
        return f"data:image/png;base64,{base64_string}"
    
    def get_image_metadata(self, file_path: str) -> dict:
        try:
            is_dicom = self._is_dicom_file(file_path)

            metadata = {
                'filename': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'is_dicom': is_dicom
            }
            
            if metadata['is_dicom']:
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                metadata.update({
                    'modality': getattr(ds, 'Modality', 'Unknown'),
                    'study_date': getattr(ds, 'StudyDate', 'Unknown'),
                    'patient_id': getattr(ds, 'PatientID', 'Unknown'),
                    'study_description': getattr(ds, 'StudyDescription', 'Unknown')
                })
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {str(e)}")
            return {'error': str(e)} 