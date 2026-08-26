# 📝 Doc2MD

Doc2MD is a simple yet powerful Streamlit-based web application that allows you to convert various documents and web pages into clean Markdown format. It leverages **Microsoft's MarkItDown** library for high-quality conversion.

**🌐 Try it online:** [doc2md.streamlit.app](https://doc2md.streamlit.app/)

## ✨ Features

- **Upload Files**: Convert local documents (PDF, Docx, etc.) to Markdown instantly.
- **Paste URLs**: Fetch and convert web content to Markdown by simply pasting a link.
- **Batch Conversion**: Upload a TOML file containing multiple URLs to convert them in bulk and download the results as a structured ZIP file.
- **Easy Download**: Download your converted Markdown files with a single click.

## How to run it on your own machine

Prerequisite: install `uv` if you don't already have it.

```
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

1. Sync the dependencies

   ```
   $ uv sync
   ```

2. Run the app

   ```
   $ uv run streamlit run streamlit_app.py
   ```

## Batch Conversion (TOML)

To use the batch conversion feature, upload a TOML file with the following format:

```toml
[news.tech]
urls = [
    "https://example.com/tech1",
    "https://example.com/tech2"
]

[news.sports]
urls = [
    "https://example.com/sports1"
]
```

### Automatic Directory Creation
The app automatically creates subdirectories based on dots in the category keys. For example, a table named `[news.tech]` will result in a folder structure like `news/tech/` inside the final ZIP file. This helps in keeping your converted files organized.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

This project includes software from the **markitdown** project, which is licensed under the MIT License.

## Acknowledgments

- [Microsoft MarkItDown](https://github.com/microsoft/markitdown) for the powerful conversion engine.
- [Streamlit](https://streamlit.io/) for the amazing web framework.
