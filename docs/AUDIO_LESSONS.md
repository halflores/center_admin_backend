# 🎧 Módulo de Lecciones de Audio - Sincronización Audio-Texto

## Descripción

Este módulo permite crear lecciones de audio con sincronización de texto para estudiantes de inglés. Utilizando **Gentle** (forced aligner), genera timestamps precisos por palabra (~10-20ms) que permiten resaltar el texto en tiempo real mientras se reproduce el audio.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE PROCESAMIENTO                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. ADMIN sube audio + texto                                │
│     │                                                       │
│     ▼                                                       │
│  2. Backend envía a Gentle (Docker)                         │
│     │                                                       │
│     ▼                                                       │
│  3. Gentle genera timestamps por palabra                    │
│     │                                                       │
│     ▼                                                       │
│  4. Backend guarda en PostgreSQL                            │
│     │                                                       │
│     ▼                                                       │
│  5. App Android descarga audio + JSON                       │
│     │                                                       │
│     ▼                                                       │
│  6. Sincronización en tiempo real                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Instalación

### 1. Requisitos

- Docker (para Gentle)
- Python 3.9+
- PostgreSQL

### 2. Iniciar Gentle

```bash
# Opción A: Docker Compose (recomendado)
docker-compose -f docker-compose.gentle.yml up -d

# Opción B: Docker directo
docker run -d -p 8765:8765 --name gentle lowerquality/gentle
```

Verificar que Gentle está corriendo:
```bash
curl http://localhost:8765/
```

### 3. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 4. Ejecutar migración de base de datos

```bash
python migrations/create_audio_lessons_tables.py
```

### 5. Variables de entorno (opcional)

```env
# URL de Gentle (default: http://localhost:8765)
GENTLE_URL=http://localhost:8765

# Ruta de almacenamiento de audio (default: uploads/audio)
AUDIO_STORAGE_PATH=uploads/audio
```

## API Endpoints

### CRUD de Lecciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/audio-lessons/` | Crear lección |
| `GET` | `/api/v1/audio-lessons/` | Listar lecciones |
| `GET` | `/api/v1/audio-lessons/{id}` | Obtener lección con timestamps |
| `PUT` | `/api/v1/audio-lessons/{id}` | Actualizar lección |
| `DELETE` | `/api/v1/audio-lessons/{id}` | Eliminar lección |

### Audio

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/audio-lessons/{id}/upload-audio` | Subir archivo de audio |
| `GET` | `/api/v1/audio-lessons/{id}/stream` | Streaming del audio |
| `GET` | `/api/v1/audio-lessons/{id}/timestamps` | Solo timestamps (optimizado) |

### Procesamiento

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/audio-lessons/{id}/process` | Procesar con Gentle |
| `GET` | `/api/v1/audio-lessons/health` | Estado de Gentle |

### Progreso del Estudiante

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/audio-lessons/{id}/progress` | Actualizar progreso |
| `GET` | `/api/v1/audio-lessons/student/lessons` | Lecciones con progreso |

### Operaciones en Lote

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/audio-lessons/batch/create-with-audio` | Crear + subir + procesar |

## Ejemplos de Uso

### Crear una lección con audio

```bash
# 1. Crear lección con audio en una sola llamada
curl -X POST "http://localhost:8000/api/v1/audio-lessons/batch/create-with-audio" \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "titulo=Lesson 1: Greetings" \
  -F "transcript_text=Hello, my name is John. Nice to meet you." \
  -F "modulo_id=1" \
  -F "audio=@lesson1.mp3" \
  -F "auto_process=true"
```

### Flujo paso a paso

```bash
# 1. Crear lección (sin audio)
curl -X POST "http://localhost:8000/api/v1/audio-lessons/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Lesson 1: Greetings",
    "transcript_text": "Hello, my name is John. Nice to meet you.",
    "modulo_id": 1
  }'

# Respuesta: {"id": 1, "estado": "PENDIENTE", ...}

# 2. Subir audio
curl -X POST "http://localhost:8000/api/v1/audio-lessons/1/upload-audio" \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "audio=@lesson1.mp3"

# 3. Procesar con Gentle
curl -X POST "http://localhost:8000/api/v1/audio-lessons/1/process" \
  -H "Authorization: Bearer ${TOKEN}"

# Respuesta: {"success": true, "words_count": 9, "duration_ms": 3500, ...}

# 4. Obtener timestamps
curl "http://localhost:8000/api/v1/audio-lessons/1/timestamps" \
  -H "Authorization: Bearer ${TOKEN}"
```

