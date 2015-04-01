"""
Entry point for the whole Pisak program. Declares descriptor for an application
launched on the Pisak start and, if executed directly, launches the application.
"""
from pisak import launcher, logger, inputs

from pisak import app_manager #@UnusedImport


def prepare_main_view(stage, script, data):
    pass


if __name__ == '__main__':
    _std_log = logger.getLogger(__name__)
    _event_log = logger.get_event_logger()
    message = "PISAK was launched."
    _std_log.info(message)
    _event_log.info(message)
    input_process = inputs.run_input_process()
    _main_app = {
        "app": "main_panel",
        "type": "clutter",
        "views": [("main", prepare_main_view)]
    }
    launcher.run(_main_app)
    if input_process:
        input_process.kill()
    message = "PISAK was closed."
    _std_log.info(message)
    _event_log.info(message)
