import os

files_to_update = [
    'templates/index.html',
    'templates/loading.html',
    'tailwind.config.js',
]

for file_path in files_to_update:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace occurrences
        content = content.replace('scarlet', 'forest')
        content = content.replace('Scarlet', 'Forest')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
print("Replaced scarlet with forest.")
