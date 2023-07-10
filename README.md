# TError

The terrific Teia toolkit for traceable error treatment and troubleshooting.

This tool tackles the task of taming turmoil in FastAPI with thorough templating ([http-error-schemas techonology](github.com/teialabs/http-error-schemas)) by tapping into tailored exception handlers for typical Python trifles, MongoDB transgressions, and http turmoil.

Pronounced tee-error (gen. pop.) or terror (close friends).

## Usage

```python
from terror.handling import add_exception_handlers 
app = FastAPI()
add_exception_handlers(app)
```
