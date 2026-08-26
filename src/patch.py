from markitdown.converters import PlainTextConverter, HtmlConverter
from charset_normalizer import from_bytes

_patches_applied = False

def apply_patches():
    """Applies patches to MarkItDown's default converters to handle encoding issues."""
    global _patches_applied
    if _patches_applied:
        return
    
    # Patch MarkItDown's PlainTextConverter to handle UnicodeDecodeError
    _original_plaintext_convert = PlainTextConverter.convert

    def _patched_plaintext_convert(self, file_stream, stream_info, **kwargs):
        try:
            return _original_plaintext_convert(self, file_stream, stream_info, **kwargs)
        except UnicodeDecodeError:
            file_stream.seek(0)
            try:
                # Fallback to UTF-8
                text_content = file_stream.read().decode('utf-8')
                from markitdown._base_converter import DocumentConverterResult
                return DocumentConverterResult(markdown=text_content)
            except UnicodeDecodeError:
                # Full stream detection
                file_stream.seek(0)
                text_content = str(from_bytes(file_stream.read()).best())
                from markitdown._base_converter import DocumentConverterResult
                return DocumentConverterResult(markdown=text_content)

    PlainTextConverter.convert = _patched_plaintext_convert

    # Patch MarkItDown's HtmlConverter to handle incorrect encoding guesses (e.g. Debian docs)
    _original_html_convert = HtmlConverter.convert

    def _patched_html_convert(self, file_stream, stream_info, **kwargs):
        # If charset was guessed (not from headers) and looks like it could be wrong,
        # or just to be safe for HTML, we re-detect using the full stream.
        # Note: MarkItDown only uses the first 4KB for guessing, which fails for some docs.
        pos = file_stream.tell()
        content = file_stream.read()
        file_stream.seek(pos)
        
        detected = from_bytes(content).best()
        if detected and detected.encoding != stream_info.charset:
            stream_info = stream_info.copy_and_update(charset=detected.encoding)
        
        return _original_html_convert(self, file_stream, stream_info, **kwargs)

    HtmlConverter.convert = _patched_html_convert
    _patches_applied = True
