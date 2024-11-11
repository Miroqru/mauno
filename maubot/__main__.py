"""Запускает бота.

```
py -m maubot
```
"""

import asyncio

from maubot.bot import main

if __name__ == "__main__":
    asyncio.run(main())
