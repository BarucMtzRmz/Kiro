# Kiro

*[Read in English](README.md)*

Una app de RAG (Generación Aumentada por Recuperación) local que lee
documentos de tu propio dispositivo y responde preguntas sobre ellos en una
interfaz de chat.

- **Tus documentos se quedan en tu equipo.** Los archivos que indexas viven
  en disco, en `data/documents/`, y se convierten en un índice vectorial
  local en `data/index/` (Chroma, basado en archivos, sin base de datos
  externa).
- **Los embeddings corren localmente.** Usa `sentence-transformers`
  (`all-MiniLM-L6-v2` por default), que se descarga una sola vez y se guarda
  en caché en tu máquina.
- **El LLM es configurable.** Por default usa [Ollama](https://ollama.com),
  así que todo el flujo —recuperación y generación— puede correr
  completamente offline. También puedes apuntarlo a cualquier API compatible
  con OpenAI (OpenAI mismo, LM Studio, vLLM, etc.) configurando un par de
  variables de entorno.

Tipos de documento soportados: `.txt`, `.md`, `.pdf`, `.docx`.

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # luego edítalo si quieres cambiar los valores por default
```

### Backend de LLM

**Opción A — Ollama (100% local, default):**

```bash
# instala Ollama desde https://ollama.com y luego:
ollama serve &
ollama pull llama3.2
```

No necesitas configurar nada más — `.env.example` ya apunta a
`http://localhost:11434` con el modelo `llama3.2`.

**Opción B — API compatible con OpenAI:**

```env
KIRO_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1   # o la URL de tu servidor local
OPENAI_MODEL=gpt-4o-mini
```

## Uso

### Línea de comandos

```bash
# Indexa un archivo o una carpeta completa (recorre subcarpetas)
python -m kiro ingest ~/Documents/notes
python -m kiro ingest ~/Documents/report.pdf

# Haz una pregunta rápida
python -m kiro ask "¿Qué dijo el reporte del Q3 sobre los ingresos?"

# Chat interactivo
python -m kiro chat

# Borra el índice y empieza de cero
python -m kiro reset
```

### Interfaz web

```bash
streamlit run app.py
```

Sube archivos o indica la ruta de una carpeta local desde la barra lateral,
y luego chatea con tus documentos en el panel principal.

## Cómo funciona

1. **Carga** — los `.txt`/`.md` se leen directamente, los `.pdf` con
   `pypdf`, y los `.docx` con `python-docx`.
2. **Fragmentación (chunking)** — los documentos se dividen en fragmentos de
   ~1000 caracteres con traslape (overlap), respetando los saltos de párrafo
   (`kiro/chunking.py`), para que la recuperación regrese pasajes
   puntuales en lugar de archivos completos.
3. **Embeddings + indexación** — cada fragmento se convierte en un vector
   con un modelo local de `sentence-transformers` y se guarda en una
   colección persistente de Chroma en disco.
4. **Recuperación** — la pregunta se convierte en vector de la misma forma
   y se compara contra el índice (similitud coseno) para traer los
   fragmentos más relevantes.
5. **Generación** — la pregunta junto con los fragmentos recuperados se
   envían al LLM configurado, con un prompt que le indica responder
   únicamente con base en ese contexto y decir cuando no sepa la respuesta.

## Configuración

Todos los ajustes son variables de entorno (ver `.env.example`), incluyendo
dónde se guardan los documentos e índice, el tamaño y traslape de los
fragmentos, cuántos fragmentos recuperar por pregunta (`KIRO_TOP_K`), y qué
modelo de embeddings usar.

## Desarrollo

```bash
pip install pytest
pytest
```

Las pruebas cubren la lógica de fragmentación y de carga de documentos
(puras, sin necesidad de red ni de descargar modelos). Indexar documentos
reales sí requiere descargar el modelo de embeddings la primera vez y,
para el chat, tener disponible un backend de LLM (Ollama o una API
compatible con OpenAI).
