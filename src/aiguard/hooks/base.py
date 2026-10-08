"""Hook installer interface."""


class HookInstaller:
    name: str = ""
    display_name: str = ""

    def is_installed(self) -> bool:
        raise NotImplementedError

    def install_hook(self) -> None:
        raise NotImplementedError

    def uninstall_hook(self) -> None:
        raise NotImplementedError
