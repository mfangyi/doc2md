import os
import tomllib
from markitdown import MarkItDown
from .patch import apply_patches
from .utils import generate_filename_from_url, clean_filename, generate_unique_filename

# Automatically apply encoding patches on import
apply_patches()

# Reusable MarkItDown instance
_md_instance = None

try:
    import streamlit as st
    @st.cache_resource
    def get_converter():
        """Returns the globally shared MarkItDown instance."""
        return MarkItDown()
except ImportError:
    def get_converter():
        """Returns the globally shared MarkItDown instance."""
        global _md_instance
        if _md_instance is None:
            _md_instance = MarkItDown()
        return _md_instance

def convert_url(url):
    """Converts a URL to Markdown and returns (content, clean_title)."""
    md = get_converter()
    result = md.convert(url)
    title = getattr(result, 'title', None) or generate_filename_from_url(url)
    clean_title = clean_filename(title)
    content = getattr(result, 'text_content', getattr(result, 'markdown', str(result)))
    return content, clean_title

def convert_file(file_path):
    """Converts a local file to Markdown and returns (content, clean_title)."""
    md = get_converter()
    result = md.convert(file_path)
    title = getattr(result, 'title', None) or os.path.splitext(os.path.basename(file_path))[0]
    clean_title = clean_filename(title)
    content = getattr(result, 'text_content', getattr(result, 'markdown', str(result)))
    return content, clean_title

def convert_urls_recursively(data, current_dir, existing_files_map, warning_callback=None, numeric_prefix=False, merge_folders=False):
    """Recursively processes TOML data and converts URLs into subdirectories."""
    if not isinstance(data, dict):
        return

    # 1. Process 'urls' at the current level
    if 'urls' in data and isinstance(data['urls'], list):
        if current_dir not in existing_files_map:
            existing_files_map[current_dir] = set()
        
        urls = data['urls']
        total_urls = len(urls)
        width = len(str(total_urls))
        ordered_contents = []  # accumulate in URL order for optional merge
        
        for i, url in enumerate(urls):
            try:
                content, filename = convert_url(url)
                if numeric_prefix:
                    prefix = f"{i+1:0{width}d}_"
                    base_filename = f"{prefix}{filename}"
                else:
                    base_filename = filename
                unique_filename = generate_unique_filename(current_dir, base_filename, existing_files_map[current_dir])
                file_path = os.path.join(current_dir, f"{unique_filename}.md")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                if merge_folders:
                    ordered_contents.append(content)
            except Exception as e:
                if warning_callback:
                    warning_callback(url, e)
                else:
                    raise e

        # Write merged file immediately after all URLs in this dir are processed,
        # preserving exact URL order (no filename-based sorting).
        if merge_folders and ordered_contents:
            # Create a merged file next to the folder using the folder name (no "_all" suffix).
            folder_name = os.path.basename(current_dir)
            parent_dir = os.path.dirname(current_dir)
            # Prefer <folder_name>.md but avoid clobbering an existing file in the parent dir
            merged_filename = f"{folder_name}.md"
            merged_path = os.path.join(parent_dir, merged_filename)
            # If a file with the same name already exists, append a numeric suffix to make it unique
            if os.path.exists(merged_path):
                base, ext = os.path.splitext(merged_filename)
                counter = 1
                while os.path.exists(os.path.join(parent_dir, f"{base}_{counter}{ext}")):
                    counter += 1
                merged_path = os.path.join(parent_dir, f"{base}_{counter}{ext}")

            with open(merged_path, 'w', encoding='utf-8') as out_f:
                for idx, content in enumerate(ordered_contents):
                    if idx > 0:
                        out_f.write('\n\n---\n\n')
                    out_f.write(content)

    # 2. Recurse into sub-categories
    for key, value in data.items():
        if key == 'urls':
            continue
        if isinstance(value, dict):
            new_dir = os.path.join(current_dir, key)
            os.makedirs(new_dir, exist_ok=True)
            convert_urls_recursively(value, new_dir, existing_files_map, warning_callback, numeric_prefix=numeric_prefix, merge_folders=merge_folders)


def convert_urls_from_toml(toml_file, output_dir, warning_callback=None, numeric_prefix=False, merge_folders=False):
    """Parses a TOML file and converts all URLs specified within it."""
    with open(toml_file, "rb") as f:
        data = tomllib.load(f)
    
    existing_files_map = {}
    convert_urls_recursively(data, output_dir, existing_files_map, warning_callback, numeric_prefix=numeric_prefix, merge_folders=merge_folders)

