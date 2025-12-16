from smart_library.utils.chunker import TextChunker
from smart_library.config import ChunkerConfig

s = ("Industry 5.0 is to create a more harmonious relationship between humans and technology. "
     "This sentence will be repeated to build a long paragraph. ")
# build a long paragraph ~1700 chars
long_para = s * 20
paragraphs = [long_para]

print('Chunker config:', ChunkerConfig.MIN_CHAR, ChunkerConfig.MAX_CHAR, ChunkerConfig.OVERLAP)
chunker = TextChunker()
non_overlap, overlap = chunker.process_chunks(paragraphs)
print('Non-overlap chunks count:', len(non_overlap))
for i,ch in enumerate(non_overlap):
    print(i, len(ch))
print('Overlap chunks count:', len(overlap))
for i,ch in enumerate(overlap):
    print(i, len(ch))

# Also test with multiple paragraphs
paras = [s * 5, s * 3, s * 8]
print('\nMultiple paragraphs test:')
non_overlap2, overlap2 = chunker.process_chunks(paras)
print('Non-overlap chunks count:', len(non_overlap2))
for i,ch in enumerate(non_overlap2):
    print(i, len(ch))
print('Overlap chunks count:', len(overlap2))
for i,ch in enumerate(overlap2):
    print(i, len(ch))
