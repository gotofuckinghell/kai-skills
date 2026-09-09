# DeepSeek Export Format

## Container

ZIP file named `deepseek_data-YYYY-MM-DD.zip`.

## Structure

```
deepseek_data-YYYY-MM-DD.zip
├── user.json           — account info: {user_id, email, mobile, oauth_profiles}
└── conversations.json  — array of conversation objects
```

## user.json

```json
{
  "user_id": "cb3c332d-...",
  "email": "ism1337@protonmail.com",
  "mobile": null,
  "oauth_profiles": null
}
```

Fields may be null. Email is the most useful field for identification.

## conversations.json

Top-level: array of objects. Each conversation:

```json
{
  "id": "string",
  "title": "Auto-generated Russian or English title",
  "inserted_at": "ISO-8601 timestamp",
  "updated_at": "ISO-8601 timestamp",
  "mapping": {
    "root": {
      "id": "root",
      "parent": null,
      "children": ["1"],
      "message": null
    },
    "1": {
      "id": "1",
      "parent": "root",
      "children": ["2"],
      "message": {
        "model": "deepseek-chat",
        "inserted_at": "ISO-8601",
        "fragments": [
          {
            "type": "REQUEST",
            "content": "user message text"
          }
        ]
      }
    },
    "2": {
      "id": "2",
      "parent": "1",
      "children": [],
      "message": {
        "model": "deepseek-chat",
        "inserted_at": "ISO-8601",
        "fragments": [
          {
            "type": "RESPONSE",
            "content": "assistant response text"
          }
        ]
      }
    }
  }
}
```

## Key observations

- **`mapping` is a flat dict**, not a nested tree. The `parent`/`children` string refs
  form the tree — walk by iterating all keys.
- **`root` node has `message: null`** — skip it when extracting messages.
- **Content is sometimes `{}` (empty object)** instead of a string — always check
  `isinstance(content, str)` before using.
- **Fragment types**: `"REQUEST"` = user message, `"RESPONSE"` = assistant response.
- **Models used**: `deepseek-chat` (standard) and `deepseek-reasoner` (R1 reasoning).
  The model name appears in each message's `model` field.
- **Titles are auto-generated** and may be in Russian or English. They are NOT
  reliable for topic classification — always fall back to first user message content.
- **Timestamps** are in local time with offset (e.g., `+08:00` for Beijing time).
- **Conversations are ordered newest-first** in the array.

## Parsing approach

```python
import zipfile, json

z = zipfile.ZipFile(path)
convs = json.loads(z.read('conversations.json'))
user = json.loads(z.read('user.json'))

for conv in convs:
    mapping = conv['mapping']
    for node_id, node in mapping.items():
        msg = node.get('message')
        if not msg or 'fragments' not in msg:
            continue  # skip root node
        for frag in msg['fragments']:
            content = frag.get('content', '')
            if not isinstance(content, str) or not content.strip():
                continue
            if frag['type'] == 'REQUEST':
                # user message
                pass
            elif frag['type'] == 'RESPONSE':
                # assistant response
                pass
```

## Known quirks

- Some conversations (especially jailbreak/filter-evasion attempts) have titles
  like "User Requests Unethical AI Manipulation Instructions" — these are
  auto-assigned by DeepSeek's moderation system, not the user's original title.
- The export may include conversations where the AI refused to answer (title +
  one refusal message). These still carry useful user-language signal.
- Fragments with `content: {}` appear when the message was an image/video upload
  without text — skip these.