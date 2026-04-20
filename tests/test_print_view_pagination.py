from html.parser import HTMLParser


class PrintPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._print_page_depth = 0
        self._print_page_stack = []
        self.page_card_counts = []

    def handle_starttag(self, tag, attrs):
        if tag != "div":
            return

        attrs_dict = dict(attrs)
        classes = set(attrs_dict.get("class", "").split())
        is_print_page = "print-page" in classes
        self._print_page_stack.append(is_print_page)

        if is_print_page:
            self._print_page_depth += 1
            self.page_card_counts.append(0)

        if self._print_page_depth > 0 and "device-card-col" in classes:
            self.page_card_counts[-1] += 1

    def handle_endtag(self, tag):
        if tag != "div" or not self._print_page_stack:
            return

        was_print_page = self._print_page_stack.pop()
        if was_print_page:
            self._print_page_depth -= 1


def _build_test_csv(total_rows):
    header = "Product,Type,MAC,Pairing Code,Description,QR\n"
    rows = [header]
    for i in range(total_rows):
        rows.append(
            f"Product {i},Switch,00:11:22:33:44:{i:02X},{10000000000 + i},Device {i},test-qr-{i}\n"
        )
    return "".join(rows)


def test_print_view_renders_three_pages_for_36_cards(client, matter_data_path):
    path = matter_data_path(_build_test_csv(36))

    response = client.get("/")
    assert response.status_code == 200

    parser = PrintPageParser()
    parser.feed(response.data.decode("utf-8"))

    assert parser.page_card_counts == [16, 16, 4]
