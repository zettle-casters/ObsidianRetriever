# Obsidian Retriever

Локальный движок для поиска и навигации по Obsidian-vault’у.

Под капотом:
- **Neo4j** — граф заметок и чанков (Note → Chunk, ссылки между ними)
- **Qdrant** — векторный поиск по чанкам и заметкам
- **Obsidian-парсер** — нарезает `.md` на чанки и вытаскивает `[[wiki-ссылки]]`

Основная точка входа — класс **`KnowledgeBaseManager`**.

---

## Требования

Перед использованием убедитесь, что:

- запущен **Neo4j** (Bolt-доступ, логин/пароль известны)
- запущен **Qdrant** (доступен HTTP/gRPC API)
```bash
docker compose up -d
```

- установлены Python-зависимости проекта (см. `requirements.txt`)
```
pip install -r requirements.txt
```
---

## Инициализация менеджера

```python
from retriever.manager import KnowledgeBaseManager

manager = KnowledgeBaseManager(
    db_url="bolt://neo4j:password@localhost:7687",  # Neo4j
    host="localhost",                               # Qdrant host
    port=6333,                                      # Qdrant port
    prefer_grpc=False,
    model_name="sentence-transformers/all-MiniLM-L6-v2",  # или другая модель
)
```

Параметры:
- `db_url` — строка подключения к Neo4j (формат `bolt://user:pass@host:port`)
- `host`, `port` — адрес Qdrant
- `prefer_grpc` — использовать ли gRPC клиент
- `model_name` — имя модели эмбеддингов (HuggingFace / sentence-transformers)

---

## Импорт Obsidian Vault

Vault заранее запаковывается в `.zip`.

```python
manager.init_vault_from_zip(
    zip_path="path/to/vault.zip",
    include_paths=[],                                # опционально: какие подпапки включать
    exclude_paths=["/Attachments", "/Templates"],    # опционально: что исключить
)
```

Что делает этот метод:
- распаковывает vault
- парсит все `.md`-файлы
- режет текст на чанки
- создаёт граф `Note → Chunk` в Neo4j
- индексирует чанки и заметки в Qdrant
- восстанавливает wiki-ссылки:
  - между заметками (Note → Note)
  - между чанками (Chunk → Chunk) для `[[Note#Heading]]`

---

## Поиск

### Поиск по чанкам

```python
results = manager.search_chunks("как работает docker", top_k=5)

for chunk, score in results:
    print(f"{chunk.note_id}  score={score:.3f}")
    print(chunk.text)
    print("-" * 80)
```

Возвращается список `(ChunkRecord, score)`.

### Поиск по заметкам

```python
results = manager.search_notes("vector database", top_k=5)

for note, score in results:
    print(f"{note.title} ({note.path})  score={score:.3f}")
```

---

## Получение данных

### Получить заметку

```python
note = manager.get_note("Folder/Note.md")
print(note.title, note.path)
```

### Получить чанк

```python
chunk = manager.get_chunks("Folder/Note.md#chunk-0")
print(chunk.text)
```

---

## Соседние ноды в графе

### Соседи заметки (wiki-ссылки между файлами)

```python
outgoing, incoming = manager.get_note_neighbors("Folder/Note.md")

print("Outgoing:")
for link in outgoing:
    print(f"{link.from_note_id} -> {link.to_note_id} ({link.link_type})")

print("Incoming:")
for link in incoming:
    print(f"{link.from_note_id} -> {link.to_note_id} ({link.link_type})")
```

### Соседи чанка (ссылки на уровне фрагментов)

```python
out_chunks, in_chunks = manager.get_chunk_neighbors("Folder/Note.md#chunk-0")

for link in out_chunks:
    print(f"{link.from_chunk_id} -> {link.to_chunk_id} ({link.link_type})")
```

---

## Ручные операции

### Линки между заметками

```python
manager.connect_notes("A/Note.md", "B/Note.md", link_type="wiki")
# или перезаписать сразу весь список:
manager.set_note_links("A/Note.md", ["B/Note.md", "C/Note.md"])
```

### Линки между чанками

```python
manager.connect_chunks(
    "A/Note.md#chunk-0",
    "B/Note.md#chunk-3",
    link_type="reference",
)
```

---

## Кратко о внутреннем устройстве

- Neo4j хранит:
  - сущности: `NoteNode`, `ChunkNode`
  - связи: `HAS_CHUNK`, `LINKS_TO` (между заметками), `REFERS_TO` (между чанками)
- Qdrant хранит:
  - эмбеддинги чанков (`obsidian_chunks`)
  - эмбеддинги заметок (`obsidian_notes`)
- `KnowledgeBaseManager` объединяет доступ к графу и векторному индексу
  в единый интерфейс для приложения или агента (MCP-тулов и т.п.).

Обновление и удаление заметок в текущей версии не реализованы и подразумевают
полную переиндексацию vault’а.
