import os
import re

root_dir = '/ransomlook'
host = os.getenv('REDIS_HOST', 'ransomlook-redis')
port = os.getenv('REDIS_PORT', '6379')

pattern = r"unix_socket_path=get_socket_path\('cache'\)"
replacement = f"host='{host}', port={port}"

for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                content = f.read()
            
            if 'unix_socket_path' in content:
                new_content = re.sub(pattern, replacement, content)
                # Also handle cases where it's redis.Redis(...)
                new_content = new_content.replace("host='ransomlook-redis', port=6379", replacement)
                
                if new_content != content:
                    with open(file_path, 'w') as f:
                        f.write(new_content)
                    print(f"Patched {file_path}")

print("Global patch for TCP Redis completed.")
