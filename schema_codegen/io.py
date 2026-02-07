from collections.abc import Sequence


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def postprocess_generated_files(paths: Sequence[str]) -> None:
    for path in paths:
        source = read_text(path)

        replaced = source.replace("OB11MessageData", "Message")
        replaced = replaced.replace("OB11Message", "")

        if replaced != source:
            write_text(path, replaced)

        print(f"Post-processed replacements for {path}.")
