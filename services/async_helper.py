import threading

def run_in_background(task_func, on_success=None, on_error=None):
    """Выполняет task_func в отдельном потоке daemon, чтобы UI не зависал."""
    def worker():
        try:
            result = task_func()
            if on_success:
                on_success(result)
        except Exception as ex:
            if on_error:
                on_error(ex)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()