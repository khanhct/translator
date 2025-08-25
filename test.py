# from unstructured.partition.pdf import partition_pdf
#
# raw_pdf_elements = partition_pdf(
#     filename="C:\\Users\\khanh.chu\\Desktop\\workspace\\Translater\\vol3.pdf",
#
#     # Using pdf format to find embedded image blocks
#     extract_image_block_types=["Image"],
#     extract_image_block_to_payload=True,
#     strategy="hi_res",
#
#     # Use layout model (YOLOX) to get bounding boxes (for tables) and find titles
#     # Titles are any sub-section of the document
#     infer_table_structure=True,
#
#     # # Post processing to aggregate text once we have the title
#     # chunking_strategy="by_title",
#     # # Chunking params to aggregate text blocks
#     # # Attempt to create a new chunk 3800 chars
#     # # Attempt to keep chunks > 2000 chars
#     # # Hard max on chunks
#     # max_characters=4000,
#     # new_after_n_chars=3800,
#     # combine_text_under_n_chars=2000,
#     # image_output_dir_path="C:\\Users\\khanh.chu\\Desktop\\workspace\\Translater\\statis",
# )
# # raw_pdf_elements = partition_pdf(filename="C:\\Users\\khanh.chu\\Desktop\\workspace\\Translator\\test1.pdf", strategy="hi_res", infer_table_structure=True)
#
# pages = {}
# for el in raw_pdf_elements:
#     # INSERT_YOUR_CODE
#     # If the element is an image and has base64 data, write it to a file
#     if el.category == "Image" and el.metadata.image_base64 is not None:
#         import base64
#         import os
#
#         output_dir = "C:\\Users\\khanh.chu\\Desktop\\workspace\\Translater\\statis"
#         os.makedirs(output_dir, exist_ok=True)
#         page = el.metadata.page_number
#         image_filename = f"image_page_{page}_{id(el)}.png"
#         image_path = os.path.join(output_dir, image_filename)
#         with open(image_path, "wb") as img_file:
#             img_file.write(base64.b64decode(el.metadata.image_base64))
#         print(f"Image written to {image_path}")
#
#     page_num = el.metadata.page_number
#     if page_num not in pages:
#         pages[page_num] = []
#     pages[page_num].append(el.text)
#
# # Print text page by page
# for page_num, texts in sorted(pages.items()):
#     print(f"\n--- Page {page_num} ---")
#     print("\n".join(filter(None, texts)))
#
# from langchain_openai import OpenAIEmbeddings
# from langchain_experimental.text_splitter import SemanticChunker
#
# # Initialize embeddings (you can use OpenAI or HuggingFace)
# embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
#
# # Create a semantic chunker
# chunker = SemanticChunker(embeddings)
#
# text = """
# WHY THIS BOOK IS IMPORTANT
# Most of the advanced astrological material which is attributed to W.D. Gann
# comes from a personal letter which Gann wrote in 1954 and several of Gann's
# original charts. These documents were released to the general public from the
# late 1970s to the mid 1980s. In recent years there have been books, seminars,
# home study courses and other products all of which say they are based on Gann's
# 1954 soybean letter. The publicly available material dealing with Gann's Circle
# Chart and Active Angles has all been based on this letter and has in fact been
# wrong.
# In this book I will reveal for the first time anywhere that Gann's 1954 soybean
# letter contains a secret, deeper level of astrological knowledge that can not be
# learned by merely reading Gann's letter. The reason I was able to discover the
# hidden knowledge in Gann's soybean letter is simply because I may be the only
# trader who actually uses a soybean horoscope, as Gann did. In addition, I have
# brought into a single book six of Gann's original charts to provide absolute proof
# that the astrological methods in this book are correct and were used by Gann.
# Most copies of Gann's charts have been reduced in size because the originals are
# so large. Some have been reduced from a 24 inch diameter to 4 inches. In this
# book I have done something unprecedented, I have made artistic replicas of
# Gann's original charts so you can see clearly the astrological information they
# contain. Of course, I indicate where to acquire the actual chart if you want to
# study the original. In this book there are 14 artistic replicas of 6 original Gann
# charts. This book also contains more of my exclusive literary analysis of Gann's
# writings. Not only will I use the literary key explained in Volume 1, but I will
# introduce a second literary key. Using both literary keys I will unveil
# astrological knowledge Gann concealed in the following: Truth of The Stock
# Tape, Wall Street Stock Selector, Mechanical Method and Trend Indicator For
# Trading in Wheat, Corn, Rye or Oats, Master Egg Course and Speculation: A
# Profitable Profession. Volume 2 also progresses beyond the literary keys and
# unveils material from Wall Street Stock Selector which Gann concealed without
# """
#
# # Perform semantic chunking
# chunks = chunker.create_documents([text])
#
# for i, chunk in enumerate(chunks, 1):
#     print(f"--- Chunk {i} ---")
#     print(chunk.page_content)
#
from translator import partition_pdf_file

partition_pdf_file("C:\\Users\\khanh.chu\\Desktop\\workspace\\Translater\\Chapter9.pdf", output_path="Chapter9.docx")