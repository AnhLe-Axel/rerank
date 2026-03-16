import unicodedata as ud
import string
import re
import pandas as pd

REPLACE_PHRASE = {'\n': ' ', "‘": "'", "”": '"', "“": '"', "′": "'", "``": "", "''": "", "|": ""}


def normalize(text: str) -> str:
    """Normalize text"""

    text = ud.normalize("NFC", text)
    for phrase in REPLACE_PHRASE:
        text = text.replace(phrase, REPLACE_PHRASE[phrase])
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def ends_with_punctuation(text: str) -> bool:
    punctuation = string.punctuation
    return text.endswith(punctuation)


def concat_chunk(chunk: dict) -> str:
    if isinstance(chunk["content"], str):
        return chunk["content"]

    title = chunk["content"]["title"]
    context = chunk["content"]["context"]

    if title:
        if not ends_with_punctuation(title):
            return title + ". " + context
        else:
            return title + " " + context

    return context


def get_title(chunk: dict) -> str:
    if isinstance(chunk["content"], str):
        return chunk["content"]

    title = chunk["content"]["title"].strip()
    context = chunk["content"]["context"].strip()

    if title:
        return title

    return context


def preprocess_table_content(table_df: pd.DataFrame) -> str:
    table_df.columns = table_df.columns.map(str)
    table_df = table_df.fillna("")
    lines = []
    header = " ".join(table_df.columns)
    separator = "\n"
    lines.extend([header, separator])

    # Create rows
    for _, row in table_df.iterrows():
        row_data = " ".join(row.astype(str))
        lines.append(row_data)

    # Join the Markdown table
    lightweight_content = "\n".join(lines)
    return lightweight_content


def format_table_chunk(chunk_content: str, output_format="light_weight_text"):
    if output_format not in ["light_weight_text", "original"]:
        raise ValueError(f"Invalid format: {format}")

    if output_format == "original":
        return chunk_content

    if output_format == "light_weight_text":
        caption = chunk_content.split('<table')[0]
        try:
            table_text = [preprocess_table_content(table_df)
                          for table_df in pd.read_html(chunk_content)]
        except Exception as e:
            print(f"pd.read_html failed: {e}, falling back to regex HTML strip")
            return re.sub(r'<[^>]+>', ' ', chunk_content)

        if not table_text:
            return chunk_content

        return "\n".join([caption] + table_text)


def common_preprocess(chunk_content: str):
    format_table_chunk_content = format_table_chunk(chunk_content)
    return format_table_chunk_content
