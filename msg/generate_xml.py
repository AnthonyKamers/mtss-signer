import sys


def old_method():
    n_lines = int(sys.argv[1]) - 3
    depth = int(sys.argv[2])
    tag_content = sys.argv[3]
    element_lines = n_lines / depth
    child_delimiters = [element_lines]
    for level in range(depth - 1):
        element_lines = element_lines / depth
        child_delimiters.append(element_lines)
    try:
        with open(f"{n_lines + 3}_{tag_content}_{len(tag_content) + 7}.xml", "w", encoding="utf-8") as file:
            file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
            file.write(f"<sett{tag_content}>\n")
            for line in range(n_lines):
                file.write(f"<a>{tag_content}</a>\n")
            file.write(f"</sett{tag_content}>")
    except OSError:
        content_name = tag_content[0:10] + f"_{len(tag_content) + 7}"
        with open(f"{n_lines}_{content_name}.xml", "w", encoding="utf-8") as file:
            file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
            file.write(f"<sett{tag_content}>\n")
            for line in range(n_lines):
                file.write(f"<a>{tag_content}</a>\n")
            file.write(f"</sett{tag_content}>")


def generate_xml(output_file, max_size):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")

        file.write("<root>\n")
        while file.tell() <= max_size:
            file.write("<a>content</a>\n")
        file.write("</root>")


# filename size_bytes
if __name__ == '__main__':
    filename = sys.argv[1]
    size_bytes = int(sys.argv[2])

    generate_xml(filename, size_bytes)
