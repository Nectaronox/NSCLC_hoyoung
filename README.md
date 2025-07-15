# NSCLC Staging Assistant

AI-powered non-small-cell lung cancer staging from chest CT images using OpenAI's vision model.

## ⚠️ Important Disclaimer

**This tool is for research purposes only and is not FDA-cleared for clinical diagnosis.** All results should be reviewed by qualified healthcare professionals. This software is not intended for diagnostic use in clinical practice.

## Features

- **Modern Web Interface**: Clean, accessible, hospital-grade UI built with React 18 and TailwindCSS
- **Drag & Drop Upload**: Support for DICOM (.dcm), PNG, and JPEG formats
- **AI-Powered Analysis**: OpenAI GPT-4 Vision model for NSCLC staging according to AJCC 8th edition
- **TNM Staging**: Comprehensive T-stage, N-stage, M-stage, and overall staging (I-IV)
- **Confidence Scores**: AI confidence levels for each staging assessment
- **Security Ready**: JWT authentication stub for hospital SSO integration
- **HIPAA Compliant**: Temporary file processing with automatic cleanup
- **Production Ready**: Structured logging, error handling, and Docker support

## Architecture

```
frontend/          # React 18 + Vite + TypeScript + TailwindCSS
├── src/
│   ├── components/    # UI components
│   ├── services/      # API integration
│   └── types.ts       # TypeScript definitions
backend/           # FastAPI + Python 3.11
├── services/          # Core business logic
├── utils/            # Utilities and logging
└── models.py         # Pydantic models
```

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- OpenAI API key with GPT-4 Vision access

### 1. Environment Setup

Create environment files:

**Backend (.env):**
```bash
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
LOG_LEVEL=INFO
```

**Frontend (.env):**
```bash
VITE_API_URL=http://localhost:8000
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The API will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The web interface will be available at `http://localhost:3000`

## Docker Compose (Recommended)

```bash
# Create docker-compose.yml in project root
docker-compose up -d
```

## API Endpoints

### Authentication
- `POST /auth/login` - User login (stub implementation)
- `GET /auth/me` - Get current user info

### Analysis
- `POST /analyze` - Upload and analyze CT image
- `GET /health` - Health check

### Example API Usage

```bash
# Login (stub - use admin/password)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Analyze CT image
curl -X POST http://localhost:8000/analyze \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@chest_ct.dcm"
```

## NSCLC Staging Reference

This tool implements staging according to the **AJCC Cancer Staging Manual, 8th Edition**:

### T Stage (Primary Tumor)
- **T1**: Tumor ≤3cm, no pleural invasion
  - T1a: ≤1cm, T1b: >1-2cm, T1c: >2-3cm
- **T2**: Tumor >3-5cm OR involves visceral pleura
  - T2a: >3-4cm, T2b: >4-5cm
- **T3**: Tumor >5-7cm OR separate nodule in same lobe
- **T4**: Tumor >7cm OR invasion of chest wall, diaphragm, mediastinum

### N Stage (Regional Lymph Nodes)
- **N0**: No regional lymph node metastasis
- **N1**: Ipsilateral hilar/peribronchial lymph nodes
- **N2**: Ipsilateral mediastinal/subcarinal lymph nodes
- **N3**: Contralateral mediastinal/hilar OR supraclavicular lymph nodes

### M Stage (Distant Metastases)
- **M0**: No distant metastases
- **M1a**: Separate nodule in contralateral lung OR pleural effusion
- **M1b**: Single distant metastasis
- **M1c**: Multiple distant metastases

## Security & Compliance

### PHI Protection
- **No PHI Storage**: All uploaded files are processed in temporary storage and immediately deleted
- **Memory Cleanup**: In-memory processing with automatic cleanup
- **Secure Transmission**: HTTPS recommended for production

### Authentication
- JWT-based authentication with hospital SSO integration stub
- Role-based access control ready for implementation
- Token expiration and refresh capabilities

### CORS Configuration
- Configured for frontend origin only
- Customizable for production environments

## Production Deployment

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key
JWT_SECRET_KEY=secure_secret_key

# Optional
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./backend/logs:/app/logs

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
```

### Health Monitoring
- Health check endpoint: `GET /health`
- Structured logging with rotation
- Error tracking and monitoring ready

## Development

### Frontend Development
```bash
cd frontend
npm run dev    # Development server
npm run build  # Production build
npm run lint   # Code linting
```

### Backend Development
```bash
cd backend
python main.py          # Development server
python -m pytest       # Run tests (when added)
```

### Code Quality
- TypeScript for type safety
- ESLint for code quality
- Pydantic for data validation
- Comprehensive error handling

## Hospital Integration

This starter code is designed for easy integration with hospital systems:

1. **SSO Integration**: Replace JWT stub with hospital SSO system
2. **PACS Integration**: Extend DICOM processing for PACS connectivity
3. **EHR Integration**: Add APIs for electronic health record systems
4. **Audit Logging**: Comprehensive logging for compliance requirements

## License

This project is for research and educational purposes only. Not for clinical use.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For technical support or questions:
- Review the code documentation
- Check the API documentation at `http://localhost:8000/docs`
- Ensure all environment variables are correctly set

---

**Remember**: This tool is for research purposes only. Always consult with qualified healthcare professionals for patient care decisions. 