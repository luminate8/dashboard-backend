with open('app/services/learning_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '"INSERT INTO document_chunks (file_name, content, embedding) VALUES ($1, $2, $3)",\n                        "admin_correction", answer_to_save, embeddings[0]',
    '"INSERT INTO document_chunks (file_name, content, embedding) VALUES ($1, $2, $3::vector)",\n                        "admin_correction", answer_to_save, str(embeddings[0])'
)

print('Fixed' if '::vector' in content else 'NOT FIXED - checking content...')
if '::vector' not in content:
    # Find the relevant line
    for i, line in enumerate(content.split('\n')):
        if 'admin_correction' in line or 'document_chunks' in line:
            print(f"Line {i}: {repr(line)}")

with open('app/services/learning_service.py', 'w', encoding='utf-8') as f:
    f.write(content)
