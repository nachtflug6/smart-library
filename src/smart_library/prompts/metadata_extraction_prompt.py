def get_metadata_extraction_prompt():
    return (
        "Extract the following metadata from the document content:\n"
        "- Title\n"
        "- Authors\n"
        "- Abstract\n"
        "- Keywords\n"
        "Return the result as a JSON object."
    )