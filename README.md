# Voice Cloning API

FastAPI backend service for voice cloning and speech synthesis.

## Features

- **Upload Voice Samples**: Register voices by uploading audio files
- **Synthesize Speech**: Generate speech in cloned voices from text
- **Voice Metadata**: Retrieve information about registered voices
- **Health Check**: Service status endpoint

## Setup

### Prerequisites

- Python 3.8+
- pip or poetry

### Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Server

### Option 1: Direct Python

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Option 2: Docker

```bash
# Build the Docker image
docker build -t voice-cloner-api .

# Run the container
docker run -d \
  --name voice-cloner-backend \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/embeddings:/app/embeddings \
  voice-cloner-api
```

### Option 3: Docker Compose

```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI): `http://localhost:8000/docs`
Alternative docs (ReDoc): `http://localhost:8000/redoc`

## API Endpoints

### Authentication Endpoints

See [Authentication](#authentication) section above for details.

### 1. Health Check

**GET** `/health`

Returns service status.

**Response:**
```json
{
  "status": "ok",
  "service": "voice-clone-api"
}
```

### 2. Upload Voice Sample

**POST** `/voices`

Upload an audio file to register a voice for cloning.

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `file` (required): Audio file (wav, mp3, m4a, ogg, webm, flac)
  - `name` (optional): Name for the voice
  - `description` (optional): Description

**Response (201):**
```json
{
  "voice_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "sample.wav",
  "duration": 3.5,
  "sample_rate": 22050,
  "message": "Voice registered successfully"
}
```

**Error Responses:**
- `400`: Missing file or invalid content type
- `500`: Internal error computing embedding or saving file

### 3. Synthesize Cloned Voice

**POST** `/voices/{voice_id}/synthesize`

Generate speech from text using a cloned voice.

**Request:**
- Content-Type: `application/json`
- Body:
```json
{
  "text": "Hello, this is a test",
  "format": "wav",
  "sample_rate": 22050
}
```

**Response (200):**
- Content-Type: `audio/wav` or `audio/mpeg`
- Body: Raw audio bytes

**Error Responses:**
- `404`: Voice ID not found
- `400`: Empty text or invalid format
- `500`: Synthesis failure

### 4. Get Voice Metadata

**GET** `/voices/{voice_id}`

Get metadata for a registered voice.

**Response (200):**
```json
{
  "voice_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "sample.wav",
  "created_at": "2024-01-15T10:30:00Z",
  "duration": 3.5,
  "sample_rate": 22050,
  "name": "My Voice",
  "description": "Sample voice"
}
```

**Error Responses:**
- `404`: Voice not found

## Implementation Notes

### Voice Engine Integration

The API includes stub functions in `engine.py` that need to be implemented with your actual voice cloning model:

1. **`compute_speaker_embedding(audio_path)`**: Extract speaker embedding from audio
   - Example libraries: Coqui TTS, YourTTS, Resemblyzer
   - Should return: (embedding, duration, sample_rate)

2. **`synthesize_speech(embedding, text, sample_rate, format)`**: Generate speech
   - Example libraries: Coqui TTS, YourTTS
   - Should return: audio bytes

### Storage

Currently uses in-memory storage (`storage.py`). For production:

- Replace with a database (PostgreSQL, MongoDB, etc.)
- Store embeddings efficiently (e.g., as numpy arrays or in a vector database)
- Implement proper file management and cleanup

### Authentication

The API supports Firebase Authentication for React Native apps. Users authenticate with Firebase in the mobile app, and the backend verifies Firebase ID tokens.

#### Setup Firebase Authentication

1. **Get Firebase Service Account Key:**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Select your project
   - Go to Project Settings → Service Accounts
   - Click "Generate New Private Key"
   - Save the JSON file (e.g., `serviceAccountKey.json`)

2. **Configure Environment Variables:**

   **Option 1: Use Service Account Key File (Development)**
   ```bash
   export FIREBASE_CREDENTIALS_PATH="./serviceAccountKey.json"
   ```

   **Option 2: Use Environment Variables (Production)**
   ```bash
   export FIREBASE_PROJECT_ID="your-project-id"
   export FIREBASE_PRIVATE_KEY_ID="your-private-key-id"
   export FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   export FIREBASE_CLIENT_EMAIL="your-service-account@your-project.iam.gserviceaccount.com"
   export FIREBASE_CLIENT_ID="your-client-id"
   ```

3. **Set JWT Secret Key:**
   ```bash
   export SECRET_KEY="your-super-secret-key-change-this-in-production"
   ```

#### Authentication Endpoints

**POST** `/api/auth/google/token`

Authenticate with Firebase ID token. This endpoint accepts Firebase ID tokens from your React Native app.

**Request:**
```json
{
  "code": "firebase_id_token",
  "firebase_token": true
}
```

**Response:**
```json
{
  "access_token": "jwt_access_token",
  "token_type": "bearer",
  "user": {
    "id": "user_uid",
    "email": "user@example.com",
    "name": "User Name",
    "picture": "https://...",
    "provider": "google",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**GET** `/api/auth/me`

Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "user_uid",
  "email": "user@example.com",
  "name": "User Name",
  "picture": "https://...",
  "provider": "google",
  "created_at": "2024-01-01T00:00:00"
}
```

#### Protecting Routes

Use the `get_current_user` dependency to protect routes:

```python
from app.api.dependencies import get_current_user
from app.models.storage import UserRecord

@app.get("/protected")
async def protected_route(user: UserRecord = Depends(get_current_user)):
    return {"message": f"Hello {user.email}"}
```

### Security & Ethics

- ✅ Authentication/authorization with Firebase and JWT
- Implement rate limiting
- Add consent validation for voice cloning
- Consider abuse detection (impersonation, etc.)
- Validate file sizes and durations

### Environment Variables

```bash
# Authentication
export SECRET_KEY="your-super-secret-key-change-this-in-production"
export FIREBASE_CREDENTIALS_PATH="./serviceAccountKey.json"  # Or use env vars below
# export FIREBASE_PROJECT_ID="your-project-id"
# export FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
# export FIREBASE_CLIENT_EMAIL="your-service-account@your-project.iam.gserviceaccount.com"

# Optional: Customize upload and embedding directories
export UPLOAD_DIR="./uploads"
export EMBEDDING_DIR="./embeddings"
```

## Example Usage

### Upload a voice sample

```bash
curl -X POST "http://localhost:8000/voices" \
  -F "file=@sample.wav" \
  -F "name=My Voice" \
  -F "description=Test voice"
```

### Synthesize speech

```bash
curl -X POST "http://localhost:8000/voices/{voice_id}/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "format": "wav"}' \
  --output output.wav
```

### Get voice metadata

```bash
curl "http://localhost:8000/voices/{voice_id}"
```

## Project Structure

```
voice-cloner-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Application settings
│   │   └── exceptions.py    # Custom exceptions
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py  # API dependencies
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py    # Health check routes
│   │       └── voices.py    # Voice-related routes
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py       # Pydantic models for validation
│   │   └── storage.py       # Storage layer (replace with DB)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── engine.py        # Voice engine interface (implement stubs)
│   │   └── voice_service.py # Business logic layer
│   └── utils/
│       ├── __init__.py
│       └── file_utils.py    # File utility functions
├── requirements.txt         # Python dependencies
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
└── README.md               # This file
```

### Architecture

The project follows a clean architecture pattern:

- **`app/core/`**: Core configuration and custom exceptions
- **`app/api/`**: API routes and dependencies (presentation layer)
- **`app/models/`**: Data models, schemas, and storage (data layer)
- **`app/services/`**: Business logic and voice engine (service layer)
- **`app/utils/`**: Utility functions

This structure provides:
- Clear separation of concerns
- Easy testing and maintenance
- Scalability for future features
- Dependency injection support

## Development

### Code Style

- Type hints throughout
- Pydantic models for validation
- Async/await for I/O operations
- Clear error handling

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (create tests/ directory)
pytest
```

## License

[Your License Here]

