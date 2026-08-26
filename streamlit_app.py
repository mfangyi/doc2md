import streamlit as st
import os
import tempfile
import zipfile
from src.converter import convert_file, convert_url, convert_urls_from_toml
from src.extractor import extract_links, format_toml

# Streamlit App Configuration
st.set_page_config(page_title="Doc2MD", page_icon="📝", layout="centered")
st.title("📝 Doc2MD")
st.write("Convert various documents and URLs to Markdown using **Microsoft's MarkItDown** library.")

# Streamlit Tabs
tab1, tab2 = st.tabs(["📄 Upload File", "🌐 Convert URL(s)"])

with tab1:
    st.markdown("### 📄 Upload a Document")
    uploaded_file = st.file_uploader("Choose a file to convert")
    if uploaded_file and st.button("Convert File", type="primary"):
        with st.spinner("Converting..."):
            try:
                suffix = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                content, _ = convert_file(tmp_path)
                os.remove(tmp_path)
                
                st.success("Conversion successful!")
                st.markdown("### Markdown Output:")
                st.text_area("markdown", content, height=400, label_visibility="collapsed")
                st.download_button(
                    label="Download Markdown",
                    data=content.encode("utf-8"),
                    file_name=f"{os.path.splitext(uploaded_file.name)[0]}.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"Error converting file: {e}")

with tab2:
    st.markdown("### 🌐 URL Conversion & Tools")
    st.write("Convert single pages, batch-convert from TOML, or extract page links to generate TOML configurations.")
    
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🔗 Single URL", "📦 Batch Convert (TOML)", "🔍 Extract Links to TOML"])
    
    with sub_tab1:
        st.markdown("#### Paste a Single URL")
        url_input = st.text_input("Enter URL", placeholder="https://example.com/article", label_visibility="collapsed")
        if url_input and st.button("Convert URL", type="primary"):
            with st.spinner("Converting..."):
                try:
                    content, filename = convert_url(url_input)
                    st.success("Conversion successful!")
                    st.markdown("### Markdown Output:")
                    st.text_area("markdown-url", content, height=400, label_visibility="collapsed")
                    st.download_button(
                        label="Download Markdown",
                        data=content.encode("utf-8"),
                        file_name=f"{filename}.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"Error converting URL: {e}")
                    
    with sub_tab2:
        st.markdown("#### Batch Convert from TOML")
        st.write("Upload a TOML file containing lists of URLs organized by categories. You will receive a structured ZIP file.")
        
        st.download_button(
            label="📥 Download TOML Template",
            data="""[news.tech]\nurls = [\n    \"https://example.com/tech-article-1\",\n    \"https://example.com/tech-article-2\"\n]\n\n[news.sports]\nurls = [\n    \"https://example.com/sports-article-1\"\n]\n""".encode("utf-8"),
            file_name="template.toml",
            mime="text/plain"
        )
        
        st.markdown(" ")
        uploaded_toml = st.file_uploader("Upload a TOML file", type="toml")

        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            use_numeric_prefix = st.checkbox(
                "Add numeric prefix to filenames",
                value=False,
                help="Adds a zero-padded index before each filename (e.g. 01_title.md, 02_title.md) to reflect the original URL order in the TOML."
            )
        with col_opt2:
            merge_folders = st.checkbox(
                "Merge folder into single file",
                value=False,
                help="For each category folder, concatenates all its pages in TOML order into a single {folder}.md, saved next to the folder."
            )

        if uploaded_toml and st.button("Convert TOML", type="primary"):
            with st.spinner("Converting URLs..."):
                try:
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        toml_path = os.path.join(tmp_dir, "uploaded.toml")
                        with open(toml_path, "wb") as f:
                            f.write(uploaded_toml.getvalue())

                        output_dir = os.path.join(tmp_dir, "raw")
                        
                        def warning_callback(url, e):
                            st.warning(f"Error for {url}: {e}")
                            
                        convert_urls_from_toml(
                            toml_path,
                            output_dir,
                            warning_callback=warning_callback,
                            numeric_prefix=use_numeric_prefix,
                            merge_folders=merge_folders,
                        )

                        zip_path = os.path.join(tmp_dir, "raw.zip")
                        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                            for root, _, files in os.walk(output_dir):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(file_path, output_dir)
                                    zipf.write(file_path, arcname)

                        with open(zip_path, "rb") as f:
                            st.download_button(
                                label="Download All as ZIP",
                                data=f.read(),
                                file_name="raw.zip",
                                mime="application/zip"
                            )
                except Exception as e:
                    st.error(f"Error during batch conversion: {e}")
                    
    with sub_tab3:
        st.markdown("#### Extract Links from Webpage")
        st.write("Enter a website URL to extract all hyperlinks and export them in TOML format.")
        
        extract_url_input = st.text_input("Website URL", placeholder="e.g., https://www.google.com", label_visibility="collapsed")
        dedup_sort = st.checkbox("Deduplicate and sort", value=True, help="Deduplicate links and sort them alphabetically. If unchecked, preserves duplicates and order of appearance.")
        
        if st.button("Extract Hyperlinks", type="primary"):
            if not extract_url_input:
                st.warning("Please enter a valid URL.")
            else:
                with st.spinner("Fetching and analyzing page content..."):
                    try:
                        title, links = extract_links(extract_url_input, deduplicate_and_sort=dedup_sort)
                        if not links:
                            st.info("No hyperlinks found on this page.")
                        else:
                            st.success(f"Successfully extracted {len(links)} links from '{title}'.")
                            
                            toml_string = format_toml(title, links)
                            
                            st.divider()
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"**Page Title:** {title}")
                                st.write(f"**Total Links:** {len(links)}")
                            with col2:
                                safe_filename = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).strip()
                                if not safe_filename:
                                    safe_filename = "links"
                                st.download_button(
                                    label="📥 Download TOML",
                                    data=toml_string,
                                    file_name=f"{safe_filename}.toml",
                                    mime="text/toml",
                                    use_container_width=True
                                )
                                
                            with st.expander("Preview TOML Content"):
                                st.code(toml_string, language="toml")
                                
                            st.markdown("### Extracted Links")
                            for link in links:
                                st.markdown(f"- {link}")
                    except Exception as e:
                        st.error(f"Error extracting links: {e}")

