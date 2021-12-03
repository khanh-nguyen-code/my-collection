import base64

import dill

if __name__ == "__main__":
    b = dill.dumps(lambda x: x + 1)
    print(base64.b64encode(b))
    f = dill.loads(b)
    print(f(3))
