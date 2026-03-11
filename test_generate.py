import os
from dotenv import load_dotenv
load_dotenv()
try:
    from server import _generate_blog
    print("Function loaded. Testing generation...")
    res = _generate_blog("Why modular kitchens need BWP plywood")
    print("SUCCESS:")
    print(res)
except Exception as e:
    import traceback
    traceback.print_exc()
