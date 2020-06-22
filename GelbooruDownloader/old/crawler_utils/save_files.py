import os

import aiofiles

CHUNK_SIZE = 64 * 1024

async def save_one(path, file_name, response):
    full_path = os.path.join(path, file_name)

    if not os.path.exists(full_path):
        async with aiofiles.open(full_path, 'wb') as f:
            while True:
                chunk = await response.content.read(CHUNK_SIZE)
                if not chunk:
                    break
                await f.write(chunk)
    else:
        print(f'\n目标目录下已存在同名文件: {file_name}', end='')

