from .document import parse_document

def parse_grobid_struct_to_domain(struct, source_path=None, source_url=None, file_hash=None):
    return parse_document(struct, source_path, source_url, file_hash)