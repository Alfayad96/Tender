from bs4 import BeautifulSoup


def parse_list_page(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    results = []

    rows = soup.find_all("tr")

    for row in rows:
        cells = row.find_all("td")

        # Eine echte Ausschreibungszeile hat hier 6 Spalten
        if len(cells) != 6:
            continue

        veroeffentlichung = cells[0].get_text(" ", strip=True)
        frist = cells[1].get_text(" ", strip=True)
        titel = cells[2].get_text(" ", strip=True)
        vergabeart = cells[3].get_text(" ", strip=True)
        auftraggeber = cells[4].get_text(" ", strip=True)

        link_tag = cells[5].find("a")
        detail_url = None

        if link_tag and link_tag.has_attr("href"):
            detail_url = link_tag["href"]

        results.append({
            "veroeffentlichung": veroeffentlichung,
            "frist": frist,
            "titel": titel,
            "vergabeart": vergabeart,
            "auftraggeber": auftraggeber,
            "detail_url": detail_url
        })

    return results