## Formato de Timestamps

El JSON de timestamps tiene esta estructura:

```json
{
  "words": [
    {"word": "Hello", "start": 0, "end": 450, "confidence": 0.98},
    {"word": "my", "start": 500, "end": 700, "confidence": 0.95},
    {"word": "name", "start": 750, "end": 1100, "confidence": 0.99},
    {"word": "is", "start": 1150, "end": 1300, "confidence": 0.97},
    {"word": "John", "start": 1350, "end": 1800, "confidence": 0.99}
  ],
  "duration_ms": 3500
}
```

- `start` y `end`: milisegundos desde el inicio del audio
- `confidence`: nivel de confianza de la alineación (0-1)

## Integración con App Android

### Pseudocódigo para sincronización

```kotlin
// Kotlin/Jetpack Compose

@Composable
fun AudioLessonPlayer(lesson: AudioLesson) {
    val exoPlayer = rememberExoPlayer()
    val currentPosition by produceState(0L) {
        while (true) {
            value = exoPlayer.currentPosition
            delay(16) // 60 FPS
        }
    }
    
    // Encontrar palabra actual
    val currentWord = lesson.timestamps.words.find { word ->
        currentPosition >= word.start && currentPosition <= word.end
    }
    
    // Renderizar texto con highlight
    lesson.words.forEach { word ->
        Text(
            text = word.word + " ",
            color = if (word == currentWord) Color.Yellow else Color.White,
            fontWeight = if (word == currentWord) FontWeight.Bold else FontWeight.Normal
        )
    }
}
```

### Endpoints para la app

```kotlin
// Retrofit service
interface AudioLessonApi {
    @GET("audio-lessons/{id}")
    suspend fun getLesson(@Path("id") id: Int): AudioLessonDetail
    
    @GET("audio-lessons/{id}/stream")
    suspend fun streamAudio(@Path("id") id: Int): ResponseBody
    
    @GET("audio-lessons/{id}/timestamps")
    suspend fun getTimestamps(@Path("id") id: Int): TimestampsData
    
    @POST("audio-lessons/{id}/progress")
    suspend fun updateProgress(
        @Path("id") id: Int, 
        @Body progress: ProgressUpdate
    ): ProgressResponse
}
```

## Estructura de Archivos

```
center_admin/
├── app/
│   ├── api/v1/endpoints/
│   │   └── audio_lessons.py      # Endpoints REST
│   ├── models/
│   │   └── models.py             # AudioLesson, StudentAudioProgress
│   ├── schemas/
│   │   └── audio_lesson.py       # Schemas Pydantic
│   └── services/
│       ├── audio_lesson_service.py    # Lógica de negocio
│       ├── gentle_service.py          # Integración con Gentle
│       └── audio_storage_service.py   # Almacenamiento de archivos
├── migrations/
│   └── create_audio_lessons_tables.py
├── uploads/
│   └── audio/
│       └── lessons/              # Archivos de audio
├── docker-compose.gentle.yml     # Docker para Gentle
└── requirements.txt              # Dependencias
```

## Troubleshooting

### Gentle no responde

```bash
# Verificar estado
docker ps | grep gentle
docker logs gentle_aligner

# Reiniciar
docker-compose -f docker-compose.gentle.yml restart
```

### Error de memoria en Gentle

Gentle requiere ~2-4GB de RAM. Ajustar en `docker-compose.gentle.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 6G
```

### Audio no se procesa

1. Verificar formato de audio (MP3, WAV soportados)
2. Verificar que el texto coincide con el audio
3. Revisar logs: `docker logs gentle_aligner`

## Roadmap

- [ ] Soporte para múltiples idiomas (español, etc.)
- [ ] Preview de audio en admin panel
- [ ] Batch processing de múltiples lecciones
- [ ] Integración con TTS (ElevenLabs, OpenAI) para generar audio desde texto
- [ ] Cache de timestamps en Redis
- [ ] CDN para streaming de audio
